# AGENTS.md

Guidance for AI agents and humans working in this repository.

## What this repo is

`ctmkit` — a modular Control-M library + CLI powering GitOps for the
`orchestration-manifests` repo. Design lives in
`orchestration-manifests/docs/2026-06-10-control-m-gitops-design.md`.

## Golden rules

1. **TDD.** Write the failing test first (every test is offline — use `httpx.MockTransport`
   or monkeypatch; never hit the network).
2. **No god scripts, no flat structure.** Each module has one responsibility under the right
   package: `aapi/` (REST services), `deploy/` (orchestration), `promote/`, `policy/`,
   `kpi/`, `cli/` (one sub-app per surface).
3. **Google-style docstrings** on every public symbol (Args/Returns/Raises).
4. **CLI convention:** `ctmkit <surface> <verb> --options`. Endpoints come from `--env`
   (resolved via `config/environments.yaml`); api-key from `$CTM_API_KEY`.
5. **Secrets never in code.** API key from Vault; in-manifest secrets are `{"Secret": …}`
   references only.

## Workflow

```bash
uv sync
uv run pytest -q          # must stay green
uv run ruff check .
```

Branch from `main`, conventional-commit messages, PR with a second reviewer. Keep
`CHANGELOG.md` updated.

## Layout

```
src/ctmkit/
  aapi/      deploy/    promote/   policy/   kpi/
  cli/       config.py  naming.py  schema.py validate.py
tests/       (mirrors src/, all offline)
```
