# Project State — Kima's MTG Deck Builder

> Living handoff file. **Keep it updated at the end of every work session** (status, DONE, TODO, decisions).
> To resume on any machine: read `docs/PROJECT_STATE.md` (this file), then `docs/SPEC.md`, then `CLAUDE.md`.

Last updated: 2026-11-13

## 1. What the project is
Open-source web app (AGPL-3.0) to build Magic: The Gathering decks, focused on the **Commander 10** format
(100 cards; commander <= R$ 5,00; sum of all other non-basic-land cards <= R$ 10,00). Card data/images from
**Scryfall**; Brazilian prices from **LigaMagic** (scraped, cached in DB, always shown with collection date).
Full spec (Portuguese): `docs/SPEC.md` — the source of truth for scope.

## 2. Current status
- Version: **v0.1.0** (pre-release, skeleton). SemVer; changes logged in `CHANGELOG.md` (Keep a Changelog).
- Roadmap step 1 (skeleton) done, except Docker Compose is written but **untested** (no Docker on the dev machine).
- Supabase project **not created yet** (waiting for `SUPABASE_ACCESS_TOKEN`).

## 3. DONE
- [x] Git repo, `main` branch, `.gitignore` (OneDrive-safe: node_modules, .venv, caches, .env, *.db ignored)
- [x] AGPL-3.0 `LICENSE` (official text from GitHub licenses API)
- [x] Public GitHub repo + topics
- [x] Backend: FastAPI app (`/health`), pydantic-settings config, SQLAlchemy 2 models for all spec section-5 tables,
      Alembic with initial migration `0001_initial_schema`, Pydantic schema stubs, empty `services/ scrapers/ jobs/`
- [x] Commander 10 validator `backend/app/services/commander10.py` (pure functions, Decimal money,
      singleton rules incl. basics/snow basics/"any number"/Seven Dwarves, unknown-price reporting) + 16 unit tests
- [x] Backend quality: ruff, black, mypy (strict), pytest — all passing (17 tests)
- [x] Frontend: Vite + React 19 + TS strict + Tailwind 4, section-7 dark palette tokens, Inter + JetBrains Mono,
      PT-BR home page, Header, Footer with Scryfall/LigaMagic credits, `PriceTag` component, API client
- [x] Frontend quality: ESLint (flat) + Prettier, lint/typecheck/format:check/build passing
- [x] `docker-compose.yml` (db, api, web, worker) + Dockerfiles — **written, untested**
- [x] `.env.example` (placeholders only), `.pre-commit-config.yaml`, GitHub Actions CI (`.github/workflows/ci.yml`)
- [x] README (PT-BR), CONTRIBUTING (PT-BR), CHANGELOG, this file, `CLAUDE.md`
- [x] Tag `v0.1.0` + GitHub pre-release

## 4. TODO / next steps (mapped to SPEC section 10)
1. **Skeleton (step 1)** — remaining:
   - [ ] Create Supabase project in the user's account once `SUPABASE_ACCESS_TOKEN` is available; put the
         connection string only in local `.env` / deploy secrets; run `alembic upgrade head` against it.
   - [ ] Test `docker compose up` on a machine with Docker (or skip in favour of hosted deploy).
   - [ ] Add pg_trgm extension + trigram indexes (Postgres only) in a migration.
2. **Scryfall import + search (step 2)**
   - [ ] Job `jobs/scryfall_import.py`: download Bulk Data (`oracle_cards`), upsert `cards`, keep only needed fields + image URLs (never host images). Respect Scryfall API guidelines (User-Agent, 50–100 ms between requests).
   - [ ] Search API `GET /cards` with filters: color identity, colors, type, subtype, CMC, oracle text, rarity, commander legality, BRL price range.
   - [ ] Frontend search page with filters.
3. **Deck builder + Commander 10 validation (step 3)**
   - [ ] Deck endpoints using `services/commander10.py`; partner/background commanders (TODO in validator).
   - [ ] Frontend deck builder: commander pick, add/remove, group by type and mana curve, 100-card counter, live budget meter.
   - [ ] Import/export plain text lists ("1 Card Name") compatible with LigaMagic, Moxfield, TopDecked.
4. **LigaMagic prices (step 4)**
   - [ ] **Before any production scraping: read LigaMagic Terms of Use and robots.txt and ask the user/LigaMagic for permission.**
   - [ ] `scrapers/ligamagic.py` parser tested with saved HTML fixtures (`backend/tests/fixtures/`).
   - [ ] Price job every 3 days (APScheduler worker), polite rate limit (>= `LIGAMAGIC_MIN_DELAY_SECONDS`), identified User-Agent, off-peak, prioritise cards in decks/recently searched; on failure keep last valid price.
   - [ ] On-demand single-card refresh; `price_runs` bookkeeping.
5. **Users + saved decks (step 5)**
   - [ ] Registration/login, argon2 password hashing, JWT; decks per user.
6. **Visual identity + deploy (step 6)**
   - [ ] Polish UI; choose host (Render / Railway / VPS) + Supabase Postgres; production CORS/secrets.

## 5. User notes and instructions (keep honouring these)
- Use skills / connectors / plugins as needed, but **ask the user before installing new ones** (tools, plugins, MCP servers, global packages).
- **Optimise credit usage** (see token-economy tips in `CLAUDE.md`).
- **Proper versioning**: SemVer, Conventional Commits, Keep a Changelog, tags + GitHub releases.
- **Always keep this process/TODO file updated.**
- **Ask the user whenever in doubt.**
- User's browser: **Zen Browser** — `C:\Users\Pedro.Col\AppData\Local\Zen Browser\zen.exe` (use it to open local pages for the user).
- The Supabase project will be created **in the user's own account** once `SUPABASE_ACCESS_TOKEN` is available.
- Agent policy: one Opus PM coordinates; implementation delegated to small, well-scoped Sonnet workers. A second Opus agent requires user approval.
- Never print or commit secrets.

## 6. Stack and tooling
- Backend: Python 3.12, FastAPI, Uvicorn, SQLAlchemy 2, Alembic, Pydantic v2 + pydantic-settings, psycopg 3, httpx.
  Dev: ruff, black, mypy (strict), pytest. Future: APScheduler, selectolax/BeautifulSoup, argon2, PyJWT.
- Database: SQLite for quick local dev (default `DATABASE_URL`); **Supabase (hosted PostgreSQL)** for shared/prod; local Postgres via Docker Compose optional.
- Frontend: React 19, TypeScript (strict), Vite, Tailwind CSS 4 (`@tailwindcss/vite`), ESLint (flat config) + Prettier.
  Tailwind tokens: `background surface border text muted primary primary-hover success success-hover danger`, `font-sans` (Inter), `font-mono` (JetBrains Mono), `rounded-card`, `shadow-card`.
- Infra: Docker Compose (api, web, db, worker) — untested; GitHub Actions CI; pre-commit.
- Dev machine: Windows, Git 2.56, gh CLI, Node 24, Python 3.12. **No Docker, no Supabase CLI** (`npx supabase` is acceptable if needed).

## 7. Important decisions (with rationale)
| Decision | Rationale |
|---|---|
| License **AGPL-3.0** | Open source; network-use clause ensures hosted forks share their changes. |
| **Supabase** as hosted Postgres | Free managed Postgres (pg_trgm available) without running Docker locally; access via plain `DATABASE_URL`, so the app stays provider-agnostic. |
| SQLite default for local dev | Zero-install dev on a machine without Docker; Alembic migrations kept portable. |
| **No Docker locally** | Not installed; Compose files are maintained but verified only when Docker is available (or in CI later). |
| **OneDrive caveat** | Repo lives in OneDrive: heavy dirs (`node_modules`, `.venv`, caches, `dist`) are gitignored; avoid huge installs/data dumps in the folder (put Scryfall bulk files outside or in ignored `data/`). Consider moving the repo out of OneDrive if sync causes file-lock issues. |
| **LigaMagic scraping** | No official API. Must check ToS and robots.txt and **ask permission before production**; credits/links do not replace permission. Polite rate limits, identified User-Agent. |
| **Prices always read from DB** with collection date | Never hit LigaMagic during user browsing; every price shown as "Preço LigaMagic em DD/MM/AAAA"; failures keep the last valid price. |
| Money as `Decimal` / `Numeric(10,2)` | Exact BRL budget comparisons (5.00 / 10.00 boundaries). |
| `oracle_id` (not printing) for prices/decks | Commander budget concerns the card, not a specific printing. |

## 8. Repo and accounts (no secrets here)
- GitHub: https://github.com/PEDRO-DEL-COL/kimas-mtg-deck-builder (public, owner `PEDRO-DEL-COL`).
- Commit identity (local repo config): `PEDRO-DEL-COL` / GitHub noreply email.
- Supabase: not created yet. Credentials will live only in `.env` (gitignored) and deploy secrets.

## 9. How to run
Backend (from `backend/`):
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate   |   Linux/macOS: source .venv/bin/activate
pip install -e ".[dev]"
cp ../.env.example ../.env   # edit values; never commit .env
alembic upgrade head
uvicorn app.main:app --reload       # http://localhost:8000/health
ruff check . && black --check . && mypy app && pytest -q
```
Frontend (from `frontend/`):
```bash
npm install
npm run dev                          # http://localhost:5173
npm run lint && npm run typecheck && npm run format:check && npm run build
```
Docker (untested): `docker compose up --build` from the repo root (needs `.env`).
Pre-commit (optional, requires installing `pre-commit` — ask user first): `pre-commit install`.

## 10. How to resume
1. Read `docs/PROJECT_STATE.md`, `docs/SPEC.md`, `CLAUDE.md`.
2. `git pull`; check `gh run list -L 3` for CI status.
3. Pick the next unchecked item in section 4; update this file + `CHANGELOG.md` when done.
