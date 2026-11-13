# Kima's MTG Deck Builder — Especificação do Projeto

> Transcrição fiel do PDF original "Kima's MTG Deck Builder — Especificação do Projeto". Fonte de verdade do escopo.

Objetivo: um site de deck builder de Magic: The Gathering com busca avançada (dados do Scryfall) e preços do mercado brasileiro (LigaMagic), pensado inicialmente para o formato Commander 10.

## 1. Visão geral
- Nome: **Kima's MTG Deck Builder** (Kima, de Kimataro).
- Tipo: aplicação web (site), acessível pelo navegador no desktop e no celular.
- Problema: montar decks vendo ao mesmo tempo filtros avançados (cor, identidade, tipo, custo, texto) e o preço em reais, para não terminar um deck e descobrir que estourou o orçamento.
- Caso de uso principal: formato **Commander 10** — deck de 100 cartas, comandante de até R$ 5,00 e a soma das cartas que não são terreno básico nem comandante de até R$ 10,00.

## 2. Funcionalidades (MVP)
1. **Busca de cartas** com filtros: identidade de cor, cores do custo, tipo, subtipo, custo de mana (CMC), texto da carta (oracle), raridade, legalidade em Commander e faixa de preço em R$.
2. **Deck builder**: escolher o comandante, adicionar e remover cartas, agrupar por tipo e por curva de mana, contador de 100 cartas e validação de singleton (exceto terrenos básicos e cartas que permitem cópias).
3. **Validação de orçamento Commander 10**: mostra em tempo real o preço do comandante (limite R$ 5) e a soma das demais cartas (limite R$ 10), com alerta visual ao ultrapassar.
4. **Preços do LigaMagic**: cada carta exibe o menor preço e o preço médio em R$, a **data da última atualização** e um link direto para a página da carta no LigaMagic.
5. **Usuários**: cadastro, login e decks salvos por usuário.
6. **Importar e exportar** listas em texto simples (formato "1 Nome da Carta"), compatível com LigaMagic, Moxfield e TopDecked.
7. **Créditos visíveis**: rodapé e páginas de carta deixando claro que os dados de cartas e imagens vêm do Scryfall e os preços vêm do LigaMagic.

## 3. Stack sugerida
- Backend: Python 3.12, FastAPI, SQLAlchemy 2, Alembic (migrations), Pydantic.
- Banco: PostgreSQL (SQLite aceitável para desenvolvimento local).
- Busca: índices no Postgres (pg_trgm para nome e texto) e filtros por colunas de cor e tipo.
- Jobs agendados: APScheduler (simples) ou Celery + Redis (se crescer).
- Scraping: httpx + selectolax ou BeautifulSoup, com limite de requisições.
- Frontend: React + TypeScript + Vite + Tailwind CSS.
- Autenticação: JWT com senha em hash (argon2 ou bcrypt).
- Infra: Docker Compose (api, web, db, worker); deploy futuro em Render, Railway ou VPS.
- Qualidade: ruff + black, mypy, pytest; ESLint + Prettier no frontend; pre-commit.

## 4. Arquitetura e fluxo de dados
- **Importação do Scryfall**: job diário baixa o Bulk Data "Oracle Cards" (ou "Default Cards") e faz upsert na tabela de cartas. Guardar apenas campos necessários e URLs das imagens (não hospedar imagens).
- **Atualização de preços**: job a cada 3 dias percorre as cartas e consulta o preço no LigaMagic, gravando valor e data. Também é possível atualizar sob demanda uma carta específica.
- **Cache**: o site sempre lê preços do próprio banco, nunca consulta o LigaMagic na hora em que o usuário navega.
- **Exibição**: todo preço aparece junto com a data da coleta (ex.: "Preço LigaMagic em 08/11/2026").

## 5. Modelo de dados (inicial)
- users: id, username, email, password_hash, created_at.
- cards: id (scryfall_id), oracle_id, name, printed_name_pt (quando houver), mana_cost, cmc, type_line, oracle_text, colors, color_identity, rarity, legal_commander, image_url, scryfall_uri.
- card_prices: id, oracle_id, min_price_brl, avg_price_brl, ligamagic_url, collected_at.
- price_runs: id, started_at, finished_at, cards_ok, cards_failed, status.
- decks: id, user_id, name, format, commander_oracle_id, created_at, updated_at.
- deck_cards: deck_id, oracle_id, quantity, category (opcional, ex.: "ramp", "sacrifício").

## 6. Scraping do LigaMagic — regras e cuidados
- LigaMagic não tem API pública oficial; coleta lendo páginas públicas das cartas.
- **Antes de produção**: ler termos de uso e robots.txt e, idealmente, pedir autorização à equipe. Créditos e links não substituem permissão caso os termos proíbam coleta automatizada.
- Ser gentil: no máximo 1 requisição a cada poucos segundos, User-Agent identificado, horários de pouco movimento, priorizar cartas em decks ou buscadas recentemente.
- Isolar o parser em `scrapers/ligamagic.py` com testes usando HTML salvo.
- Em caso de falha, manter o último preço válido e mostrar a data antiga, sem apagar dados.

## 7. Identidade visual
- 100% dark mode, sem tema claro.
- Fundo principal `#0F0F14`; superfícies/cards `#1A1A23`; bordas `#2A2A36`.
- Texto principal `#E6E6EB`; secundário `#A0A0AB`.
- Roxo (ações principais, links, seleção) `#8B5CF6`, hover `#A78BFA`.
- Verde (preço dentro do orçamento, sucesso) `#22C55E`, hover `#4ADE80`.
- Alerta de orçamento estourado: vermelho suave `#F87171`.
- Tipografia: Inter (interface) e JetBrains Mono (números e preços).
- Cantos arredondados, sombras discretas, contraste confortável.

## 8. Estrutura de pastas sugerida
- `backend/app/` — main.py, api/, models/, schemas/, services/, scrapers/, jobs/, core/
- `backend/tests/`
- `frontend/src/` — pages/, components/, hooks/, api/, styles/
- docker-compose.yml, .env.example, README.md

## 9. Padrões de desenvolvimento
- Código, variáveis e commits em inglês; interface do site em português.
- Conventional Commits (feat, fix, chore...).
- Configurações sensíveis só via variáveis de ambiente.
- Toda regra de negócio (validação de deck e orçamento) com testes unitários.

## 10. Roteiro de implementação
1. Subir o esqueleto com Docker Compose (FastAPI, Postgres, React).
2. Importar o Bulk Data do Scryfall e criar a busca com filtros.
3. Criar o deck builder e a validação do Commander 10.
4. Implementar o scraper do LigaMagic com cache e exibição da data do preço.
5. Adicionar usuários e decks salvos.
6. Aplicar a identidade visual completa e preparar o deploy.
