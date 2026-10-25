# Catalog of skills

A short list, not a directory of everything that exists. An entry gets in only when it was read
in full and is used in a real project, or when the owner named it as wanted. Anything else is
found through the search in SKILL.md step 4 and vetted in step 5; add it here only after it
earns its place the same way.

Repositories move and skills get renamed. Before installing, list the repository's current
skills with `DO_NOT_TRACK=1 npx skills add <owner/repo> -l` and read what you install. Install commands follow
SKILL.md step 7 (`mkdir -p .claude`, `DO_NOT_TRACK=1`).

## Skills in use

| Layer | Skill | Install | What it gives | Caveats | Checked |
|---|---|---|---|---|---|
| Agent and LLM | `developing-ai-agents` | `DO_NOT_TRACK=1 npx skills add ilkruglov/developing-ai-agents-skill --skill developing-ai-agents -a claude-code codex -y` | Framework-neutral agent engineering: context, tools, memory, evals, multi-agent work; based on Bojie Li's book, in Russian | Text only; review and diagnosis stay read-only until asked | read and used, 2026-10-24 |
| Agent and LLM | `mastra` | `DO_NOT_TRACK=1 npx skills add mastra-ai/skills --skill mastra -a claude-code codex -y` | Mastra by the Mastra team: reads the docs inside the installed `@mastra/*` packages, a model registry script, common errors, migrations | **Sends data out**: tells the agent to post bug reports to `mastra.ai/api/feedback` without asking; propose an `AGENTS.md` line against it. `mastra-factory` in the same repo is for their hosted Factory only | read and used, 2026-10-24 |
| Agent and LLM | `copilotkit` | `DO_NOT_TRACK=1 npx skills add CopilotKit/CopilotKit --skill copilotkit -a claude-code codex -y` | Official entry point for CopilotKit: where the current docs (`docs.copilotkit.ai/<path>.md`) and sources live; v1 vs v2 imports | Almost no API detail by design; does not cover the A2UI protocol itself. Its `verify` command checks the CopilotKit runtime and adds a telemetry flag: skip it when the project has no runtime | read and used, 2026-10-24 |
| External APIs | `telegram-bot-development` | `DO_NOT_TRACK=1 npx skills add nyxandro/telegram-bot-development-skill --skill telegram-bot-development -a claude-code codex -y` | The owner's skill: checks the live Bot API docs and what the installed library supports (grammY, Telegraf, aiogram, python-telegram-bot and others); UX, webhooks, limits, Stars payments, Mini Apps | Mini Apps at the concept level, not the `@tma.js` SDK. The library check finds nothing until the project's dependencies are installed. Its `evals/` folder ships with every install; the deliberately vulnerable `evals/files/webhook.ts` earns a Socket warning on skills.sh | read and used, 2026-10-24 |
| External APIs | `using-mtcute` | `DO_NOT_TRACK=1 npx skills add mtcute/mtcute --skill using-mtcute -a claude-code codex -y` | Official mtcute skill; three scripts look up methods, TL constructors and classes in the installed `@mtcute/core` | Run the scripts from the project root: `node .claude/skills/using-mtcute/tools/get-method.js <name>` | read and used, 2026-10-24 |
| Frontend | `vercel-react-best-practices` | `DO_NOT_TRACK=1 npx skills add vercel-labs/agent-skills --skill vercel-react-best-practices -a claude-code codex -y` | 70 React performance rules: re-renders, rendering, bundle size, async waterfalls, JS hot paths | 10 rules are Next.js server-side and do not apply to a client-only app; last updated 2026-04 | read and used, 2026-10-24 |
| Testing | `vitest` | `DO_NOT_TRACK=1 npx skills add antfu/skills --skill vitest -a claude-code codex -y` | Vitest by Anthony Fu, generated from the official docs: API, mocking, config, filtering, coverage | Regenerated often; the line "based on Vitest X" may name a beta ahead of the project. Features labeled "(5.1)" and under "v5.1 Additions" do not exist on 5.0 | read and used, 2026-10-24 |

## Named by the owner, install when the layer appears

| Layer | Skill | Install | When | Checked |
|---|---|---|---|---|
| Deploy and CI | `github-actions-docs` | `DO_NOT_TRACK=1 npx skills add xixu-me/skills --skill github-actions-docs -a claude-code codex -y` | The project deploys or tests through GitHub Actions. Grounds workflow syntax, triggers, runners, secrets and OIDC in the official docs; does not check whether third-party action versions are current | header read, 2026-10-24 |
| AI infrastructure | `designing-ai-infra` | `DO_NOT_TRACK=1 npx skills add ilkruglov/designing-ai-infra-skill -l` first (the skill sits under `plugins/designing-ai-infra/skills/`) | The project runs its own model inference or training: GPU memory, KV cache, batching, TTFT/TPOT, parallelism, cost per token. Not for projects that call a hosted API | header read, 2026-10-24 |

## Never install per project

- `claude-api`: built into Claude Code.
- The owner's global set (`property-testing`, `prod-recon`, `find-docs`, `diagnosing-bugs`,
  `session-handoff`, `issue-register`, `goal-rules`, `sparring`, `worklog` and others): read the
  current list from the layout check; these count as coverage, never as candidates.
- The owner's own skills live in `nyxandro/<name>-skill` repositories and are listed in the
  `nyxandro/skills` plugin catalog.

## Dead ends

Checked and not worth installing, so they are not checked again:

| What | Why not | Checked |
|---|---|---|
| `recharts/recharts` `guide` | For authors of the Recharts docs site, not for users. No official user-facing Recharts skill; a project with a brand book follows it instead | 2026-10-24 |
| Skills in `google/A2UI` (`.agents/skills/a2ui-*`) | For A2UI contributors: issue triage, releases, SDK work. For the protocol, read the installed `@a2ui/web_core` sources | 2026-10-24 |
| CopilotKit `a2ui-renderer` | Removed on 2026-09-10; replaced by `copilotkit` | 2026-10-24 |
| `yusukebe/hono-skill` | Moved to `honojs/skills` | 2026-10-24 |
| Drizzle skills | No official one; the popular community ones are written for other projects' code | 2026-10-24 |
| `@tma.js` Mini App SDK skills | Only small community skills with a few dozen installs | 2026-10-24 |
| LangChain `ecosystem-primer` | Tells the agent to always set `LANGSMITH_TRACING=true`, which sends prompts and data to LangSmith, through environment variables | 2026-10-24 |
| Ranking by install count | Unrelated skills with 100K+ installs top many searches ("github actions", "docker") | 2026-10-24 |
