# Contribuindo

Obrigado por querer contribuir com o Kima's MTG Deck Builder!

## Convenções

- **Commits:** seguimos [Conventional Commits](https://www.conventionalcommits.org/pt-br/) (`feat:`, `fix:`, `docs:`, `chore:`, `test:`, `refactor:`...).
- **Idioma:** código, nomes, comentários e mensagens de commit em **inglês**; textos da interface (UI) em **português do Brasil**.
- **Testes:** regras de negócio (por exemplo, o validador do Commander 10) exigem testes automatizados.

## Fluxo de trabalho

1. Crie uma branch a partir de `main` (`feat/minha-feature`, `fix/meu-bug`).
2. Faça commits pequenos e descritivos.
3. Garanta que as verificações de qualidade passam (veja "Qualidade" no [README](README.md)).
4. Abra um Pull Request para `main` descrevendo o que mudou e por quê.

## pre-commit

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

Os hooks rodam ruff e black no backend, além de eslint e prettier no frontend (requer `npm install` em `frontend/`).

## Versionamento e changelog

Usamos [SemVer](https://semver.org/lang/pt-BR/). Toda mudança relevante deve ser registrada na seção `[Unreleased]` do [CHANGELOG.md](CHANGELOG.md) (formato Keep a Changelog, em inglês).

Veja também [docs/PROJECT_STATE.md](docs/PROJECT_STATE.md) e [docs/SPEC.md](docs/SPEC.md).
