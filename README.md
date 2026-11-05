<div align="center">

# Skill Picker

**A Claude Code skill that picks, vets and installs the agent skills your project's stack actually needs, and shows what's covered.**

[![Release](https://img.shields.io/github/v/release/nyxandro/skill-picker-skill)](https://github.com/nyxandro/skill-picker-skill/releases)
[![License](https://img.shields.io/github/license/nyxandro/skill-picker-skill)](LICENSE)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-SKILL.md-6f42c1)](https://agentskills.io/specification)
[![Claude Code plugin](https://img.shields.io/badge/Claude%20Code-plugin-d97757)](#install)

**English** · [Русский](README.ru.md)

</div>

Skill Picker is a skill for Claude Code, Codex, OpenCode, Cursor and other agents that read Agent
Skills. It picks, installs and audits project-level skills for the current project. The agent
sorts the stack into layers, rates for each technology how likely it is to write outdated code,
finds official or otherwise strong skills, reads every candidate in full before recommending it,
installs only what you approve and reports one coverage table.

## Why

A model's knowledge of libraries lags behind their releases, and every project has its own stack,
so the useful set of skills differs from project to project. Picked by habit, the set goes wrong.

- There's a skill for a stable library nobody needed.
- There's none for the protocol that ships a new version every month.
- One of them quietly posts bug reports to a vendor.

This skill turns the choice into a method with evidence behind every row. Installed versions,
release dates and the skill's own files.

## Install

| Agent | Command |
|---|---|
| Claude Code, as a plugin | `/plugin install skill-picker --marketplace nyxandro/skills` |
| Claude Code, Codex, OpenCode, Cursor and others | `npx skills add nyxandro/skill-picker-skill` |
| Any agent, by hand | Download the [latest `.skill` archive](https://github.com/nyxandro/skill-picker-skill/releases/latest/download/skill-picker.skill) and unpack it into the agent's skills folder |

Pick one. If you install it two ways, Claude Code loads the skill twice.

<details>
<summary>Requirements and more install options</summary>

<br>

- The layout check needs Python 3 and only its standard library. Searching and installing use
  Node.js (`npx skills`) and the GitHub CLI (`gh`).
- The search step sends the names of your project's technologies to skills.sh. Every
  `npx skills` command runs with `DO_NOT_TRACK=1`, so the CLI's own statistics stay off.
- The one-line plugin install needs Claude Code 2.1.275 or later. On an older version, add the
  catalog first with `/plugin marketplace add nyxandro/skills` and then run
  `/plugin install skill-picker@nyxandro`.
- The catalog pins no version, so every commit here reaches plugin users as an update. Run
  `claude plugin marketplace update nyxandro` and `claude plugin update skill-picker@nyxandro`, or
  turn on auto-update under `/plugin` → Marketplaces.
- With `npx skills`, add `-g` to install the skill for every project. To install a given version,
  add its tag, as in `nyxandro/skill-picker-skill@v1.0.0`.
- You can also clone this repository and link the `skill-picker/` folder into your agent's skills
  folder. There is no build step.

</details>

## Usage

The wording sets how far the agent goes.

| You ask | The agent |
|---|---|
| *What's covered by skills here and what isn't?* | Audits what is installed, with no search and no installs |
| *Pick skills for this project.* | Finds and vets candidates, then stops before installing |
| *Install X and Y.* | Vets those two and installs them |

## How it works

1. **Inventory.** It reads the manifests, the installed versions from the package manager or the
   lockfile (never guessed), the deploy and CI files, the agent instructions and docs, and the
   skills already present. It changes nothing.
2. **Layers.** Languages, the agent and LLM layer, external APIs, frontend, backend, data,
   testing, build, deploy and CI, observability, security and process. Framework-neutral layers
   count too. An agent project wants a skill on agent design, not only one for its framework.
3. **Risk.** For each technology it reads the registry and the changelog and writes the risk as a
   consequence, such as "I would call methods that no longer exist", not a bare "high".
4. **Search.** What's already covered by global and built-in skills, skills shipped inside the
   installed packages, a short catalog of vetted skills, the library's own repository, and the
   public skills.sh catalog.
5. **Vetting.** It reads every candidate, scripts included. Who wrote it and for whom, which
   version it was written for, whether it checks live docs or is a static dump, anything that sends
   data out on its own, conflicts with your project's rules, and its cost in every session.
6. **Report and stop.** The coverage table, then each candidate with what it gives, what it costs
   and a recommendation. Nothing is installed without your go-ahead on a named list.
7. **Install.** The real folder goes into `.agents/skills/`, a link into `.claude/skills/` and an
   entry into `skills-lock.json`. A skill shipped inside a package is linked from `node_modules` or
   the virtualenv instead, so it always matches the installed library. Then it checks the layout
   again and proves nothing outside the project changed.

It works at project level only. Global skill folders are read, never changed. It makes no commits
or pushes, and if a skill folder resolves outside the project, it stops and touches nothing.

## Example

A coverage table for a made-up project.

| Layer | Technology | Risk of outdated code | Covered by |
|---|---|---|---|
| Agent and LLM | Anthropic SDK | High, I'd use parameters renamed in recent releases | ✅ `claude-api` |
| External APIs | Telegram Bot API | High, a new version every month | ✅ `telegram-bot-development` |
| Frontend | React | Medium | ⚪ No skill on purpose, docs are looked up per task |
| Data | Prisma | High, the migration commands changed | ❌ A candidate is waiting for your decision |

After the table come the weak spots, one line per high-risk row that isn't fully covered, and what
was not done.

## Versions

The current version sits in `metadata.version` of `skill-picker/SKILL.md`, so any installed copy
tells you which one it is. Every version has a git tag and a
[release](https://github.com/nyxandro/skill-picker-skill/releases) with its own archive.
[CHANGELOG.md](CHANGELOG.md) lists what changed.

<details>
<summary>Tests</summary>

<br>

```bash
uv run --with pytest python -m pytest test
```

The tests run offline on fake projects and a fake home folder in a temporary directory. They
check every layout defect the script reports, the stop cases, and that the script changes
nothing. pytest is needed only for the tests, not by the skill.

</details>

<details>
<summary>Repository layout</summary>

<br>

```text
skill-picker/                the skill
  SKILL.md                   the method, from inventory to the coverage table
  references/layers.md       the layers, the signals that reveal each one, the skill that serves it
  references/catalog.md      vetted skills in use, with install commands, caveats and dead ends
  scripts/check_layout.py    a read-only check of the project's skill layout
test/                        offline tests of the layout check
dist/skill-picker.skill      the skill folder as a downloadable archive
CHANGELOG.md                 what changed in each version
README.md, README.ru.md      this page in English and in Russian
```

</details>

## License

[MIT](LICENSE)
