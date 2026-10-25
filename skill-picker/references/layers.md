# Layers of a project

Every technology that matters goes into one layer. The signals come from step 1 of SKILL.md
and the project docs. "Typical skills" names the kind of skill that serves the layer; concrete
skills with install commands are in `catalog.md`.

## 1. Languages and runtimes

- **Signals**: `engines`, `packageManager`, `requires-python`, the `go` line, `rust-version`,
  Dockerfile `FROM` images, `.nvmrc`.
- **Typical skills**: rarely needed. A language-level skill (advanced TypeScript types, modern
  Python typing) only when the project leans on that part of the language heavily.

## 2. Agent and LLM layer

- **Signals**: `@mastra/*`, `ai` (Vercel AI SDK), `openai`, `@anthropic-ai/sdk`,
  `@anthropic-ai/claude-agent-sdk`, `langchain`, `@langchain/langgraph`, `llamaindex`, `crewai`,
  `pydantic-ai`, `@modelcontextprotocol/sdk`, `@copilotkit/*`, `@ag-ui/*`, `@a2ui/*`; folders of
  prompts, tools, evals.
- **Typical skills**, usually more than one:
  - the agent framework's own skill (Mastra, LangGraph);
  - a framework-neutral skill on agent design: context, tools, memory, evals, multi-agent
    coordination (`developing-ai-agents`);
  - the agent UI protocol's skill when agents render UI (CopilotKit, AG-UI, A2UI);
  - `claude-api`, built into Claude Code, when the project calls Claude directly;
  - `designing-ai-infra` only when the project runs its own model inference or training
    (vLLM, SGLang, TensorRT, GPU sizing), not when it calls a hosted API.

## 3. External APIs and protocols

- **Signals**: Telegram Bot API libraries (`grammy`, `telegraf`, `aiogram`,
  `python-telegram-bot`), MTProto clients (`@mtcute/*`, `telethon`, `pyrogram`, `gramjs`),
  payments (`stripe`, `yookassa`), OAuth providers, other SaaS SDKs; the spec names them too.
- **Typical skills**: the API's own skill when it checks the live docs. An API that ships monthly
  (the Bot API) is high risk whatever the library.

## 4. Frontend and design

- **Signals**: `react`, `vue`, `svelte`, `solid-js`, routers, chart libraries, UI kits, Mini App
  SDKs (`@tma.js/*`, `@telegram-apps/*`), a design system folder in the docs.
- **Typical skills**: performance and composition rules for the framework
  (`vercel-react-best-practices`), the framework's official skill. A design system in the repo
  outranks any generic design or chart-styling skill; if a skill would mostly fight it, skip it.

## 5. Backend and HTTP

- **Signals**: `hono`, `express`, `fastify`, `@nestjs/*`, `fastapi`, `django`, `flask`, Go
  routers.
- **Typical skills**: the framework's official skill, only if the version is fresh or the project
  uses less common features. Mature frameworks are usually ⚪ with `find-docs`.

## 6. Data and database

- **Signals**: ORMs and query builders (`drizzle-orm`, `prisma`, `sqlalchemy`, `kysely`,
  `typeorm`), migration tools, `pg`, `pgvector` images, Redis, queues; compose services with
  database images.
- **Typical skills**: the ORM's official skill when one exists; Postgres practice skills.
  Migrations touch persisted data: rate this layer one step higher than the library alone
  suggests.

## 7. Testing

- **Signals**: `vitest`, `jest`, `pytest`, `go test`; `fast-check`, `hypothesis`; `playwright`,
  `cypress`; a test-first rule in the agent instructions.
- **Typical skills**: the runner's skill (a test-first project runs it in every task);
  property-based testing (`property-testing`, often in the owner's global set); browser and e2e
  (the owner's global `agent-browser` first; a framework's own skill only after vetting).

## 8. Build and tooling

- **Signals**: `vite`, `webpack`, `turbo`, `esbuild`, `rolldown`; package managers; linters and
  formatters (`@biomejs/biome`, `eslint`, `ruff`); the TypeScript version.
- **Typical skills**: the bundler's skill only when its config changes often or a fresh major
  changed its internals. Usually ⚪.

## 9. Deploy and CI/CD

- **Signals**: the deploy and CI files found in step 1: `.github/workflows/*` and the actions they use,
  other CI files, Dockerfiles and compose, hosting files (`vercel.json`, `wrangler.toml`,
  `fly.toml`, Terraform). With no such files, the ops docs say how the project ships (for
  example ssh, rsync and compose on a server).
- **Typical skills**: `github-actions-docs` for GitHub Actions; the platform's official skills
  (Vercel, Cloudflare) for platform deploys; nothing extra for a hand deploy described in docs.
  Production access and read-only checks are the owner's global `prod-recon`.

## 10. Observability and operations

- **Signals**: loggers (`pino`, `structlog`), tracing (`@opentelemetry/*`, Langfuse), metrics,
  alerting configs, backup jobs in compose.
- **Typical skills**: the vendor's skill when the project depends on its API; otherwise ⚪.

## 11. Security and auth

- **Signals**: auth libraries (`better-auth`, `@clerk/*`, `next-auth`, `lucia`), init-data or
  webhook signature checks, secrets handling.
- **Typical skills**: the auth library's official skill. Mistakes here are security mistakes:
  rate one step higher.

## 12. Process

- **Signals**: issue registers, handoff documents, plans in `docs/`.
- **Typical skills**: the owner's global process skills (handoff, issue register, goal mode,
  worklog). Never install these per project.

## Narrow cases

Some risks sit below the library level and are easy to miss: a protocol's message format (A2UI
components, the MTProto TL schema), payment rules (Telegram Stars), an unusual runtime (Bun,
Deno, Cloudflare Workers), a beta feature the project depends on. Give each its own row when the
project leans on it.
