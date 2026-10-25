"""Builders for small fake projects used by the tests."""

from pathlib import Path


def write(path: Path, text: str = "") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def skill(folder: Path, name: str) -> Path:
    write(folder / name / "SKILL.md", f"---\nname: {name}\ndescription: test\n---\n")
    return folder / name


def error_codes(data: dict) -> dict[str, str]:
    """Map each reported file to its error code."""
    return {e["path"]: e["code"] for e in data["errors"]}


def tree_snapshot(*roots: Path) -> list[tuple]:
    """Every path under the roots with its link target or content, to prove nothing changed."""
    entries = []
    for root in roots:
        for path in sorted(root.rglob("*")):
            if path.is_symlink():
                entries.append((str(path), "link", str(path.readlink())))
            elif path.is_file():
                entries.append((str(path), "file", path.read_bytes()))
            else:
                entries.append((str(path), "dir", None))
    return entries
