import re
from typing import List
from .base import Rule
from ..code_model import CodeModel
from ..detection import Detection
from ..value_objects import PatternType, Confidence, SourceLocation, EvidenceItem


class SqlInjectionDynamicConcatHazardRule(Rule):
    @property
    def name(self) -> str:
        return "SQL_INJECTION_DYNAMIC_CONCAT_HAZARD"

    def evaluate(self, model: CodeModel) -> List[Detection]:
        detections: List[Detection] = []
        # Look for execute '... ' || var or execute query without quote_ident / %I or format
        unsafe_pattern = re.compile(r'\bexecute\s+[\'"].*?\|\|\s*\w+|\bexecute\s+query_str\b|\bsp_executesql\s+@\w+\s*\+\s*@\w+', re.IGNORECASE)
        for file in model.files:
            for fn in file.functions:
                # If function uses execute with string concatenation without quote_ident or format(%I)
                for line_idx, line in enumerate(fn.body.splitlines(), start=fn.line_number):
                    if unsafe_pattern.search(line) and not ("quote_ident" in line.lower() or "quote_literal" in line.lower() or "format(" in line.lower()):
                        loc = SourceLocation(file_path=file.file_path, line_number=line_idx)
                        ev = EvidenceItem(
                            rule_name="HAZARD_DYNAMIC_SQL_INJECTION",
                            weight=0.95,
                            description=f"Function '{fn.name}' executes dynamically concatenated SQL query without sanitization, risking SQL Injection",
                            location=loc,
                        )
                        detections.append(
                            Detection(
                                pattern_type=PatternType.SQL_INJECTION_DYNAMIC_CONCAT_HAZARD,
                                target_name=fn.name,
                                location=loc,
                                confidence=Confidence(0.95),
                                evidence=[ev],
                            )
                        )
        return detections


class MissingIndexForeignKeyHazardRule(Rule):
    @property
    def name(self) -> str:
        return "MISSING_INDEX_FOREIGN_KEY_HAZARD"

    def evaluate(self, model: CodeModel) -> List[Detection]:
        detections: List[Detection] = []
        for file in model.files:
            for tbl in file.tables:
                existing_indexes = model.get_indexes_for_table(tbl.name)
                indexed_leading_cols = set()
                for idx in existing_indexes:
                    if idx.columns:
                        indexed_leading_cols.add(idx.columns[0].lower())
                
                # Check FK columns
                for fk in tbl.foreign_keys:
                    from_col = fk.get("from_col", "").lower()
                    if from_col and from_col not in indexed_leading_cols and from_col not in [pk.lower() for pk in tbl.primary_keys]:
                        loc = SourceLocation(file_path=file.file_path, line_number=tbl.line_number)
                        ev = EvidenceItem(
                            rule_name="HAZARD_MISSING_FK_INDEX",
                            weight=0.88,
                            description=f"Foreign Key column '{tbl.name}.{from_col}' lacks an index, risking full table scans and table-level locking on DELETE",
                            location=loc,
                        )
                        detections.append(
                            Detection(
                                pattern_type=PatternType.MISSING_INDEX_FOREIGN_KEY_HAZARD,
                                target_name=f"{tbl.name}.{from_col}",
                                location=loc,
                                confidence=Confidence(0.88),
                                evidence=[ev],
                            )
                        )
        return detections


class NPlusOneCursorIterationHazardRule(Rule):
    @property
    def name(self) -> str:
        return "N_PLUS_ONE_CURSOR_ITERATION_HAZARD"

    def evaluate(self, model: CodeModel) -> List[Detection]:
        detections: List[Detection] = []
        for file in model.files:
            for fn in file.functions:
                # If function has cursor and executes select/insert/update inside loop
                has_cursor_loop = bool(re.search(r'\bfor\s+\w+\s+in\b|\bfetch\s+next\b', fn.body, re.IGNORECASE))
                has_nested_mutation = bool(re.search(r'\b(insert\s+into|update\s+\w+|delete\s+from)\b', fn.body, re.IGNORECASE))
                if has_cursor_loop and has_nested_mutation:
                    loc = SourceLocation(file_path=file.file_path, line_number=fn.line_number)
                    ev = EvidenceItem(
                        rule_name="HAZARD_RBAR_CURSOR_LOOP",
                        weight=0.90,
                        description=f"Routine '{fn.name}' performs row-by-row mutations inside cursor loop (RBAR Anti-Pattern); rewrite as set-based bulk operation",
                        location=loc,
                    )
                    detections.append(
                        Detection(
                            pattern_type=PatternType.N_PLUS_ONE_CURSOR_ITERATION_HAZARD,
                            target_name=fn.name,
                            location=loc,
                            confidence=Confidence(0.90),
                            evidence=[ev],
                        )
                    )
        return detections


class UnboundedSelectStarHazardRule(Rule):
    @property
    def name(self) -> str:
        return "UNBOUNDED_SELECT_STAR_HAZARD"

    def evaluate(self, model: CodeModel) -> List[Detection]:
        detections: List[Detection] = []
        for file in model.files:
            for view in file.views:
                if re.search(r'\bselect\s+\*\s+from\b', view.query_body, re.IGNORECASE):
                    loc = SourceLocation(file_path=file.file_path, line_number=view.line_number)
                    ev = EvidenceItem(
                        rule_name="HAZARD_SELECT_STAR_VIEW",
                        weight=0.85,
                        description=f"View '{view.name}' uses 'SELECT *' risking schema drift breakage and excessive IO",
                        location=loc,
                    )
                    detections.append(
                        Detection(
                            pattern_type=PatternType.UNBOUNDED_SELECT_STAR_HAZARD,
                            target_name=view.name,
                            location=loc,
                            confidence=Confidence(0.85),
                            evidence=[ev],
                        )
                    )
            for fn in file.functions:
                if re.search(r'\bselect\s+\*\s+from\b', fn.body, re.IGNORECASE):
                    loc = SourceLocation(file_path=file.file_path, line_number=fn.line_number)
                    ev = EvidenceItem(
                        rule_name="HAZARD_SELECT_STAR_PROCEDURE",
                        weight=0.85,
                        description=f"Routine '{fn.name}' queries with 'SELECT *' risking column alignment errors",
                        location=loc,
                    )
                    detections.append(
                        Detection(
                            pattern_type=PatternType.UNBOUNDED_SELECT_STAR_HAZARD,
                            target_name=fn.name,
                            location=loc,
                            confidence=Confidence(0.85),
                            evidence=[ev],
                        )
                    )
        return detections


class DeadlockProneLockOrderingHazardRule(Rule):
    @property
    def name(self) -> str:
        return "DEADLOCK_PRONE_LOCK_ORDERING_HAZARD"

    def evaluate(self, model: CodeModel) -> List[Detection]:
        detections: List[Detection] = []
        for file in model.files:
            for query in file.queries:
                if query.has_for_update and not query.has_order_by:
                    loc = SourceLocation(file_path=file.file_path, line_number=query.line_number)
                    ev = EvidenceItem(
                        rule_name="HAZARD_UNORDERED_FOR_UPDATE",
                        weight=0.88,
                        description="SELECT FOR UPDATE statement without ORDER BY risks deadlocks under concurrent execution",
                        location=loc,
                    )
                    detections.append(
                        Detection(
                            pattern_type=PatternType.DEADLOCK_PRONE_LOCK_ORDERING_HAZARD,
                            target_name="FOR_UPDATE",
                            location=loc,
                            confidence=Confidence(0.88),
                            evidence=[ev],
                        )
                    )
        return detections


class ImplicitTypeCastingIndexHazardRule(Rule):
    @property
    def name(self) -> str:
        return "IMPLICIT_TYPE_CASTING_INDEX_HAZARD"

    def evaluate(self, model: CodeModel) -> List[Detection]:
        detections: List[Detection] = []
        func_where_pattern = re.compile(
            r'\bwhere\s+.*?\b(lower|upper|date|to_char|cast|substring|trim)\s*\(\s*(\w+)\s*\)',
            re.IGNORECASE | re.DOTALL,
        )
        for file in model.files:
            for query in file.queries:
                match = func_where_pattern.search(query.raw_text)
                if match:
                    func_name = match.group(1).upper()
                    col_name = match.group(2)
                    loc = SourceLocation(file_path=file.file_path, line_number=query.line_number)
                    ev = EvidenceItem(
                        rule_name="HAZARD_FUNCTION_ON_INDEX_COLUMN",
                        weight=0.85,
                        description=f"Predicate applies {func_name}({col_name}) in WHERE clause, preventing standard B-tree index usage unless a functional index exists",
                        location=loc,
                    )
                    detections.append(
                        Detection(
                            pattern_type=PatternType.IMPLICIT_TYPE_CASTING_INDEX_HAZARD,
                            target_name=f"{func_name}({col_name})",
                            location=loc,
                            confidence=Confidence(0.85),
                            evidence=[ev],
                        )
                    )
        return detections
