#!/usr/bin/env python3
"""Record that a human read an agent-drafted artefact — as a receipt, not a claim.

MING Labs' Comprehension Obligation says an agent's owner must be able to redo
the agent's work, within a bounded time, on a cadence, or the agent loses a
level. It is the best idea of its kind we have seen, and like every governance
idea it is worth exactly as much as its evidence. A footer that says "a human
read this" is the assertion. This is the receipt.

What it records: which artefact (by content hash, so the text cannot change
afterwards without breaking the record), who read it, when they started, when
they finished, and a signature over all of it.

What it will not do: invent a duration. If the start and end are not supplied,
it fails. An attestation whose numbers were generated rather than observed is
worse than none, because it converts an honest silence into a false record — the
`enforcement` mistake this specification exists to stop, committed by the tool
that reports on it.

Verification needs nothing from us. The signing key is an SSH key whose public
half GitHub already publishes:

    curl -s https://github.com/<user>.keys > allowed_keys.tmp
    # prefix each line with:  <principal> namespaces="org-as-code-attestation" <key>
    ssh-keygen -Y verify -f allowed_signers -I <principal> \\
        -n org-as-code-attestation -s <artefact>.sig < <artefact>

Usage:
    python3 tools/attest.py LETTER.md \\
        --reader "Andreas Siemes <post@andreassiemes.de>" \\
        --started 2026-08-26T09:14:00+02:00 \\
        --finished 2026-08-26T09:41:00+02:00 \\
        --key ~/.ssh/id_ed25519 \\
        --out slices/ming-labs/attestation.json
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import subprocess
import sys
from pathlib import Path

NAMESPACE = "org-as-code-attestation"


def _parse_ts(value: str, label: str) -> datetime.datetime:
    try:
        ts = datetime.datetime.fromisoformat(value)
    except ValueError:
        raise SystemExit(f"{label}: not an ISO-8601 timestamp: {value!r}")
    if ts.tzinfo is None:
        raise SystemExit(
            f"{label}: needs an offset (e.g. +02:00). A reading time without a "
            f"zone is not a fact anyone else can place.")
    return ts


def sign(payload: bytes, key: Path) -> str | None:
    """Sign with ssh-keygen -Y. Returns None when no key was given."""
    if key is None:
        return None
    if not key.exists():
        raise SystemExit(f"signing key not found: {key}")
    proc = subprocess.run(
        ["ssh-keygen", "-Y", "sign", "-f", str(key), "-n", NAMESPACE, "-q", "-"],
        input=payload, capture_output=True)
    if proc.returncode != 0:
        raise SystemExit(f"ssh-keygen failed: {proc.stderr.decode().strip()}")
    return proc.stdout.decode()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("artefact", type=Path)
    ap.add_argument("--reader", required=True,
                    help="who did the reading — the principal in the signature")
    ap.add_argument("--started", required=True)
    ap.add_argument("--finished", required=True)
    ap.add_argument("--key", type=Path, default=None,
                    help="SSH private key. Omitted: an unsigned draft receipt")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--note", default=None,
                    help="anything the reader changed or challenged during the read")
    a = ap.parse_args(argv)

    if not a.artefact.exists():
        raise SystemExit(f"no such artefact: {a.artefact}")
    started, finished = _parse_ts(a.started, "--started"), _parse_ts(a.finished, "--finished")
    if finished <= started:
        raise SystemExit("--finished is not after --started")
    minutes = round((finished - started).total_seconds() / 60, 1)

    body = a.artefact.read_bytes()
    digest = hashlib.sha256(body).hexdigest()

    record = {
        "artefact": a.artefact.name,
        "sha256": digest,
        "bytes": len(body),
        "reader": a.reader,
        "started": started.isoformat(timespec="seconds"),
        "finished": finished.isoformat(timespec="seconds"),
        "minutes": minutes,
        "namespace": NAMESPACE,
        "drafted_by": "an agent; the reader did not write it",
        "note": a.note,
        "what_this_is": (
            "A receipt for a human read of an agent-drafted text, in the spirit of "
            "MING Labs' Comprehension Obligation. The hash binds the receipt to one "
            "exact version: change a character and this record stops matching. The "
            "duration was observed, not generated — the tool refuses to run without "
            "both timestamps."
        ),
        "verify": (
            f"sha256 the artefact and compare; then `ssh-keygen -Y verify -n "
            f"{NAMESPACE}` against the signer's public key, which GitHub publishes "
            f"at https://github.com/<user>.keys"
        ),
    }
    canonical = json.dumps(record, sort_keys=True, separators=(",", ":")).encode()
    signature = sign(canonical, a.key)
    record["signed_payload_sha256"] = hashlib.sha256(canonical).hexdigest()
    record["signature"] = signature
    if signature is None:
        record["unsigned"] = (
            "No key was supplied, so this is a draft receipt: it states the facts "
            "but proves nothing. Do not publish it in this state."
        )

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n",
                     encoding="utf-8")
    print(f"attestation: {a.out}")
    print(f"  {a.artefact.name} · sha256 {digest[:12]}… · {minutes} min"
          f" · {'signed' if signature else 'UNSIGNED'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
