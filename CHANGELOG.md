# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-11-13

### Added

- Scryfall Bulk Data importer (`python -m app.jobs.scryfall_import`): streams JSON or JSON Lines, skips non-game layouts, upserts cards on SQLite and PostgreSQL.
- Card search API `GET /api/cards` (name, color identity, mana colors, type, subtype, CMC range, oracle text, rarity, Commander legality, USD price range, sorting, pagination) and `GET /api/cards/{id}`.
- Scryfall USD prices (`usd`, `usd_foil`, `usd_etched`) stored with the bulk data date and shown as "US$ ... (Scryfall)" with the date.
- Currency-explicit Commander 10 budget (`Money`), with a `PriceConverter` interface; no conversion implemented (BRL estimate is a documented TODO, never a flat rate).
- Frontend card search page in PT-BR: filters, card grid, card detail modal with Scryfall credit, shareable hash URLs.
- Migrations: denormalised color keys and CMC index (0002), optional Postgres `pg_trgm` trigram indexes (0003), USD price columns (0004), Row Level Security on all tables in Postgres (0005).
- Hosted Supabase project schema applied via the Management API.

### Changed

- Settings also read the repository-root `.env` when running from `backend/`.
- Default Scryfall bulk type is `oracle_cards`.

## [0.1.0] - 2026-11-13

### Added

- Project skeleton.
- FastAPI backend with `/health` endpoint, settings, SQLAlchemy models and initial Alembic migration.
- Commander 10 validator (100 cards, commander <= R$5, other non-basic cards total <= R$10) with unit tests.
- React/Vite/Tailwind frontend with dark theme home page and credits footer.
- Docker Compose, CI (GitHub Actions), pre-commit and project docs.

[Unreleased]: https://github.com/PEDRO-DEL-COL/kimas-mtg-deck-builder/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/PEDRO-DEL-COL/kimas-mtg-deck-builder/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/PEDRO-DEL-COL/kimas-mtg-deck-builder/releases/tag/v0.1.0
