import re
from typing import List
from .base import Rule
from ..code_model import CodeModel
from ..detection import Detection
from ..value_objects import PatternType, Confidence, SourceLocation, EvidenceItem


class MonolithicProcedureSrpRule(Rule):
    @property
    def name(self) -> str:
        return "MONOLITHIC_PROCEDURE_SRP"

    def evaluate(self, model: CodeModel) -> List[Detection]:
        detections: List[Detection] = []
        for file in model.files:
            for fn in file.functions:
                if fn.lines_count >= 80:
                    loc = SourceLocation(file_path=file.file_path, line_number=fn.line_number)
                    ev = EvidenceItem(
                        rule_name="SOLID_SRP_MONOLITHIC_PROCEDURE",
                        weight=0.85,
                        description=f"Stored Procedure '{fn.name}' spans {fn.lines_count} lines (>80), indicating SRP violation and multiple responsibilities",
                        location=loc,
                    )
                    detections.append(
                        Detection(
                            pattern_type=PatternType.MONOLITHIC_PROCEDURE_SRP,
                            target_name=fn.name,
                            location=loc,
                            confidence=Confidence(0.85),
                            evidence=[ev],
                        )
                    )
        return detections


class WideTableGodSchemaSrpRule(Rule):
    @property
    def name(self) -> str:
        return "WIDE_TABLE_GOD_SCHEMA_SRP"

    def evaluate(self, model: CodeModel) -> List[Detection]:
        detections: List[Detection] = []
        for file in model.files:
            for tbl in file.tables:
                if tbl.column_count >= 25:
                    loc = SourceLocation(file_path=file.file_path, line_number=tbl.line_number)
                    ev = EvidenceItem(
                        rule_name="SOLID_SRP_WIDE_GOD_TABLE",
                        weight=0.85,
                        description=f"Table '{tbl.name}' defines {tbl.column_count} columns (>=25), indicating God Table anti-pattern and denormalization",
                        location=loc,
                    )
                    detections.append(
                        Detection(
                            pattern_type=PatternType.WIDE_TABLE_GOD_SCHEMA_SRP,
                            target_name=tbl.name,
                            location=loc,
                            confidence=Confidence(0.85),
                            evidence=[ev],
                        )
                    )
        return detections


class FatViewInterfaceIspRule(Rule):
    @property
    def name(self) -> str:
        return "FAT_VIEW_INTERFACE_ISP"

    def evaluate(self, model: CodeModel) -> List[Detection]:
        detections: List[Detection] = []
        for file in model.files:
            for view in file.views:
                join_count = len(re.findall(r'\bjoin\b', view.query_body, re.IGNORECASE))
                if join_count >= 6:
                    loc = SourceLocation(file_path=file.file_path, line_number=view.line_number)
                    ev = EvidenceItem(
                        rule_name="SOLID_ISP_FAT_VIEW",
                        weight=0.85,
                        description=f"View '{view.name}' joins {join_count} tables (>=6), violating Interface Segregation Principle",
                        location=loc,
                    )
                    detections.append(
                        Detection(
                            pattern_type=PatternType.FAT_VIEW_INTERFACE_ISP,
                            target_name=view.name,
                            location=loc,
                            confidence=Confidence(0.85),
                            evidence=[ev],
                        )
                    )
        return detections
