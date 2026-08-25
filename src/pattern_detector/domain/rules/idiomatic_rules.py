import re
from typing import List
from .base import Rule
from ..code_model import CodeModel
from ..detection import Detection
from ..value_objects import PatternType, Confidence, SourceLocation, EvidenceItem


class RecursiveCteHierarchyRule(Rule):
    @property
    def name(self) -> str:
        return "RECURSIVE_CTE_HIERARCHY"

    def evaluate(self, model: CodeModel) -> List[Detection]:
        detections: List[Detection] = []
        for file in model.files:
            for query in file.queries:
                if query.has_recursive_cte or re.search(r'\bwith\s+recursive\b', query.raw_text, re.IGNORECASE):
                    loc = SourceLocation(file_path=file.file_path, line_number=query.line_number)
                    ev = EvidenceItem(
                        rule_name="SQL_RECURSIVE_CTE",
                        weight=0.95,
                        description="Query utilizes WITH RECURSIVE CTE for hierarchical tree or graph traversal",
                        location=loc,
                    )
                    detections.append(
                        Detection(
                            pattern_type=PatternType.RECURSIVE_CTE_HIERARCHY,
                            target_name="WITH_RECURSIVE",
                            location=loc,
                            confidence=Confidence(0.95),
                            evidence=[ev],
                        )
                    )
        return detections


class WindowFunctionAnalyticsRule(Rule):
    @property
    def name(self) -> str:
        return "WINDOW_FUNCTION_ANALYTICS"

    def evaluate(self, model: CodeModel) -> List[Detection]:
        detections: List[Detection] = []
        window_pattern = re.compile(
            r'\b(row_number|rank|dense_rank|ntile|lag|lead|first_value|last_value|sum|avg|count)\s*\([^)]*\)\s+over\s*\(',
            re.IGNORECASE,
        )
        for file in model.files:
            for query in file.queries:
                if query.has_window_func or window_pattern.search(query.raw_text):
                    loc = SourceLocation(file_path=file.file_path, line_number=query.line_number)
                    ev = EvidenceItem(
                        rule_name="SQL_WINDOW_FUNCTION",
                        weight=0.92,
                        description="Query applies analytical Window Function (OVER PARTITION BY / ORDER BY)",
                        location=loc,
                    )
                    detections.append(
                        Detection(
                            pattern_type=PatternType.WINDOW_FUNCTION_ANALYTICS,
                            target_name="OVER()",
                            location=loc,
                            confidence=Confidence(0.92),
                            evidence=[ev],
                        )
                    )
        return detections


class UpsertMergeIdempotencyRule(Rule):
    @property
    def name(self) -> str:
        return "UPSERT_MERGE_IDEMPOTENCY"

    def evaluate(self, model: CodeModel) -> List[Detection]:
        detections: List[Detection] = []
        upsert_pattern = re.compile(
            r'\bon\s+conflict\b.*?\bdo\s+(update|nothing)\b|\bmerge\s+into\b',
            re.IGNORECASE | re.DOTALL,
        )
        for file in model.files:
            for query in file.queries:
                if query.has_upsert or upsert_pattern.search(query.raw_text):
                    loc = SourceLocation(file_path=file.file_path, line_number=query.line_number)
                    ev = EvidenceItem(
                        rule_name="SQL_UPSERT_MERGE",
                        weight=0.92,
                        description="Atomic upsert operation using ON CONFLICT DO UPDATE / MERGE INTO for idempotent mutations",
                        location=loc,
                    )
                    detections.append(
                        Detection(
                            pattern_type=PatternType.UPSERT_MERGE_IDEMPOTENCY,
                            target_name="UPSERT/MERGE",
                            location=loc,
                            confidence=Confidence(0.92),
                            evidence=[ev],
                        )
                    )
        return detections


class MaterializedViewCacheRule(Rule):
    @property
    def name(self) -> str:
        return "MATERIALIZED_VIEW_CACHE"

    def evaluate(self, model: CodeModel) -> List[Detection]:
        detections: List[Detection] = []
        for file in model.files:
            for view in file.views:
                if view.is_materialized:
                    loc = SourceLocation(file_path=file.file_path, line_number=view.line_number)
                    ev = EvidenceItem(
                        rule_name="SQL_MATERIALIZED_VIEW",
                        weight=0.90,
                        description=f"Materialized View '{view.name}' caches precomputed query results with physical storage",
                        location=loc,
                    )
                    detections.append(
                        Detection(
                            pattern_type=PatternType.MATERIALIZED_VIEW_CACHE,
                            target_name=view.name,
                            location=loc,
                            confidence=Confidence(0.90),
                            evidence=[ev],
                        )
                    )
        return detections


class LateralJoinSubqueryRule(Rule):
    @property
    def name(self) -> str:
        return "LATERAL_JOIN_SUBQUERY"

    def evaluate(self, model: CodeModel) -> List[Detection]:
        detections: List[Detection] = []
        lateral_pattern = re.compile(r'\b(cross|left|inner)?\s*join\s+lateral\b|\bcross\s+apply\b|\bouter\s+apply\b', re.IGNORECASE)
        for file in model.files:
            for query in file.queries:
                if query.has_lateral or lateral_pattern.search(query.raw_text):
                    loc = SourceLocation(file_path=file.file_path, line_number=query.line_number)
                    ev = EvidenceItem(
                        rule_name="SQL_LATERAL_JOIN",
                        weight=0.90,
                        description="Query evaluates correlated subquery per row using LATERAL join / APPLY syntax",
                        location=loc,
                    )
                    detections.append(
                        Detection(
                            pattern_type=PatternType.LATERAL_JOIN_SUBQUERY,
                            target_name="JOIN_LATERAL",
                            location=loc,
                            confidence=Confidence(0.90),
                            evidence=[ev],
                        )
                    )
        return detections


class TablePartitioningShardingRule(Rule):
    @property
    def name(self) -> str:
        return "TABLE_PARTITIONING_SHARDING"

    def evaluate(self, model: CodeModel) -> List[Detection]:
        detections: List[Detection] = []
        for file in model.files:
            for tbl in file.tables:
                if tbl.is_partitioned:
                    loc = SourceLocation(file_path=file.file_path, line_number=tbl.line_number)
                    ev = EvidenceItem(
                        rule_name="SQL_TABLE_PARTITION",
                        weight=0.92,
                        description=f"Table '{tbl.name}' implements Horizontal Partitioning by {tbl.partition_by or 'KEY'}",
                        location=loc,
                    )
                    detections.append(
                        Detection(
                            pattern_type=PatternType.TABLE_PARTITIONING_SHARDING,
                            target_name=tbl.name,
                            location=loc,
                            confidence=Confidence(0.92),
                            evidence=[ev],
                        )
                    )
        return detections
