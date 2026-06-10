# ctmkit

A Control-M library + CLI for Jobs-as-Code GitOps: site-standard validation, Automation-API
build/deploy/transform, ordered deploys, deploy-descriptor promotion/retrofit, and an MCP door
for AI agents. Published to Artifactory and consumed by the `orchestration-manifests` GitHub Actions.

> Design: `orchestration-manifests/docs/2026-06-10-control-m-gitops-design.md`.

## CLI — `ctmkit <surface> <verb> --options`

kubectl/gh-style surfaces with Rich output. Endpoints resolve from `--env` via
`config/environments.yaml` (`development` / `staging` / `production` / our private `lab`);
`--endpoint` overrides. API key comes from `$CTM_API_KEY` (HashiCorp Vault).

```bash
uv sync
uv run ctmkit --help

# validate manifests (JSON schema + nomenclature / site standard)
uv run ctmkit manifests validate --path /path/to/orchestration-manifests

# Automation API
export CTM_API_KEY=…
uv run ctmkit session login --env lab   --path /path/to/orchestration-manifests
uv run ctmkit build   run   --file …/0225_X.json --env lab --path …
uv run ctmkit deploy  plan  --app 0225 --env development --path …       # no network
uv run ctmkit deploy  run   --app 0225 --env lab --path … [--dry-run]
uv run ctmkit promote run   --app 0225 --from-env development --to-env staging --path …
```

## Architecture (modular, no god scripts)

- `ctmkit/aapi/` — typed client over the AAPI REST services (`session`, `build`, `deploy`,
  `transform`) on an injectable `httpx` client.
- `ctmkit/deploy/ordered.py` — ordered, one-file-at-a-time, fail-fast tree deploy.
- `ctmkit/promote/` — deploy-descriptor promotion / retrofit.
- `ctmkit/cli/` — one Typer sub-app per surface; shared Rich output in `cli/_console.py`.

## Develop

```bash
uv sync
uv run pytest          # every test is offline (httpx MockTransport / fixtures)
```
