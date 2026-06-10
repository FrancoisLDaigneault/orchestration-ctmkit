# ctmkit

A Control-M library + CLI for Jobs-as-Code GitOps: deploy descriptors, site-standard
validation, safe ordered deploys, KPIs, and an MCP door for AI agents. Published to
Artifactory and consumed by the `orchestration-manifests` GitHub Actions.

> Design: see `orchestration-manifests/docs/2026-06-10-control-m-gitops-design.md`.
> This repo currently lands the first slice — the **BMC docs mirror**.

## Docs mirror

BMC's documentation sits behind a Cloudflare challenge on several spaces. `ctmkit.docs`
defeats it with `curl_cffi` browser impersonation (real Chrome TLS fingerprint — no
headless browser needed) and converts each page to clean markdown.

```bash
uv sync
uv run ctmkit-docs --out docs/reference/bmc           # gather the curated set
```

Edit `src/ctmkit/docs/sources.yaml` to add pages/seeds. A scheduled workflow
(`.github/workflows/refresh-docs.yml`) refreshes the mirror periodically.

## Develop

```bash
uv sync
uv run pytest          # unit tests (no network)
```
