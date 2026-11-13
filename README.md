# Kima's MTG Deck Builder

Montador de decks de **Magic: The Gathering** (Commander) de código aberto, com dados de cartas do Scryfall. Por enquanto os preços exibidos são os preços em **dólar (US$) do Scryfall**; preços/estimativas em reais (R$) estão planejados.

> **Status:** v0.2.0 — importação do Scryfall e busca de cartas com filtros prontas. Deck builder, usuários e preços em R$ ainda não existem.

## Funcionalidades (MVP)

Consulte a especificação completa em [docs/SPEC.md](docs/SPEC.md). Resumo:

- Busca de cartas (dados do Scryfall).
- Montagem de decks Commander 10 com validação automática das regras.
- Preços sempre com fonte e data. Hoje: US$ do Scryfall (sem conversão). Futuro: estimativa em R$ baseada em estudo manual LigaMagic × Scryfall (nunca câmbio fixo).
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

A API fica em http://localhost:8000 (verifique `/health`; busca em `/api/cards`).

Importar as cartas do Scryfall (baixa o Bulk Data "Oracle Cards", ~200 MB, para `backend/data/`, que é ignorado pelo git):

```bash
python -m app.jobs.scryfall_import            # ou --file caminho/arquivo.jsonl
```

### Banco no Supabase (opcional)

O projeto Supabase já existe (ref `mmkzcrrfonqxezccnomb`, região us-west-2) com o schema aplicado (migração `0005`).
Para usar, copie a *connection string* do painel do Supabase (Project Settings → Database → Connection string, modo
*Session pooler*) e cole **somente no seu `.env` local** como `DATABASE_URL`, trocando o driver para `postgresql+psycopg://`
e preenchendo sua senha do banco. Nunca faça commit do `.env`.

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
- Preços atuais: US$ do Scryfall (snapshot do Bulk Data), exibidos com a data.
- LigaMagic: **nenhum dado é coletado**. A coleta automática só acontecerá com permissão por escrito da LigaMagic.

## Aviso legal

Este é um projeto não oficial de fãs (Fan Content). Não é afiliado, patrocinado nem endossado pela Wizards of the Coast. Magic: The Gathering e seus elementos são propriedade da Wizards of the Coast LLC.

## Contribuindo

Veja [CONTRIBUTING.md](CONTRIBUTING.md) e o estado atual do projeto em [docs/PROJECT_STATE.md](docs/PROJECT_STATE.md).

## Licença

[AGPL-3.0](LICENSE)
