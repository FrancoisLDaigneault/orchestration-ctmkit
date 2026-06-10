# Contributing to ctmkit

Thanks for helping build the Control-M GitOps toolkit. This guide covers local setup,
our conventions, and the review flow.

## Local setup

```bash
uv sync                 # create the venv + install deps (Python 3.12)
uv run pytest -q        # run the full suite (every test is offline)
uv run ruff check .     # lint
```

## Conventions

- **TDD** — write a failing test first, then the minimal code to pass it.
- **Small, single-responsibility modules** — no god scripts, no flat dumping. New behaviour
  goes in a focused module under the right package (`aapi/`, `deploy/`, `promote/`, `policy/`,
  `kpi/`, `cli/`, `docs/`).
- **Google-style docstrings** on every public function/class (Args/Returns/Raises).
- **CLI** follows `ctmkit <surface> <verb> --options`; one Typer sub-app per surface in
  `cli/<surface>.py`, shared Rich output via `cli/_console.py`.
- **Offline tests** — never hit the network; inject `httpx.MockTransport` or monkeypatch.
- **Typed** — keep `mypy`/type-checkers happy; the package ships `py.typed`.

## Commits & branches

- Branch from `main`; one logical change per commit.
- Conventional-commit style messages: `feat(deploy): …`, `fix(docs): …`, `test(cli): …`.
- Open a PR; CI (lint + tests) must be green. A second reviewer approves before merge.

## Releasing

Versions are published to Artifactory from `main` tags. Bump `version` in `pyproject.toml`
and add a `CHANGELOG.md` entry under a new heading.
