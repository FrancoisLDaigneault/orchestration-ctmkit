"""Unit tests for the pure (no-network) helpers in ctmkit.docs.mirror."""
from ctmkit.docs import mirror

BASE = "https://documents.bmc.com/supportu/API/Monthly/en-US/Documentation/API_Intro.htm"
ALLOW = ["https://documents.bmc.com/supportu/API/Monthly/en-US/Documentation/"]


def test_extract_links_keeps_in_scope_htm_only():
    html = """
      <a href="API_Services_RunService.htm">services</a>
      <a href="#section">anchor</a>
      <a href="javascript:void(0)">js</a>
      <a href="https://example.com/other.htm">offsite</a>
      <a href="../images/diagram.png">image</a>
    """
    links = mirror.extract_links(html, BASE, ALLOW)
    assert links == [
        "https://documents.bmc.com/supportu/API/Monthly/en-US/Documentation/API_Services_RunService.htm"
    ]


def test_extract_links_dedupes_and_strips_fragments():
    html = '<a href="A.htm#x">a</a><a href="A.htm#y">a2</a>'
    links = mirror.extract_links(html, BASE, ALLOW)
    assert links == [
        "https://documents.bmc.com/supportu/API/Monthly/en-US/Documentation/A.htm"
    ]


def test_html_to_markdown_trims_to_breadcrumb_and_converts_headings():
    html = "<div>chrome junk</div>You are here:<h1>Deploy Descriptor</h1><p>Rules.</p>"
    out = mirror.html_to_markdown(html)
    assert "chrome junk" not in out
    assert "# Deploy Descriptor" in out
    assert "Rules." in out


def test_slug_for_uses_space_and_page_name():
    assert mirror.slug_for(BASE) == ("API", "API_Intro")
    saas = "https://documents.bmc.com/supportu/controlm-saas/en-US/Documentation/Integrations_Main.htm"
    assert mirror.slug_for(saas) == ("controlm-saas", "Integrations_Main")
