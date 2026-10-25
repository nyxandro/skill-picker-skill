# Skill Picker Skill

[![Download Skill Picker Skill](https://img.shields.io/badge/Download-skill--picker.skill-blue?style=for-the-badge)](https://github.com/nyxandro/skill-picker-skill/raw/main/dist/skill-picker.skill)

A skill picker for Claude Code, Codex and OpenCode: pick, install and audit the project-level
agent skills for the current project. The agent inventories the stack by layers, rates for each
technology how likely it is to write outdated code, finds official or otherwise strong skills,
reads every candidate in full before recommending it, installs only what the owner approves,
and reports one coverage table.

The model's knowledge of libraries lags behind their releases, and every project has its own
stack, so the useful set of skills differs from project to project. Picked by habit, the set
ends up with a skill for a stable library nobody needed, none for the protocol that ships every
month, and one that quietly posts bug reports to a vendor. This skill turns the choice into a
method with evidence behind every row: installed versions, release dates, the skill's own files.

## What the agent does

1. **Inventories the project** and changes nothing: manifests, installed versions from the
   package manager or the lockfile (never guessed), deploy and CI files, agent instructions and
   docs, and the skills already present, through the bundled layout check.
2. **Sorts the stack into layers**: languages, the agent and LLM layer, external APIs,
   frontend, backend, data, testing, build, deploy and CI, observability, security, process.
   Framework-neutral layers count too: an agent project wants a skill on agent design, not only
   one for its framework.
3. **Rates the risk of outdated code** per technology from the registry and the changelog, and
   writes it as a consequence: "I would call methods that no longer exist", not a bare "high".
4. **Finds candidates** in order: what is already covered (global and built-in skills), skills
   shipped inside the installed packages, a short catalog of vetted skills, the library's own
   repository, the public skills.sh catalog.
5. **Vets every candidate by reading it**, scripts included: the author, the audience (users of
   the library or its contributors), the version it was written for, whether it checks live
   docs or is a static dump, anything that sends data out on its own, conflicts with the
   project's rules, its cost in every session.
6. **Reports and stops.** The coverage table, then each candidate with what it gives, what it
   costs and a recommendation. Nothing is installed without the owner's go-ahead on a named list.
7. **Installs the approved list** in one layout for every agent: the real folder in
   `.agents/skills/`, a link in `.claude/skills/`, the entry in `skills-lock.json`. A skill
   shipped inside a package is linked into `node_modules` or the virtualenv instead, so it
   always matches the installed library. Then it runs the layout check again and proves that
   nothing outside the project changed.

The wording sets the depth: "what's covered" is an audit with no search and no installs, "pick
skills" stops before installing, "install X and Y" vets and installs those two.

Hard limits: project level only; the global skill folders are read, never changed; no commits
or pushes; and when a skill folder resolves outside the project, the agent stops and touches
nothing, because a "repair" there would delete global skills.

## The report

One table, in the owner's language: layer, technology with its installed version, where it is
used, the risk of outdated code, and what covers it. ✅ a skill covers it, ✅ partially with the
gap named, ⚪ no skill on purpose with the reason and what protects instead, ❌ not covered with
the candidate waiting for the owner. After it: the weak spots, one line per high-risk row that
is not fully covered, and what was not done.

## Install

**Claude Code, as a plugin.** The plugin comes from [nyxandro/skills](https://github.com/nyxandro/skills),
the catalog of my skills. Run in a Claude Code session:

```text
/plugin install skill-picker --marketplace nyxandro/skills
```

This adds the catalog and installs the plugin from it, on Claude Code 2.1.275 or later. On an
older version, add the catalog first:

```text
/plugin marketplace add nyxandro/skills
/plugin install skill-picker@nyxandro
```

No version is pinned, so every commit to this repository is a new version. To take it, run
`claude plugin marketplace update nyxandro` and then `claude plugin update skill-picker@nyxandro`
in your shell, or turn on auto-update for the catalog under `/plugin` → Marketplaces.

**Any agent, as a skill folder.** Download `dist/skill-picker.skill` (the badge above) and
unpack it into the skills folder of your agent, or clone this repository and link the
`skill-picker/` folder there. No build step. Install it one way or the other, not both: with
both, Claude Code loads the skill twice.

The layout check needs Python 3 and nothing beyond its standard library. Searching and installing
use Node.js (`npx skills`) and the GitHub CLI (`gh`). The search step sends the names of the
project's technologies to skills.sh; every `npx skills` command runs with `DO_NOT_TRACK=1`, so the
CLI's own statistics stay off.

## Tests

```bash
uv run --with pytest python -m pytest test
```

Offline: fake projects and a fake home folder in a temporary directory. The tests check every
layout defect the script reports, the stop cases, and that the script changes nothing. pytest is
needed only for the tests, not by the skill.

## Repository layout

```text
skill-picker/                the skill itself
  SKILL.md                   the method: inventory, layers, risk, search, vetting, install, the table
  references/layers.md       the layers, the signals that reveal each one, the kind of skill that serves it
  references/catalog.md      vetted skills in use, with install commands and caveats; dead ends
  scripts/check_layout.py    read-only check of the project's skill layout
test/                        offline tests of the layout check
dist/skill-picker.skill      downloadable archive of the skill folder
```

## License

MIT.
