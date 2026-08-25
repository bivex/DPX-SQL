from typing import List
from .base import Rule
from ..code_model import CodeModel
from ..detection import Detection
from ..value_objects import PatternType, Confidence, SourceLocation, EvidenceItem


class PartialConditionalIndexRule(Rule):
    @property
    def name(self) -> str:
        return "PARTIAL_CONDITIONAL_INDEX"

    def evaluate(self, model: CodeModel) -> List[Detection]:
        detections: List[Detection] = []
        for file in model.files:
            for idx in file.indexes:
                if idx.is_partial and idx.where_clause:
                    loc = SourceLocation(file_path=file.file_path, line_number=idx.line_number)
                    ev = EvidenceItem(
                        rule_name="SQL_PARTIAL_INDEX",
                        weight=0.95,
                        description=f"Index '{idx.name}' on '{idx.table_name}' is a Partial Index with predicate: WHERE {idx.where_clause}",
                        location=loc,
                    )
                    detections.append(
                        Detection(
                            pattern_type=PatternType.PARTIAL_CONDITIONAL_INDEX,
                            target_name=idx.name,
                            location=loc,
                            confidence=Confidence(0.95),
                            evidence=[ev],
                        )
                    )
        return detections


class CoveringIndexIncludeRule(Rule):
    @property
    def name(self) -> str:
        return "COVERING_INDEX_INCLUDE"

    def evaluate(self, model: CodeModel) -> List[Detection]:
        detections: List[Detection] = []
        for file in model.files:
            for idx in file.indexes:
                if idx.includes:
                    loc = SourceLocation(file_path=file.file_path, line_number=idx.line_number)
                    ev = EvidenceItem(
                        rule_name="SQL_COVERING_INDEX",
                        weight=0.92,
                        description=f"Index '{idx.name}' on '{idx.table_name}' uses INCLUDE clause ({', '.join(idx.includes)}) enabling Index-Only Scans",
                        location=loc,
                    )
                    detections.append(
                        Detection(
                            pattern_type=PatternType.COVERING_INDEX_INCLUDE,
                            target_name=idx.name,
                            location=loc,
                            confidence=Confidence(0.92),
                            evidence=[ev],
                        )
                    )
        return detections


class GinGistSpecializedIndexRule(Rule):
    @property
    def name(self) -> str:
        return "GIN_GIST_SPECIALIZED_INDEX"

    def evaluate(self, model: CodeModel) -> List[Detection]:
        detections: List[Detection] = []
        for file in model.files:
            for idx in file.indexes:
                if idx.index_type.upper() in ["GIN", "GIST", "BRIN"]:
                    loc = SourceLocation(file_path=file.file_path, line_number=idx.line_number)
                    ev = EvidenceItem(
                        rule_name="SQL_SPECIALIZED_INDEX_TYPE",
                        weight=0.95,
                        description=f"Index '{idx.name}' on '{idx.table_name}' uses specialized access method {idx.index_type.upper()} for JSONB/array/geometry/full-text",
                        location=loc,
                    )
                    detections.append(
                        Detection(
                            pattern_type=PatternType.GIN_GIST_SPECIALIZED_INDEX,
                            target_name=idx.name,
                            location=loc,
                            confidence=Confidence(0.95),
                            evidence=[ev],
                        )
                    )
        return detections


class CompositeMultiColumnIndexRule(Rule):
    @property
    def name(self) -> str:
        return "COMPOSITE_MULTI_COLUMN_INDEX"

    def evaluate(self, model: CodeModel) -> List[Detection]:
        detections: List[Detection] = []
        for file in model.files:
            for idx in file.indexes:
                if len(idx.columns) >= 2:
                    loc = SourceLocation(file_path=file.file_path, line_number=idx.line_number)
                    ev = EvidenceItem(
                        rule_name="SQL_COMPOSITE_INDEX",
                        weight=0.90,
                        description=f"Index '{idx.name}' on '{idx.table_name}' is a composite multi-column index ({', '.join(idx.columns)})",
                        location=loc,
                    )
                    detections.append(
                        Detection(
                            pattern_type=PatternType.COMPOSITE_MULTI_COLUMN_INDEX,
                            target_name=idx.name,
                            location=loc,
                            confidence=Confidence(0.90),
                            evidence=[ev],
                        )
                    )
        return detections


class ForeignKeyCascadeTreeRule(Rule):
    @property
    def name(self) -> str:
        return "FOREIGN_KEY_CASCADE_TREE"

    def evaluate(self, model: CodeModel) -> List[Detection]:
        detections: List[Detection] = []
        for file in model.files:
            for tbl in file.tables:
                for fk in tbl.foreign_keys:
                    action = fk.get("on_delete", "").upper()
                    if "CASCADE" in action or "SET NULL" in action:
                        loc = SourceLocation(file_path=file.file_path, line_number=tbl.line_number)
                        ev = EvidenceItem(
                            rule_name="SQL_FK_CASCADE",
                            weight=0.90,
                            description=f"Table '{tbl.name}' defines referential integrity action {action} referencing '{fk.get('to_table')}'",
                            location=loc,
                        )
                        detections.append(
                            Detection(
                                pattern_type=PatternType.FOREIGN_KEY_CASCADE_TREE,
                                target_name=f"{tbl.name}->{fk.get('to_table')}",
                                location=loc,
                                confidence=Confidence(0.90),
                                evidence=[ev],
                            )
                        )
        return detections
