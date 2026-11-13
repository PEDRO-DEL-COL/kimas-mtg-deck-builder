# Kima's MTG Deck Builder

Montador de decks de **Magic: The Gathering** (Commander) de código aberto, com dados de cartas do Scryfall e preços em reais (R$) da LigaMagic.

> **Status:** v0.1.0 — esqueleto do projeto, em desenvolvimento inicial. Nem todas as funcionalidades abaixo existem ainda.

## Funcionalidades (MVP)

Consulte a especificação completa em [docs/SPEC.md](docs/SPEC.md). Resumo:

- Busca de cartas (dados do Scryfall).
- Montagem de decks Commander 10 com validação automática das regras.
- Preços em R$ vindos da LigaMagic, sempre com a data da coleta.
- Cálculo de custo total do deck e do orçamento restante.

## Regras do Commander 10

- Deck de **100 cartas**.
- **Comandante** custa no máximo **R$ 5**.
- As demais cartas **não básicas** somam no máximo **R$ 10**.

## Stack

- **Backend:** Python 3.12, FastAPI, SQLAlchemy, Alembic.
- **Frontend:** React 19, TypeScript, Vite, Tailwind CSS 4.
- **Banco de dados:** SQLite local; Postgres (Supabase) em produção.
- **Dados:** Scryfall (cartas) e LigaMagic (preços).

## Configuração (sem Docker)

### Backend

Windows (PowerShell):

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
Copy-Item ..\.env.example ..\.env
alembic upgrade head
uvicorn app.main:app --reload
```

Linux/macOS:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp ../.env.example ../.env
alembic upgrade head
uvicorn app.main:app --reload
```

A API fica em http://localhost:8000 (verifique `/health`).

### Frontend

```bash
cd frontend
npm install
npm run dev
```

O app fica em http://localhost:5173. A URL da API é configurada por `VITE_API_URL`.

## Docker Compose (opcional, não testado)

```bash
cp .env.example .env
docker compose up --build
```

Sobe Postgres local, API (8000), frontend (5173) e um worker placeholder. Esta configuração ainda não foi testada. Em produção o alvo é o Supabase.

## Qualidade

Backend (a partir de `backend/`):

```bash
ruff check .
black --check .
mypy app
pytest -q
```

Frontend (a partir de `frontend/`):

```bash
npm run lint
npm run typecheck
npm run format:check
npm run build
```

## Créditos

- Dados e imagens de cartas: [Scryfall](https://scryfall.com), conforme as [diretrizes do Scryfall](https://scryfall.com/docs/api/images).
- Preços: LigaMagic, exibidos sempre com a data da coleta. A coleta (scraping) só deve ser feita após verificar os Termos de Uso e o `robots.txt` do site e obter permissão quando necessário.

## Aviso legal

Este é um projeto não oficial de fãs (Fan Content). Não é afiliado, patrocinado nem endossado pela Wizards of the Coast. Magic: The Gathering e seus elementos são propriedade da Wizards of the Coast LLC.

## Contribuindo

Veja [CONTRIBUTING.md](CONTRIBUTING.md) e o estado atual do projeto em [docs/PROJECT_STATE.md](docs/PROJECT_STATE.md).

## Licença

[AGPL-3.0](LICENSE)
