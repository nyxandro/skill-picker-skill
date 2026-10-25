#!/usr/bin/env python3
"""Check the project's skills layout and list the owner's global skills (read only).

The owner's layout: the real folder in .agents/skills/<name>, a link to it in
.claude/skills/<name>, the install recorded in skills-lock.json. A skill shipped inside an
installed package is linked instead (both folders point into node_modules or the virtualenv) and
has no lock entry. Anything that would make a "repair" touch files outside the project blocks
the report instead of being diagnosed.

Usage: python3 check_layout.py [PROJECT_ROOT] [--json]

Standard library only. It reads files and never changes anything.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

SKILL_DIRS = (".agents", ".agents/skills", ".claude", ".claude/skills")
PACKAGE_DIRS = {"node_modules", "site-packages", "dist-packages"}


def has_skill_md(path: Path) -> bool:
    return (path / "SKILL.md").is_file()


def is_broken_link(path: Path) -> bool:
    return path.is_symlink() and not path.exists()


def links_into_package(path: Path) -> bool:
    """A link that leads into installed dependencies, whether or not they are installed now."""
    return path.is_symlink() and bool(PACKAGE_DIRS & set(path.resolve().parts))


def is_inside(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


def skill_entries(folder: Path) -> list[str]:
    """Folders and links in a skills folder; plain files are not skills."""
    if not folder.is_dir():
        return []
    return sorted(
        p.name for p in folder.iterdir()
        if not p.name.startswith(".") and (p.is_dir() or p.is_symlink())
    )


def read_lock(root: Path, errors: list[dict]) -> dict:
    path = root / "skills-lock.json"
    if not path.is_file():
        return {}
    try:
        skills = json.loads(path.read_text(encoding="utf-8-sig")).get("skills", {})
        if not isinstance(skills, dict):
            raise ValueError("'skills' is not an object")
        return skills
    except (OSError, ValueError, AttributeError) as error:
        errors.append({"code": "SKILLS_LOCK_INVALID", "path": "skills-lock.json", "reason": str(error)})
        return {}


def blocked(problems: list[str]) -> dict:
    return {"project": [], "problems": problems, "blocking": True}


def project_skills(root: Path, errors: list[dict]) -> dict:
    root_real = root.resolve()
    if root_real == Path.home().resolve():
        return blocked([
            "SKILLS_ROOT_IS_HOME: the project root is the home folder, so its skill folders are the "
            "owner's global ones. Do not install, remove or repair anything from here."
        ])
    outside = [
        f"SKILLS_DIR_OUTSIDE_PROJECT: {rel} resolves to {(root / rel).resolve()}, outside the project. "
        "Do not install, remove or repair anything until the owner fixes this link."
        for rel in SKILL_DIRS
        if ((root / rel).exists() or (root / rel).is_symlink()) and not is_inside((root / rel).resolve(), root_real)
    ]
    if outside:
        return blocked(outside)

    agents_dir, claude_dir = root / ".agents" / "skills", root / ".claude" / "skills"
    lock = read_lock(root, errors)
    entries, problems = [], []
    for name in sorted(set(skill_entries(agents_dir)) | set(skill_entries(claude_dir)) | set(lock)):
        agents_path, claude_path = agents_dir / name, claude_dir / name
        agents = agents_path.is_dir()
        if claude_path.is_symlink():
            claude = "link" if claude_path.exists() else "broken"
        elif claude_path.is_dir():
            # The whole .claude/skills folder may be a link to .agents/skills: same files, no copy.
            claude = "shared" if agents and claude_path.resolve() == agents_path.resolve() else "copy"
        else:
            claude = None
        in_lock = name in lock
        entry = lock.get(name)
        from_package = links_into_package(agents_path) or links_into_package(claude_path)
        entries.append({
            "name": name, "source": entry.get("source") if isinstance(entry, dict) else None,
            "claude": claude, "agents": agents, "in_lock": in_lock, "from_package": from_package,
        })
        problems += package_problems(name, agents_path, claude_path) if from_package else lock_problems(
            name, agents_path, claude_path, claude, agents, in_lock, root_real)
    return {"project": entries, "problems": problems, "blocking": False}


def package_problems(name: str, agents_path: Path, claude_path: Path) -> list[str]:
    """A skill linked from an installed package: no lock entry by design, and its links are
    expected to be broken until the project's dependencies are installed."""
    problems = []
    if is_broken_link(agents_path) or is_broken_link(claude_path):
        problems.append(f"{name}: links into an installed package that is not installed right now. Install the "
                        "project's dependencies (for example `uv sync` or `pnpm install`); nothing to repair")
    elif agents_path.is_dir() and not has_skill_md(agents_path):
        problems.append(f"{name}: the package folder it links to has no SKILL.md")
    if not agents_path.is_symlink() and not agents_path.exists():
        problems.append(f"{name}: no link in .agents/skills, so Codex and other agents do not see it")
    if not claude_path.is_symlink() and not claude_path.exists():
        problems.append(f"{name}: .agents/skills/{name} has no link in .claude/skills, so Claude Code does not see it")
    if agents_path.is_symlink() and claude_path.is_symlink() and agents_path.resolve() != claude_path.resolve():
        problems.append(f"{name}: .claude/skills/{name} and .agents/skills/{name} lead to different folders")
    return problems


def lock_problems(name, agents_path, claude_path, claude, agents, in_lock, root_real) -> list[str]:
    """A skill installed with the skills CLI: real folder in .agents/skills, link, lock entry."""
    problems = []
    if is_broken_link(agents_path):
        problems.append(f"{name}: .agents/skills/{name} is a broken link (-> {os.readlink(agents_path)})")
    if agents_path.is_symlink() and not is_inside(agents_path.resolve(), root_real):
        problems.append(f"{name}: .agents/skills/{name} links to {agents_path.resolve()}, outside the project; "
                        "editing or removing it changes files outside the project")
    if agents and not has_skill_md(agents_path):
        problems.append(f"{name}: .agents/skills/{name} has no SKILL.md")
    if claude == "copy":
        problems.append(f"{name}: .claude/skills/{name} is a copy, not a link to .agents/skills/{name}")
    if claude == "broken" and not is_broken_link(agents_path):
        problems.append(f"{name}: .claude/skills/{name} is a broken link (-> {os.readlink(claude_path)})")
    if claude == "link" and claude_path.resolve() != agents_path.resolve():
        problems.append(f"{name}: .claude/skills/{name} links to {os.readlink(claude_path)}, not to .agents/skills/{name}")
    if agents and claude is None:
        problems.append(f"{name}: .agents/skills/{name} has no link in .claude/skills, so Claude Code does not see it")
    if in_lock and not agents and claude not in ("link", "copy"):
        problems.append(f"{name}: listed in skills-lock.json but its folder is missing")
    if not in_lock and (agents or claude in ("link", "copy")):
        problems.append(f"{name}: not in skills-lock.json (installed by hand; `skills update` does not track it)")
    return problems


def global_skills() -> tuple[list[str], list[str]]:
    """The owner's global set, for coverage only: never changed here. Returns names and problems."""
    home = Path.home()
    names, problems = set(), []
    for folder in (home / ".agents" / "skills", home / ".claude" / "skills"):
        try:
            entries = skill_entries(folder)
        except OSError as error:
            problems.append(f"{folder}: cannot list ({error.strerror or error})")
            continue
        for name in entries:
            path = folder / name
            if name == "synced":
                continue
            if path.is_symlink() and not path.exists():
                problems.append(f"{folder}/{name}: broken link (-> {os.readlink(path)})")
            elif has_skill_md(path):
                names.add(name)
    synced = home / ".claude" / "skills" / "synced"
    if synced.is_dir():
        for org in synced.iterdir():
            if org.is_dir() and not org.name.startswith("."):
                names.update(p.name for p in org.iterdir() if has_skill_md(p))
    return sorted(names), problems


def collect(root: Path) -> dict:
    root = root.resolve()
    errors: list[dict] = []
    skills = project_skills(root, errors)
    global_names, global_problems = global_skills()
    return {
        "root": str(root),
        "errors": errors,
        "skills": skills,
        "global_skills": global_names,
        "global_problems": global_problems,
    }


def render_markdown(data: dict) -> str:
    skills = data["skills"]
    out = [f"# Skills layout: {data['root']}", ""]
    if skills["blocking"]:
        out += ["## STOP: skill folders point outside the project", ""]
        out += [f"- {p}" for p in skills["problems"]] + [""]
    for e in data["errors"]:
        out += [f"- {e['code']}: {e['path']}: {e['reason']}", ""]

    out += ["## Project skills", ""]
    if skills["project"]:
        out += ["| Skill | Source | .agents/skills | .claude/skills | In skills-lock.json |", "|---|---|---|---|---|"]
        for s in skills["project"]:
            source = s["source"] or ("installed package" if s["from_package"] else "—")
            out.append(f"| {s['name']} | {source} | {'yes' if s['agents'] else 'no'} | {s['claude'] or 'none'} | {'yes' if s['in_lock'] else 'no'} |")
    elif not skills["blocking"]:
        out.append("No project-level skills.")
    if skills["problems"] and not skills["blocking"]:
        out += ["", "Layout problems:"] + [f"- {p}" for p in skills["problems"]]

    out += ["", "## Global skills (the owner's set, read only)", ""]
    out.append(", ".join(data["global_skills"]) or "none")
    if data["global_problems"]:
        out += ["", "Problems in the global folders (report to the owner, do not fix):"]
        out += [f"- {p}" for p in data["global_problems"]]
    return "\n".join(out) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("root", nargs="?", default=".", help="project root (default: current folder)")
    parser.add_argument("--json", action="store_true", help="print JSON instead of a Markdown report")
    args = parser.parse_args(argv)

    root = Path(args.root)
    if not root.is_dir():
        print(f"PROJECT_ROOT_NOT_FOUND: {root} is not a folder. Pass the project root as the argument.", file=sys.stderr)
        return 2
    data = collect(root)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="backslashreplace")  # folder names that are not valid UTF-8
    print(json.dumps(data, indent=2, ensure_ascii=False) if args.json else render_markdown(data), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
