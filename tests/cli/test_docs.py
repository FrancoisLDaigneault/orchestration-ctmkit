from typer.testing import CliRunner

from ctmkit.cli import app

runner = CliRunner()


def test_docs_help_lists_crawl_and_mirror():
    result = runner.invoke(app, ["docs", "--help"])
    assert result.exit_code == 0
    assert "crawl" in result.output and "mirror" in result.output
