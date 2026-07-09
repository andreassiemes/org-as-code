"""Load an OPI document set (a file or a repo directory) into one in-memory model.

The repository stays the source of truth: the loader is a stateless projection of
the working tree. `Model.stale()` supports `--watch` (mtime-based reload).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

SKIP_DIRS = {".git", ".venv", "node_modules", "dist", "__pycache__", "templates"}
ENTITY_LISTS = ("units", "gremien", "decisions", "agents", "flows", "knowledge")


class LoadError(RuntimeError):
    pass


class Model:
    """Merged view over every OPI YAML document below a root."""

    def __init__(self, root: Path, docs: dict[Path, dict], mtimes: dict[Path, float]):
        self.root = root
        self.docs = docs
        self._mtimes = mtimes
        self.org: dict = {}
        self.entities: dict[str, list[dict]] = {k: [] for k in ENTITY_LISTS}
        for path, doc in sorted(docs.items()):
            if not isinstance(doc, dict):
                continue
            if isinstance(doc.get("org"), dict) and not self.org:
                self.org = doc["org"]
            # single `unit:` documents count as one more unit
            if isinstance(doc.get("unit"), dict):
                self.entities["units"].append(doc["unit"])
            for key in ENTITY_LISTS:
                val = doc.get(key)
                if isinstance(val, list):
                    self.entities[key].extend(e for e in val if isinstance(e, dict))

    # -- watch support -------------------------------------------------------
    def stale(self) -> bool:
        for path, old in self._mtimes.items():
            try:
                if path.stat().st_mtime != old:
                    return True
            except FileNotFoundError:
                return True
        # new files appearing also count
        return set(_yaml_files(self.root)) != set(self._mtimes)

    # -- convenience ---------------------------------------------------------
    def by_id(self, kind: str, eid: str) -> dict | None:
        for e in self.entities.get(kind, []):
            if str(e.get("id")) == str(eid):
                return e
        return None

    def counts(self) -> dict[str, int]:
        return {k: len(v) for k, v in self.entities.items() if v}


def _yaml_files(root: Path) -> list[Path]:
    if root.is_file():
        return [root]
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in filenames:
            if fn.endswith((".yaml", ".yml")) and "invalid" not in fn:
                out.append(Path(dirpath) / fn)
    return sorted(out)


def load(root: str | Path) -> Model:
    if yaml is None:
        raise LoadError(
            "PyYAML is required to parse OPI documents (pip install pyyaml). "
            "There is deliberately no fallback parser — a server that guesses "
            "at YAML would defeat its purpose."
        )
    rootp = Path(root).resolve()
    if not rootp.exists():
        raise LoadError(f"no such file or directory: {rootp}")
    files = _yaml_files(rootp)
    if not files:
        raise LoadError(f"no .yaml documents found under {rootp}")
    docs, mtimes, errors = {}, {}, []
    for f in files:
        try:
            docs[f] = yaml.safe_load(f.read_text(encoding="utf-8"))
            mtimes[f] = f.stat().st_mtime
        except yaml.YAMLError as exc:
            errors.append(f"{f}: {exc}")
    if errors:
        raise LoadError("failed to parse:\n  " + "\n  ".join(errors))
    model = Model(rootp, docs, mtimes)
    if not any(model.entities.values()):
        raise LoadError(f"no OPI entities (units/gremien/decisions/...) found under {rootp}")
    return model
