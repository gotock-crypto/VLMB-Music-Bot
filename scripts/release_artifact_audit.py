#!/usr/bin/env python3
"""Validate release-tree purity and deterministic release metadata."""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_NAMES = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
FORBIDDEN_SUFFIXES = {".pyc", ".pyo"}


def check(ok: bool, label: str, detail: str = "") -> None:
    print(f"{'PASS' if ok else 'FAIL'}  {label}{' — ' + detail if detail else ''}")
    if not ok:
        raise SystemExit(1)


def validate_tree(root: Path) -> list[str]:
    bad: list[str] = []
    for path in root.rglob("*"):
        if path.is_dir() and path.name in FORBIDDEN_NAMES:
            bad.append(str(path.relative_to(root)))
        elif path.is_file() and (path.suffix.lower() in FORBIDDEN_SUFFIXES or path.name == ".coverage"):
            bad.append(str(path.relative_to(root)))
    return sorted(bad)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=ROOT)
    parser.add_argument("--artifact", type=Path, help="archive/file to hash after tree validation")
    args = parser.parse_args()
    root = args.root.resolve()

    check(root.is_dir(), "release tree exists", str(root))
    bad = validate_tree(root)
    check(not bad, "generated-file exclusion", ", ".join(bad) if bad else "clean")

    version_file = root / "RELEASE_VERSION"
    check(version_file.is_file(), "RELEASE_VERSION exists")
    version = version_file.read_text(encoding="utf-8").strip()
    check(bool(version), "release version is non-empty")
    check(" " not in version and "\n" not in version, "release version is single-line", version)

    manifest = root / "RELEASE_MANIFEST.md"
    check(manifest.is_file(), "RELEASE_MANIFEST.md exists")

    if args.artifact:
        artifact = args.artifact.resolve()
        check(artifact.is_file(), "artifact exists", str(artifact))
        print(f"INFO  artifact sha256 — {sha256_file(artifact)}")

    print("\nRelease artifact audit OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
