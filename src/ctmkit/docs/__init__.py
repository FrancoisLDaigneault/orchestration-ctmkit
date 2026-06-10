"""BMC Control-M documentation mirror.

BMC's docs sit behind a Cloudflare challenge on several spaces. We defeat it with
``curl_cffi`` browser impersonation (real Chrome TLS/JA3 fingerprint) — no headless
browser, no Docker required — then convert each page to clean markdown.
"""
