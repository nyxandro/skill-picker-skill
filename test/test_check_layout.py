"""Offline tests of check_layout.py: fake projects and a fake home folder in tmp_path.

The check must never send the agent to delete real or global skills, and must change nothing.
"""

import json
import os

import check_layout
from helpers import error_codes, skill, tree_snapshot, write


def problems(data: dict) -> str:
    return "\n".join(data["skills"]["problems"])


class TestPerSkillLayout:
    def test_correct_layout_has_no_problems(self, project, home):
        skill(project / ".agents/skills", "mastra")
        (project / ".claude/skills").mkdir(parents=True)
        os.symlink("../../.agents/skills/mastra", project / ".claude/skills/mastra")
        write(project / "skills-lock.json", json.dumps({"version": 1, "skills": {"mastra": {"source": "mastra-ai/skills"}}}))

        data = check_layout.collect(project)

        assert data["skills"]["project"] == [{
            "name": "mastra", "source": "mastra-ai/skills", "claude": "link", "agents": True,
            "in_lock": True, "from_package": False,
        }]
        assert data["skills"]["problems"] == []
        assert data["skills"]["blocking"] is False

    def test_every_layout_defect_is_reported(self, project, home):
        skill(project / ".agents/skills", "unlinked")
        skill(project / ".claude/skills", "copied")
        skill(project / ".agents/skills", "copied")
        os.symlink("../../.agents/skills/gone", project / ".claude/skills/broken")
        write(project / "skills-lock.json", json.dumps({"version": 1, "skills": {
            "copied": {"source": "a/b"}, "unlinked": {"source": "a/b"}, "removed": {"source": "a/b"},
        }}))

        text = problems(check_layout.collect(project))

        assert "copied: .claude/skills/copied is a copy" in text
        assert "broken: .claude/skills/broken is a broken link" in text
        assert "unlinked: .agents/skills/unlinked has no link in .claude/skills" in text
        assert "removed: listed in skills-lock.json but its folder is missing" in text

    def test_hand_installed_skill_outside_lock_is_flagged(self, project, home):
        skill(project / ".agents/skills", "manual")
        (project / ".claude/skills").mkdir(parents=True)
        os.symlink("../../.agents/skills/manual", project / ".claude/skills/manual")

        assert "manual: not in skills-lock.json" in problems(check_layout.collect(project))

    def test_agents_skill_linked_outside_the_project_is_flagged(self, project, home):
        skill(home / ".agents/skills", "find-docs")
        (project / ".agents/skills").mkdir(parents=True)
        os.symlink(str(home / ".agents/skills/find-docs"), project / ".agents/skills/find-docs")
        (project / ".claude/skills").mkdir(parents=True)
        os.symlink("../../.agents/skills/find-docs", project / ".claude/skills/find-docs")

        assert "outside the project" in problems(check_layout.collect(project))

    def test_claude_link_to_another_folder_is_flagged(self, project, home):
        skill(project / ".agents/skills", "vitest")
        skill(project / "vendor/skills", "vitest")
        (project / ".claude/skills").mkdir(parents=True)
        os.symlink("../../vendor/skills/vitest", project / ".claude/skills/vitest")

        assert "not to .agents/skills/vitest" in problems(check_layout.collect(project))

    def test_link_to_a_folder_without_skill_md_is_not_called_broken(self, project, home):
        (project / ".agents/skills/empty").mkdir(parents=True)
        (project / ".claude/skills").mkdir(parents=True)
        os.symlink("../../.agents/skills/empty", project / ".claude/skills/empty")

        text = problems(check_layout.collect(project))

        assert "broken link" not in text
        assert "no SKILL.md" in text

    def test_plain_files_in_skill_folders_are_not_skills(self, project, home):
        write(project / ".agents/skills/README.md", "notes")

        assert check_layout.collect(project)["skills"]["project"] == []

    def test_invalid_lock_is_reported_and_folders_are_still_listed(self, project, home):
        skill(project / ".agents/skills", "vitest")
        write(project / "skills-lock.json", "{not json")

        data = check_layout.collect(project)

        assert error_codes(data) == {"skills-lock.json": "SKILLS_LOCK_INVALID"}
        assert [s["name"] for s in data["skills"]["project"]] == ["vitest"]


def python_package_skill(project, name="fastapi", installed=True):
    """The layout library-skills creates: both folders link straight into the virtualenv."""
    target = f"../../.venv/lib/python3.12/site-packages/{name}/.agents/skills/{name}"
    if installed:
        skill(project / f".venv/lib/python3.12/site-packages/{name}/.agents/skills", name)
    for folder in (".agents/skills", ".claude/skills"):
        (project / folder).mkdir(parents=True, exist_ok=True)
        os.symlink(target, project / folder / name)


def pnpm_package_skill(project, installed=True):
    """A hand link through the stable node_modules/<pkg> path, which pnpm points into .pnpm."""
    if installed:
        skill(project / "node_modules/.pnpm/@tanstack+router-core@1.171.39/node_modules/@tanstack/router-core/skills", "router-core")
        (project / "node_modules/@tanstack").mkdir(parents=True)
        os.symlink("../.pnpm/@tanstack+router-core@1.171.39/node_modules/@tanstack/router-core",
                   project / "node_modules/@tanstack/router-core")
    (project / ".agents/skills").mkdir(parents=True)
    os.symlink("../../node_modules/@tanstack/router-core/skills/router-core", project / ".agents/skills/router-core")
    (project / ".claude/skills").mkdir(parents=True)
    os.symlink("../../.agents/skills/router-core", project / ".claude/skills/router-core")


class TestPackageSkills:
    def test_library_skills_layout_is_valid_without_a_lock_entry(self, project, home):
        python_package_skill(project)

        data = check_layout.collect(project)

        assert data["skills"]["project"][0]["from_package"] is True
        assert data["skills"]["problems"] == []

    def test_pnpm_package_skill_linked_by_hand_is_valid(self, project, home):
        pnpm_package_skill(project)

        data = check_layout.collect(project)

        assert data["skills"]["project"][0]["from_package"] is True
        assert data["skills"]["problems"] == []

    def test_package_skill_before_dependencies_are_installed_says_so(self, project, home):
        python_package_skill(project, installed=False)

        text = problems(check_layout.collect(project))

        assert "fastapi: links into an installed package" in text
        assert "dependencies" in text
        assert "broken link" not in text
        assert "skills-lock.json" not in text

    def test_pnpm_package_skill_before_install_says_so(self, project, home):
        pnpm_package_skill(project, installed=False)

        text = problems(check_layout.collect(project))

        assert "router-core: links into an installed package" in text
        assert "broken link" not in text

    def test_package_skill_seen_only_by_claude_is_flagged(self, project, home):
        skill(project / ".venv/lib/python3.12/site-packages/fastapi/.agents/skills", "fastapi")
        (project / ".claude/skills").mkdir(parents=True)
        os.symlink("../../.venv/lib/python3.12/site-packages/fastapi/.agents/skills/fastapi", project / ".claude/skills/fastapi")

        assert "fastapi: no link in .agents/skills" in problems(check_layout.collect(project))

    def test_markdown_marks_package_skills(self, project, home, capsys):
        python_package_skill(project)

        check_layout.main([str(project)])

        assert "| fastapi | installed package |" in capsys.readouterr().out


class TestBrokenAgentsLink:
    def test_broken_link_in_agents_folder_is_reported(self, project, home):
        (project / ".agents/skills").mkdir(parents=True)
        os.symlink("../../vendor/gone", project / ".agents/skills/gone")
        (project / ".claude/skills").mkdir(parents=True)
        os.symlink("../../.agents/skills/gone", project / ".claude/skills/gone")

        assert "gone: .agents/skills/gone is a broken link" in problems(check_layout.collect(project))


class TestFolderLevelLinks:
    def test_whole_skills_folder_linked_inside_the_project_is_not_a_copy(self, project, home):
        skill(project / ".agents/skills", "mastra")
        (project / ".claude").mkdir()
        os.symlink("../.agents/skills", project / ".claude/skills")

        data = check_layout.collect(project)

        assert data["skills"]["project"][0]["claude"] == "shared"
        assert "copy" not in problems(data)
        assert data["skills"]["blocking"] is False

    def test_skills_folder_linked_to_the_global_one_blocks_everything(self, project, home):
        skill(home / ".claude/skills", "find-docs")
        (project / ".claude").mkdir()
        os.symlink(str(home / ".claude/skills"), project / ".claude/skills")

        data = check_layout.collect(project)

        assert data["skills"]["blocking"] is True
        assert data["skills"]["project"] == []
        assert "SKILLS_DIR_OUTSIDE_PROJECT" in problems(data)

    def test_dot_claude_itself_linked_outside_blocks_everything(self, project, home):
        (home / ".claude").mkdir()
        os.symlink(str(home / ".claude"), project / ".claude")

        data = check_layout.collect(project)

        assert data["skills"]["blocking"] is True
        assert "SKILLS_DIR_OUTSIDE_PROJECT" in problems(data)

    def test_project_root_equal_to_home_blocks_everything(self, home):
        skill(home / ".agents/skills", "find-docs")

        data = check_layout.collect(home)

        assert data["skills"]["blocking"] is True
        assert "SKILLS_ROOT_IS_HOME" in problems(data)


class TestGlobalSkills:
    def test_global_skills_are_listed_from_both_folders_and_account_sync(self, project, home):
        skill(home / ".agents/skills", "find-docs")
        (home / ".claude/skills").mkdir(parents=True)
        os.symlink("../../.agents/skills/find-docs", home / ".claude/skills/find-docs")
        skill(home / ".claude/skills/synced/org-1", "docx")
        skill(home / ".claude/skills/.trash/123", "old")

        assert check_layout.collect(project)["global_skills"] == ["docx", "find-docs"]

    def test_broken_global_links_are_reported_not_listed(self, project, home):
        (home / ".claude/skills").mkdir(parents=True)
        os.symlink("../../.agents/skills/gone", home / ".claude/skills/gone")

        data = check_layout.collect(project)

        assert data["global_skills"] == []
        assert any("gone" in p and "broken link" in p for p in data["global_problems"])

    def test_no_global_folders_is_not_an_error(self, project, home):
        data = check_layout.collect(project)

        assert data["global_skills"] == [] and data["global_problems"] == []


class TestSafetyAndCli:
    def test_check_changes_nothing_in_the_project_or_home(self, project, home):
        skill(project / ".agents/skills", "a")
        skill(project / ".claude/skills", "a")
        skill(home / ".agents/skills", "g")
        before = tree_snapshot(project, home)

        check_layout.collect(project)

        assert tree_snapshot(project, home) == before

    def test_json_output_is_machine_readable(self, project, home, capsys):
        skill(project / ".agents/skills", "vitest")

        assert check_layout.main([str(project), "--json"]) == 0

        assert json.loads(capsys.readouterr().out)["skills"]["project"][0]["name"] == "vitest"

    def test_markdown_report_shows_stop_first(self, project, home, capsys):
        (home / ".claude/skills").mkdir(parents=True)
        (project / ".claude").mkdir()
        os.symlink(str(home / ".claude/skills"), project / ".claude/skills")

        assert check_layout.main([str(project)]) == 0

        out = capsys.readouterr().out
        assert out.index("STOP") < out.index("## Global skills")

    def test_markdown_report_lists_skills_and_problems(self, project, home, capsys):
        skill(project / ".agents/skills", "vitest")

        check_layout.main([str(project)])

        out = capsys.readouterr().out
        assert "## Project skills" in out and "| vitest |" in out
        assert "has no link in .claude/skills" in out

    def test_missing_project_root_fails_with_a_clear_error(self, tmp_path, home, capsys):
        assert check_layout.main([str(tmp_path / "nope")]) == 2
        assert "PROJECT_ROOT_NOT_FOUND" in capsys.readouterr().err
