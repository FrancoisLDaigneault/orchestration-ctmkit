# Security Policy

## Supported versions

The latest released minor version on `main` receives security fixes.

## Reporting a vulnerability

**Do not open a public issue for security problems.** Report vulnerabilities privately to the
maintainers via your internal security channel (or a private email to the repository owners).
Include a description, reproduction steps, and impact. We aim to acknowledge within 2 business
days and provide a remediation timeline.

## Handling of secrets

`ctmkit` never stores credentials in code or logs:

- The Automation API **API key** is read from the environment (`$CTM_API_KEY`), sourced from
  **HashiCorp Vault** in CI — never committed.
- In-manifest secrets are **references only** (`{"Secret": "<name>"}`); values live in
  Control-M Vault / CyberArk and are resolved at deploy time.
- Connection-profile schemas reject literal `Password` fields in committed JSON.

If you find a secret committed to history, rotate it immediately and notify the maintainers.
