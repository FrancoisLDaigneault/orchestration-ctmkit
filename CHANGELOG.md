# Changelog

All notable changes to `ctmkit` are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **AAPI layer** (`aapi/`): session (api-key auth), build, deploy, transform over an
  injectable `httpx` client.
- **Deploy orchestration** (`deploy/ordered.py`): ordered, one-file-at-a-time, fail-fast.
- **Promotion** (`promote/`): deploy-descriptor promote/retrofit across environments.
- **Rich CLI** (`cli/`): `ctmkit <surface> <verb> --options` — `manifests`, `session`,
  `build`, `deploy`, `promote`. Endpoints resolve from `--env`.
- **Validation core** (`config`, `naming`, `schema`, `validate`): JSON schema + site-standard
  nomenclature for the manifests repo.

## [0.0.1] - 2026-06-10

- Initial project scaffold.
