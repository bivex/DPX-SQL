import os
import pytest
from typer.testing import CliRunner
from pattern_detector.adapters.inbound.cli.main import app

runner = CliRunner()


def test_cli_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "DPX-SQL" in result.stdout


def test_cli_catalog():
    result = runner.invoke(app, ["catalog"], env={"COLUMNS": "300"})
    assert result.exit_code == 0
    assert "recursive_cte_hierarchy" in result.stdout
    assert "sql_injection_dynamic_concat_hazard" in result.stdout


def test_cli_scan(tmp_path):
    sql_file = tmp_path / "test.sql"
    sql_file.write_text("""
    CREATE TABLE accounts (
        id BIGINT PRIMARY KEY,
        balance NUMERIC(18, 2) CHECK (balance >= 0)
    );
    CREATE INDEX idx_accounts_balance ON accounts (balance);
    """)

    html_out = str(tmp_path / "hud.html")
    json_out = str(tmp_path / "findings.json")

    result = runner.invoke(app, ["scan", str(tmp_path), "-H", html_out, "-J", json_out])
    assert result.exit_code == 0
    assert "DPX-SQL Analysis Complete" in result.stdout
    assert os.path.exists(html_out)
    assert os.path.exists(json_out)
