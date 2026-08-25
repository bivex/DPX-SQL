import re
from typing import List
from .base import Rule
from ..code_model import CodeModel
from ..detection import Detection
from ..value_objects import PatternType, Confidence, SourceLocation, EvidenceItem


class StoredProcedureRouterRule(Rule):
    @property
    def name(self) -> str:
        return "STORED_PROCEDURE_ROUTER"

    def evaluate(self, model: CodeModel) -> List[Detection]:
        detections: List[Detection] = []
        for file in model.files:
            for fn in file.functions:
                loc = SourceLocation(file_path=file.file_path, line_number=fn.line_number)
                ev = EvidenceItem(
                    rule_name="SQL_STORED_PROCEDURE",
                    weight=0.92,
                    description=f"Function/Procedure '{fn.name}' ({fn.language}) encapsulates server-side business logic and return type '{fn.return_type}'",
                    location=loc,
                )
                detections.append(
                    Detection(
                        pattern_type=PatternType.STORED_PROCEDURE_ROUTER,
                        target_name=fn.name,
                        location=loc,
                        confidence=Confidence(0.92),
                        evidence=[ev],
                    )
                )
        return detections


class TriggerEventInterceptorRule(Rule):
    @property
    def name(self) -> str:
        return "TRIGGER_EVENT_INTERCEPTOR"

    def evaluate(self, model: CodeModel) -> List[Detection]:
        detections: List[Detection] = []
        for file in model.files:
            for trg in file.triggers:
                loc = SourceLocation(file_path=file.file_path, line_number=trg.line_number)
                ev = EvidenceItem(
                    rule_name="SQL_TRIGGER_INTERCEPTOR",
                    weight=0.95,
                    description=f"Trigger '{trg.name}' intercepts {trg.timing} {'/'.join(trg.events)} FOR EACH {trg.for_each} on table '{trg.table_name}'",
                    location=loc,
                )
                detections.append(
                    Detection(
                        pattern_type=PatternType.TRIGGER_EVENT_INTERCEPTOR,
                        target_name=trg.name,
                        location=loc,
                        confidence=Confidence(0.95),
                        evidence=[ev],
                    )
                )
        return detections


class TransactionIsolationGuardRule(Rule):
    @property
    def name(self) -> str:
        return "TRANSACTION_ISOLATION_GUARD"

    def evaluate(self, model: CodeModel) -> List[Detection]:
        detections: List[Detection] = []
        isolation_pattern = re.compile(
            r'\bset\s+transaction\s+isolation\s+level\s+(serializable|repeatable\s+read|read\s+committed)\b|\bselect\b.*?\bfor\s+(update|share|no\s+key\s+update)\b',
            re.IGNORECASE | re.DOTALL,
        )
        for file in model.files:
            for query in file.queries:
                if query.has_for_update or isolation_pattern.search(query.raw_text):
                    loc = SourceLocation(file_path=file.file_path, line_number=query.line_number)
                    ev = EvidenceItem(
                        rule_name="SQL_TRANSACTION_ISOLATION",
                        weight=0.92,
                        description="Explicit concurrency control and locking (SET TRANSACTION ISOLATION / SELECT FOR UPDATE)",
                        location=loc,
                    )
                    detections.append(
                        Detection(
                            pattern_type=PatternType.TRANSACTION_ISOLATION_GUARD,
                            target_name="ISOLATION_LOCK",
                            location=loc,
                            confidence=Confidence(0.92),
                            evidence=[ev],
                        )
                    )
        return detections


class AutonomousTransactionSavepointRule(Rule):
    @property
    def name(self) -> str:
        return "AUTONOMOUS_TRANSACTION_SAVEPOINT"

    def evaluate(self, model: CodeModel) -> List[Detection]:
        detections: List[Detection] = []
        savepoint_pattern = re.compile(r'\bsavepoint\s+\w+\b|\brollback\s+to\s+(savepoint\s+)?\w+\b|\brelease\s+savepoint\b', re.IGNORECASE)
        for file in model.files:
            for fn in file.functions:
                if fn.has_savepoint or savepoint_pattern.search(fn.body):
                    loc = SourceLocation(file_path=file.file_path, line_number=fn.line_number)
                    ev = EvidenceItem(
                        rule_name="SQL_SAVEPOINT_CHECKPOINT",
                        weight=0.90,
                        description=f"Routine '{fn.name}' implements granular rollback checkpoint using SAVEPOINT",
                        location=loc,
                    )
                    detections.append(
                        Detection(
                            pattern_type=PatternType.AUTONOMOUS_TRANSACTION_SAVEPOINT,
                            target_name=fn.name,
                            location=loc,
                            confidence=Confidence(0.90),
                            evidence=[ev],
                        )
                    )
        return detections
