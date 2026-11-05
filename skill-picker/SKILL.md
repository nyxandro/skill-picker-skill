---
name: skill-picker
description: >
  Pick, install and audit project-level agent skills for the current project: inventory the
  stack by layers, rate how likely the agent is to write outdated code for each technology, find
  official or otherwise strong skills, vet them by reading their files, install the approved
  ones into .agents/skills with links in .claude/skills, and report a coverage table (✅ covered,
  ⚪ left to docs lookup, ❌ not covered). Always use it when the owner asks which skills a
  project needs or what they cover: "pick skills for this project", "what skills should we
  install here", "are there skills for our stack", "what is covered by skills and what isn't",
  "install skills into the project", "is there a skill for X here", "check the project's
  skills", or as an audit without web search when work starts in a new or unfamiliar project.
  Not for the owner's global skill set or for writing a new skill. The owner may phrase this in
  another language; match on meaning.
metadata:
  version: "1.0.0"
---

# Skill picker

The agent's knowledge of libraries lags behind their releases, and every project has its own
stack, so the useful set of skills differs from project to project. The owner keeps the global
set fixed and small and wants the project-level set chosen by a method, not by habit. The
owner's words: "so I don't have to explain this order of steps a second time: check the
technologies, frameworks, techniques, languages, some narrow cases; even the deploy method
should count", and "the global ones I manage myself, the set is always the same".

This skill is that method: inventory the project, sort it into layers, rate the risk of outdated
code per technology, find and vet skills, install only what the owner approves, and show
coverage in one table.

## Scope and limits

- **Project level only.** The layout is the owner's everywhere: the real folder in
  `<project>/.agents/skills/<name>`, a link to it in `<project>/.claude/skills/<name>`, and the
  install recorded in `<project>/skills-lock.json`. Claude Code reads `.claude/skills`; Codex,
  OpenCode and other agents read `.agents/skills`; one copy serves all of them. The one
  exception is a skill shipped inside an installed package: both folders hold relative links
  into `node_modules` or the virtualenv, with no lock entry, so the skill always matches the
  installed version of its library (step 7).
- **Global folders are read only.** `~/.agents/skills` and `~/.claude/skills` are listed to know
  what is already covered. Never install, remove or repair anything there; report a problem
  you see and leave it to the owner.
- **Nothing is installed without the owner's go-ahead on a named list.** A skill runs with the
  agent's full permissions, adds instructions to every session, and some send data out on
  their own. The owner decides.
- **Do not commit or push.** Say which files are new and recommend committing them.

The wording sets the depth:

- **Audit** ("what's covered", "check the project's skills"): step 1 with the layout check,
  steps 2 and 3, and the coverage table. Also check that every installed project skill still
  matches a technology in the project; a skill for something the project no longer uses is
  proposed for removal.
  No search, no installs, no repairs without the owner's go-ahead.
- **Pick** ("pick skills for the project"): the full pass through step 6, then stop and ask.
- **Install** ("install X and Y"): vet X and Y (step 5) if not vetted yet in this conversation.
  If vetting turns up anything from the step 5 list (data sent out on its own, a skill meant for
  the library's contributors, a version gap, a conflict with the project's rules), stop and ask
  before installing. Otherwise install them and show the updated table.

If the layout check in step 1 opens with **STOP** (a skill folder resolves outside the project,
or the project root is the home folder), change nothing in any skill folder in any mode: a "repair"
there would delete the owner's global skills. Report it and leave it to the owner.

## Step 1. Inventory the project

Collect facts, not impressions, and change nothing: no installs, no updates, no lockfile edits.

**Manifests.** First list the project's files without installed packages, virtualenvs and
build output; run everything from the project root. In a git repository, take the tracked files plus new ones not added yet; ignored
files stay out, so build output listed in `.gitignore` does not slip in:

```bash
git ls-files --cached --others --exclude-standard | grep -vE '^\.(agents|claude)/' > <temp-folder>/files.txt
```

A project without git (a new one often has none yet) gets the same list from `find`, pruning
installed code, virtualenv internals and build folders:

```bash
find . \( -name node_modules -o -name .git -o -name .venv -o -name venv -o -name site-packages \
  -o -name dist-packages -o -name dist -o -name build -o -name target -o -name vendor \
  -o -name .agents -o -name .claude -o -name .next -o -name .turbo \) -prune -o -type f -print \
  | sed 's|^\./||' > <temp-folder>/files.txt
```

`find` does not know `.gitignore`: drop paths that are plainly generated (a framework's build
output such as `.mastra/output/`). Then pick the manifests from the list:

```bash
grep -E '(^|/)(package\.json|pyproject\.toml|requirements[^/]*\.txt|requirements/[^/]+\.txt|go\.mod|Cargo\.toml|composer\.json|Gemfile|setup\.py|setup\.cfg|Pipfile|pom\.xml|build\.gradle(\.kts)?|[^/]+\.csproj|pubspec\.yaml|deno\.jsonc?)$' <temp-folder>/files.txt
```

Read every manifest found. A file with a manifest's name can be binary or broken: name the ones
you could not read, because the technologies behind them are unknown, not absent. Internal
workspace packages (`workspace:` and `link:` versions, path dependencies) are not technologies.

**A project with no manifests yet.** When the skills are picked before the code exists, the stack
comes from what is planned: the spec, the plan, the README, the owner's own words. If nothing is
written down, ask the owner which language, frameworks, database and deploy method are planned
before going further. There are no installed versions then: rate the risk against the current
release from the registry, the one a fresh install would get today, and say so in the table.

**Installed versions.** A manifest holds ranges (`^19.0.0`, `>=3.22`); what matters is the
version actually installed. Ask the package manager, read only:

- pnpm: `pnpm list -r --depth 0 --json` (every workspace at once); npm: `npm ls --depth=0`;
- Python: `uv pip list` or `pip list` inside the project's environment;
- Go: `go.mod` already names exact versions;
- Rust, PHP, Ruby: read `Cargo.lock`, `composer.lock`, `Gemfile.lock`.

When dependencies are not installed, read the lockfile (`pnpm-lock.yaml`, `package-lock.json`,
`yarn.lock`, `uv.lock`, `poetry.lock` and so on). With neither, the version is unknown: say so
and never guess it. Do not run anything that installs or updates (`install`, `update`, `add`,
`cargo tree`, `go mod tidy`).

**Deploy and CI.** Find the files, then read them: base images, compose services and their
images, each workflow's steps and the third-party actions it uses, hosting configs.

```bash
grep -iE '(^|/)(dockerfile[^/]*|[^/]*compose[^/]*\.ya?ml)$|^\.(github|gitea|forgejo)/workflows/|\.gitlab-ci\.yml|vercel\.json|netlify\.toml|wrangler\.|fly\.toml|\.tf$' <temp-folder>/files.txt
```

**Skills already present.** Run the bundled check from anywhere, with the project root as the
argument (standard-library Python; it reads files and changes nothing):

```bash
python3 <this-skill>/scripts/check_layout.py <project-root>        # add --json for JSON
```

It lists the project's skills with how each one is installed and every layout problem (a copy
instead of a link, a broken link, a skill Claude Code cannot see, a lock entry without a folder,
a folder without a lock entry), and the owner's global skill names with any problems in the
global folders. Skills linked from installed packages show the source "installed package";
when the dependencies are not installed yet it says so, which is expected and needs no repair.
It opens with **STOP** when a skill folder resolves outside the project or the project root is
the home folder.

**Agent instructions and docs.** `AGENTS.md`, `CLAUDE.md`, `.claude/CLAUDE.md`,
`CLAUDE.local.md`, `.cursor/rules/`, `.windsurf/rules/`, `.github/copilot-instructions.md`,
`.github/instructions/`, and the docs folders. Open only what answers these:

- **Agent instructions** (`AGENTS.md`, `CLAUDE.md`): project rules outrank any skill's advice,
  for example a design system that fixes chart colors, or a test-first rule that makes the test
  runner part of every task.
- **Operations or deploy docs**: how the project actually ships. When there are no CI files,
  the deploy layer comes from here (ssh plus rsync plus compose on a server, a platform, a
  pipeline).
- **Spec or plan**: external APIs and protocols (Telegram Bot API, MTProto, payments), what the
  agents do, what is planned next.

When the role of a dependency is unclear, grep for its imports; do not read the whole codebase.

## Step 2. Sort the stack into layers

Read `references/layers.md`: the layers, the signals that reveal each one, and what kind of skill
usually serves it. Place every technology that matters in one layer. Framework-neutral layers
count even where no single library stands out: an agent project needs a skill for its agent
framework and a framework-neutral skill on agent design; a project deployed by GitHub Actions
wants a GitHub Actions skill whatever the app is written in. Leave out type packages, tiny
utilities and anything the project does not lean on.

## Step 3. Rate the risk of outdated code

For each technology, how likely is the agent to write code that no longer matches the installed
version, and how much does a mistake cost?

- **High**: a protocol or library under about a year old, or before 1.0 with breaking minor
  releases; an API that ships monthly; a niche library the model has seen little of; or an area
  where a mistake hits data, money or security.
- **Medium**: a major version released in the last twelve months or after the model's knowledge
  cutoff; build and test tooling on a fresh major.
- **Low**: stable for years, or used only in a small finished corner of the project.

Use evidence, not memory: the installed version from step 1, release dates from the
registry (`npm view <pkg> time --json`, `npm view <pkg> dist-tags`,
`https://pypi.org/pypi/<name>/json`), the library's changelog. Write each risk as a consequence:
"I would call methods that no longer exist", not a bare "high".

## Step 4. Find candidates

In this order, stopping as soon as a technology is settled:

1. **Already covered**: the global names from the layout check, the project's own skills, and the
   skills built into the agent (for example `claude-api` in Claude Code). These need no install.
2. **Skills inside installed packages.** The best source there is: written by the library's
   authors for exactly the installed version, and updated with it. A growing number of
   libraries ship them (FastAPI and TanStack Router among them). Look in the installed
   dependencies, from the project root:

   ```bash
   find -L node_modules -maxdepth 6 -path node_modules/.pnpm -prune -o -name SKILL.md -print
   find .venv/lib/*/site-packages -maxdepth 5 -name SKILL.md
   ```

   Packages put them in `.agents/skills/<name>/` (the convention `library-skills` reads) or in
   their own folder such as `skills/<name>/`. A SKILL.md inside another skill's folder is a part
   of that skill, not a separate one. Count only the project's own dependencies, not
   dependencies of dependencies. With nothing installed yet, this source is empty: say so.
3. **The catalog**, `references/catalog.md`: the short list of skills in use or named by the owner,
   with install commands and caveats, and dead ends already checked.
4. **The library's own repository.** Official skills often live there, in `skills/`,
   `.claude/skills/` or `.agents/skills/`:
   `gh api "repos/<org>/<repo>/git/trees/HEAD?recursive=1" --jq '.tree[].path' | grep SKILL.md`.
5. **The public catalog**: `DO_NOT_TRACK=1 npx skills find "<technology>"`. The query itself
   goes to the skills.sh search, so it names the project's technologies to an outside service;
   `DO_NOT_TRACK=1` keeps the CLI from also logging it as a statistics event. Install counts are
   not a quality signal: unrelated skills with a hundred thousand installs top many queries.
6. **List a repository's skills without installing**: `npx skills add <owner/repo> -l`, with
   `--full-depth` when the repository root has its own SKILL.md. Listing sends nothing.

Also check whether the package ships its own documentation (Mastra puts it in
`node_modules/@mastra/*/dist/docs`): a skill that points there beats a static summary. When
nothing worth installing exists, the technology is covered by the global docs lookup
(`find-docs`) and gets ⚪ in the table, with the reason.

## Step 5. Vet every candidate before recommending it

Read every skill you are going to recommend in full, scripts included; a catalog card is not a
reading. For a candidate you reject, stop reading once the reason is clear and name it: reading
fourteen skills end to end to reject nine of them doubles the cost of a pick.

Read without installing. `skills add` installs, so never run it just to look. Use
`gh api "repos/<owner>/<repo>/contents/<path>" --jq .content | base64 -d` for single files, or
`git clone --depth 1 https://github.com/<owner>/<repo> <temp-folder>` into a temporary folder
outside the project, and delete that folder when done. Check:

- **Author.** The library's own organisation first, then a core maintainer (Anthony Fu for Vite
  and Vitest), then a known organisation, then a single community author. A skill shipped inside
  the installed package is the library's own by definition, and it is read in place, in
  `node_modules` or the virtualenv.
- **Package skills change with every upgrade.** Upgrading the library silently replaces the
  instructions the agent follows. Tell the owner, and propose a line in `AGENTS.md`: when such a
  library is upgraded, read what changed in its skill before relying on it, as for any new skill.
- **Audience.** It must be for users of the library. Skills in a library's repository are often
  for its contributors: the Recharts `guide` skill writes their docs site; the skills in Google's
  A2UI repository triage their issues.
- **Freshness and version.** The last commit, and the version the skill was written for against
  the installed one. Skills generated from docs can run ahead: the Vitest skill was built from a
  5.1 beta while the project ran 5.0.5. That is fine when the newer features are labeled; tell
  the owner what to avoid until the project upgrades.
- **Mechanism.** A skill that checks the installed package or the live docs keeps working; a
  static dump of API facts ages from the day it was written.
- **Anything that sends data out on its own.** The Mastra skill tells the agent to post bug
  reports to mastra.ai without asking; the CopilotKit skill's verify command adds a telemetry
  flag. Name every such behavior to the owner and propose a line in `AGENTS.md` that forbids it
  without permission. For scripts, look for network and process calls, then read every hit:
  `grep -rnE 'fetch\(|https?://|curl|wget|requests\.|urllib|httpx|axios|subprocess|child_process|exec(Sync)?\(|spawn\(|os\.system' <skill-folder>`.
- **Conflicts with project rules.** A generic styling skill against the project's brand book: the
  project wins, and a skill that mostly conflicts is not worth installing.
- **Cost.** Every skill's description sits in every session; its body loads whenever it fires.
  A stable, low-risk library does not earn a skill.
- **Moves and removals.** Skills get renamed and moved (`yusukebe/hono-skill` moved to
  `honojs/skills`; CopilotKit replaced `a2ui-renderer` with `copilotkit`). Trust the
  repository's current tree, not a catalog page.

skills.sh rates every skill (Gen, Socket, Snyk). With `DO_NOT_TRACK=1` the CLI does not fetch
those ratings and prints no risk panel, and without it the panel appears only during the
install, after the decision. So look the ratings up while vetting, on the repository's page
(`https://skills.sh/<owner>/<repo>`), before you ask the owner. A warning usually means network
calls, telemetry or a deliberately unsafe example file; confirm by reading and say what it was.

## Step 6. Report and ask

Show the coverage table (format below) with the current state, then each candidate: what it
gives, what it costs now, what it locks in later, and a clear recommendation with the reason.
Ask which to install. In pick mode, stop here.

## Step 7. Install the approved list

Before the first command, note the CLI version (`npx skills --version`) and take a snapshot of
the global folders, to prove afterwards that nothing outside the project changed:

```bash
ls -la ~/.agents/skills ~/.claude/skills > <temp-folder>/global-before.txt
```

Then, from the project root, one command per repository:

```bash
mkdir -p .claude
DO_NOT_TRACK=1 npx skills add <owner/repo> --skill <name> -a claude-code codex -y
```

- Always `npx skills`, not a `skills` found on the PATH: a global install can be an older
  version with different behavior. The notes below were observed on 1.5.10 and checked in the
  1.7.0 source; on another version, check that the result still looks as described.
- Create `.claude/` first. Version 1.5.10 silently skipped Claude Code when the folder was
  missing: it installed for Codex only and no link appeared. The `mkdir` costs nothing on
  versions that create it themselves.
- Keep `-a claude-code codex`. With a universal agent in the list, the CLI puts the real folder
  in `.agents/skills/` and links `.claude/skills/` to it. With `-a claude-code` alone it copies
  the folder into `.claude/skills/` and breaks the layout.
- `DO_NOT_TRACK=1` turns off the CLI's own statistics, which it otherwise sends to
  `add-skill.vercel.sh` on `add`, `find` and `remove` (the source repository, skill names,
  agents, search queries; no project files). Mention it to the owner either way.
- Run the layout check again: each new skill must show `.agents/skills` yes, `.claude/skills` link,
  in `skills-lock.json` yes, and the report must list no layout problems. Compare the global
  folders with the snapshot.
- Run bundled scripts once on the real project, and note when they only work from the project
  root (the mtcute tools do).
- To remove a skill: `DO_NOT_TRACK=1 npx skills remove <name> -y`, then check
  `skills-lock.json`; version 1.5.10 left the entry behind. Remove a stale entry by hand.
- Before deleting anything by hand, run `readlink -f` on the path and on `.claude/skills` and
  `.agents/skills`: every one must stay inside the project. A layout-check row with
  `.claude/skills` = `shared` means the whole folder is a link to `.agents/skills`; that is not
  a copy, and deleting "the copy" would delete the skill itself.
- To repair a real copy that should be a link: delete the copy in `.claude/skills/` after the
  check above, then install again with the agent pair.
- The current session may need a restart before new skills appear; Claude Code usually picks
  them up on the fly. Say which you observed.

### Skills from installed packages

These are linked, not copied, so they stay in step with the library. `skills add` is not used
for them, and they get no lock entry.

- **The package keeps them in `.agents/skills/`** (FastAPI does): use `library-skills` by the
  FastAPI author. It makes the relative links in both folders, repairs its own links after an
  upgrade, removes them when the package goes, never touches other skills, and sends nothing
  out (checked in version 0.0.19). From the project root:

  ```bash
  uvx library-skills scan                                         # read only: what the packages ship
  uvx library-skills install --skill <name> --claude --yes        # Python; npx library-skills for JS
  uvx library-skills --check                                      # exit 1 if a link drifted or broke
  ```

  Checked on a Python project with FastAPI 0.162.0. The JavaScript form is documented but was not
  tried: after it, look at where the links point.
- **The package keeps them elsewhere** (TanStack Router ships `skills/router-core/`, which
  `library-skills` does not see): link the entry folder by hand, relative, through the stable
  top-level package path:

  ```bash
  ln -s ../../node_modules/@tanstack/router-core/skills/router-core .agents/skills/router-core
  ln -s ../../.agents/skills/router-core .claude/skills/router-core
  ```

  Never link through `node_modules/.pnpm/<package>@<version>/…`: that path changes with every
  upgrade. A Python link goes through `.venv/lib/python3.X/`, so a Python upgrade breaks it; run
  `library-skills install` again, or redo the hand link.
- The links are broken until the project's dependencies are installed: on a fresh clone, a
  server or CI there is no skill until `pnpm install` or `uv sync`. The layout check reports that
  plainly; it is not a problem to repair. The links are relative, so recommend committing them
  like any other skill files.

## The coverage table

Write it in the owner's language. Columns:

| Layer | Technology (version) | Where in the project | Risk of outdated code | Covered by |
|---|---|---|---|---|

- **✅ `skill`**: covered; say how in a few words (checks the installed version, the live docs,
  a set of rules).
- **✅ `skill`, partially**: say what is not covered and where the agent checks instead.
- **⚪ no skill, deliberately**: the reason, and what protects instead (`find-docs`, the type
  check, the project's rules).
- **❌ not covered**: the candidate, waiting for the owner.

Group rows by layer, highest risk first inside a layer, and bold the technology in high-risk
rows. Take installed versions from step 1. Merge stable low-risk libraries into one ⚪ row at the
bottom. After the table, two short blocks:

- **Weak spots**: every high-risk row that is not fully ✅, one line each, with what the agent
  will do instead.
- **Not done**: uncommitted files, flagged outward-facing behaviors without an `AGENTS.md` line,
  candidates waiting for the owner, manifests you could not read.

Example from a real project (TypeScript monorepo: Telegram bot, Mini App, agents on Mastra),
in the owner's language:

| Слой | Технология (версия) | Где в проекте | Риск устаревшего кода | Чем закрыто |
|---|---|---|---|---|
| Агентный слой | **Mastra 1.78** | агенты | высокий: API меняется от версии к версии | ✅ `mastra`: сверяется с документацией внутри установленного пакета |
| Агентный слой | **A2UI 0.10 + `@copilotkit/a2ui-renderer` 1.79** | дашборды мини-аппа | высокий: протоколу меньше года | ✅ `copilotkit`, частично: ведёт к свежей документации CopilotKit, сам протокол сверять по исходникам `@a2ui/web_core` |
| Агентный слой | Устройство агентов | агенты | — | ✅ `developing-ai-agents` |
| Внешние API | **Bot API / grammY 1.46** | бот | высокий: Bot API выходит каждый месяц | ✅ `telegram-bot-development`: живая документация плюс проверка установленной библиотеки |
| Внешние API | **mtcute 0.32** | чтение каналов | высокий: редкая библиотека до 1.0 | ✅ `using-mtcute`: скрипты читают установленную версию |
| Тесты | Vitest 5.0 | все тесты | средний: свежая крупная версия | ✅ `vitest`: собран по бете 5.1, помеченное «(5.1)» не использовать |
| Фронтенд | React 19.3 | мини-апп | низкий | ✅ `vercel-react-best-practices`: правила производительности |
| Сборка | Vite 8 | мини-апп | средний | ⚪ без скилла: настройки сборки почти не меняются; `find-docs` |
| Фронтенд | Recharts 3 | 3 файла графиков | низкий | ⚪ без скилла: официального нет, правила задаёт брендбук |
| Разное | Hono 4, Zod 3, Drizzle 0.45, TypeScript 6, Biome 2.5 | сервер, база, инструменты | низкий/средний | ⚪ `find-docs` по запросу |

## Before you report, check yourself

- The global folders match the snapshot taken before step 7.
- Every installed skill has the real folder, the link and the lock entry (a package skill: the
  two links into the installed package), and the layout check shows no layout problems.
- Every recommended skill was read in full, scripts included, not judged by its card.
- Every high-risk row is ✅, ✅ partially with a stated fallback, or ❌ with a named candidate.
  None is missing.
- Every outward-facing behavior is named to the owner.
- A skill the owner approved and you installed and read in full, or a new dead end, is offered
  to the owner as an addition to `references/catalog.md`, with the date it was checked. Skills
  merely seen in a search, rejected, or judged optional do not go into the catalog.
