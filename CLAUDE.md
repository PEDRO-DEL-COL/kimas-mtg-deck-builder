# CLAUDE.md — Kima's MTG Deck Builder

Start every session by reading, in order:
1. `docs/PROJECT_STATE.md` — current status, DONE/TODO, user notes, decisions, how to run.
2. `docs/SPEC.md` — full project spec (Portuguese), source of truth for scope.

At the end of every session, update `docs/PROJECT_STATE.md` (status, checklist, decisions) and `CHANGELOG.md`.

## Conventions
- Code, identifiers, comments and commit messages in **English**; all site UI text in **Brazilian Portuguese**.
- **Conventional Commits** (`feat:`, `fix:`, `chore:`, `docs:`, `ci:`, `build:`, `test:`, `refactor:`), small logical commits.
- **SemVer** + Keep a Changelog; tag releases (`vX.Y.Z`) and create GitHub releases.
- Every business rule (deck validation, Commander 10 budget, price logic) needs **unit tests**.
- Config/secrets only via environment variables; never print or commit secrets (`.env` is gitignored).
- Prices are always read from the DB and shown with their collection date; never query LigaMagic on user requests.
- LigaMagic scraping: check ToS/robots.txt and get permission before production use.
- Checks before committing:
  - backend/: `ruff check . && black --check . && mypy app && pytest -q`
  - frontend/: `npm run lint && npm run typecheck && npm run format:check && npm run build`

## Agent policy
- One **Opus** agent acts as PM/coordinator; implementation goes to **Sonnet** subagents with small, well-scoped tasks and exact file lists (disjoint files when running in parallel; workers don't run git, the PM commits).
- **Ask the user before** spawning a second Opus agent, or installing any new tool, plugin, MCP server or global package.
- When in doubt, ask the user.
- User's browser: Zen Browser (`C:\Users\Pedro.Col\AppData\Local\Zen Browser\zen.exe`).

## Token economy
- Read only the files/sections you need (use Grep/Glob, `offset`/`limit`); don't re-read files after editing.
- Give workers the exact commands and facts they need instead of having them rediscover context.
- Batch independent tool calls; avoid verbose command output (`-q`, `| tail`).
- Keep reports and summaries short.

## Environment notes
- Repo is inside OneDrive: keep `node_modules`, `.venv`, caches and data dumps gitignored; avoid heavy installs here.
- Windows dev machine; no Docker and no Supabase CLI locally (`npx supabase` acceptable).
- The path contains `´` (Pedro´s Codes): quote paths in shell commands.
