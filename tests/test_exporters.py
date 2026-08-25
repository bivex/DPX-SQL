import os
import json
import pytest
from pattern_detector.domain.detection import Detection, DetectionReport
from pattern_detector.domain.value_objects import PatternType, Confidence, SourceLocation
from pattern_detector.adapters.outbound.exporters.html_hud_exporter import HtmlHudExporter
from pattern_detector.adapters.outbound.exporters.json_exporter import JsonExporter
from pattern_detector.adapters.outbound.exporters.markdown_exporter import MarkdownExporter
from pattern_detector.adapters.outbound.exporters.sarif_exporter import SarifExporter


def test_exporters(tmp_path):
    loc = SourceLocation("sample.sql", 12)
    d = Detection(
        pattern_type=PatternType.RECURSIVE_CTE_HIERARCHY,
        target_name="WITH_RECURSIVE",
        location=loc,
        confidence=Confidence(0.95),
    )
    report = DetectionReport(
        target_path="sample.sql",
        scanned_files_count=1,
        execution_time_seconds=0.005,
        detections=[d],
    )

    # 1. HTML HUD
    html_file = str(tmp_path / "hud.html")
    HtmlHudExporter().export(report, html_file)
    assert os.path.exists(html_file)
    with open(html_file, "r", encoding="utf-8") as f:
        content = f.read()
    assert "DPX-SQL" in content
    assert "WITH_RECURSIVE" in content

    # 2. JSON
    json_file = str(tmp_path / "report.json")
    JsonExporter().export(report, json_file)
    assert os.path.exists(json_file)
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["total_detections"] == 1

    # 3. Markdown
    md_file = str(tmp_path / "report.md")
    MarkdownExporter().export(report, md_file)
    assert os.path.exists(md_file)
    with open(md_file, "r", encoding="utf-8") as f:
        md_content = f.read()
    assert "# 🐘 DPX-SQL Analysis Report" in md_content

    # 4. SARIF
    sarif_file = str(tmp_path / "report.sarif")
    SarifExporter().export(report, sarif_file)
    assert os.path.exists(sarif_file)
    with open(sarif_file, "r", encoding="utf-8") as f:
        sarif_data = json.load(f)
    assert sarif_data["version"] == "2.1.0"
    assert len(sarif_data["runs"][0]["results"]) == 1
