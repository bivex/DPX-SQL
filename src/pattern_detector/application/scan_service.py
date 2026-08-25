import os
from typing import List, Optional
from ..domain.detection import DetectionReport
from ..ports.inbound.parser_port import SqlParserPort
from ..ports.inbound.detector_port import PatternDetectorPort
from ..ports.outbound.exporter_port import ExporterPort


class ScanService:
    def __init__(
        self,
        parser: SqlParserPort,
        detector: PatternDetectorPort,
        html_exporter: Optional[ExporterPort] = None,
        json_exporter: Optional[ExporterPort] = None,
        markdown_exporter: Optional[ExporterPort] = None,
        sarif_exporter: Optional[ExporterPort] = None,
    ):
        self.parser = parser
        self.detector = detector
        self.html_exporter = html_exporter
        self.json_exporter = json_exporter
        self.markdown_exporter = markdown_exporter
        self.sarif_exporter = sarif_exporter

    def scan_path(
        self,
        target_path: str,
        html_output: Optional[str] = None,
        json_output: Optional[str] = None,
        markdown_output: Optional[str] = None,
        sarif_output: Optional[str] = None,
    ) -> DetectionReport:
        model = self.parser.parse_code_model([target_path])
        report = self.detector.detect(model)

        if html_output and self.html_exporter:
            self.html_exporter.export(report, html_output)

        if json_output and self.json_exporter:
            self.json_exporter.export(report, json_output)

        if markdown_output and self.markdown_exporter:
            self.markdown_exporter.export(report, markdown_output)

        if sarif_output and self.sarif_exporter:
            self.sarif_exporter.export(report, sarif_output)

        return report
