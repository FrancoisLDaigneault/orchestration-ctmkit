from ctmkit.docs import refresh as R


class _Resp:
    def __init__(self, status, text=""):
        self.status_code = status
        self.text = text
        self.headers = {}


class _Session:
    def __init__(self, by_url):
        self.by_url = by_url
        self.calls = []

    def get(self, url, headers=None, timeout=None):
        self.calls.append((url, headers))
        return self.by_url[url]


def _page(tmp_path, rel, url, body="old"):
    p = tmp_path / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(f"<!-- source: {url} -->\n\n{body}\n", encoding="utf-8")
    return p


def test_source_url_and_if_modified_since(tmp_path):
    p = _page(tmp_path, "bmc/x.md", "https://h/x.htm")
    assert R.source_url(p.read_text()) == "https://h/x.htm"
    assert R.if_modified_since(p).endswith("GMT")


def test_refresh_skips_304_and_rewrites_200(tmp_path):
    _page(tmp_path, "bmc/a.md", "https://h/a.htm", "old-a")
    _page(tmp_path, "bmc/b.md", "https://h/b.htm", "old-b")
    session = _Session({
        "https://h/a.htm": _Resp(304),
        "https://h/b.htm": _Resp(200, "<p>fresh-b</p>"),
    })
    res = R.refresh(tmp_path, session, clean_fn=lambda html: html.replace("<p>", "").replace("</p>", ""))
    assert (res.updated, res.unchanged, res.errors) == (1, 1, 0)
    assert "fresh-b" in (tmp_path / "bmc/b.md").read_text()
    assert "old-a" in (tmp_path / "bmc/a.md").read_text()  # untouched
    # the conditional header was sent
    assert all("If-Modified-Since" in (h or {}) for _, h in session.calls)


def test_refresh_counts_blocked_as_error(tmp_path):
    _page(tmp_path, "bmc/c.md", "https://h/c.htm")
    session = _Session({"https://h/c.htm": _Resp(200, "Just a moment...")})
    res = R.refresh(tmp_path, session, clean_fn=lambda h: h)
    assert (res.updated, res.unchanged, res.errors) == (0, 0, 1)
