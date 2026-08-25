import re
from typing import List
from .base import Rule
from ..code_model import CodeModel
from ..detection import Detection
from ..value_objects import PatternType, Confidence, SourceLocation, EvidenceItem


class ChainOfResponsibilityTriggerPipelineRule(Rule):
    @property
    def name(self) -> str:
        return "CHAIN_OF_RESPONSIBILITY_TRIGGER_PIPELINE"

    def evaluate(self, model: CodeModel) -> List[Detection]:
        detections: List[Detection] = []
        table_triggers: dict = {}
        for file in model.files:
            for trg in file.triggers:
                table_triggers.setdefault(trg.table_name.lower(), []).append(trg)
        for tbl_name, trgs in table_triggers.items():
            if len(trgs) >= 2:
                loc = SourceLocation(file_path=model.files[0].file_path if model.files else "", line_number=trgs[0].line_number)
                ev = EvidenceItem(
                    rule_name="BEHAVIORAL_CHAIN_TRIGGER_PIPELINE",
                    weight=0.90,
                    description=f"Chain of Responsibility: Table '{tbl_name}' chains {len(trgs)} sequential triggers ({', '.join(t.name for t in trgs)})",
                    location=loc,
                )
                detections.append(
                    Detection(
                        pattern_type=PatternType.CHAIN_OF_RESPONSIBILITY_TRIGGER_PIPELINE,
                        target_name=tbl_name,
                        location=loc,
                        confidence=Confidence(0.90),
                        evidence=[ev],
                    )
                )
        return detections


class CommandActionQueueTableRule(Rule):
    @property
    def name(self) -> str:
        return "COMMAND_ACTION_QUEUE_TABLE"

    def evaluate(self, model: CodeModel) -> List[Detection]:
        detections: List[Detection] = []
        for file in model.files:
            for tbl in file.tables:
                if any(k in tbl.name.lower() for k in ["outbox", "job_queue", "tasks", "task_queue", "event_queue", "command_log", "work_queue"]):
                    loc = SourceLocation(file_path=file.file_path, line_number=tbl.line_number)
                    ev = EvidenceItem(
                        rule_name="BEHAVIORAL_COMMAND_QUEUE",
                        weight=0.92,
                        description=f"Command pattern: Table '{tbl.name}' implements Transactional Outbox / Command Queue for asynchronous processing",
                        location=loc,
                    )
                    detections.append(
                        Detection(
                            pattern_type=PatternType.COMMAND_ACTION_QUEUE_TABLE,
                            target_name=tbl.name,
                            location=loc,
                            confidence=Confidence(0.92),
                            evidence=[ev],
                        )
                    )
        return detections


class InterpreterDynamicSqlEvalRule(Rule):
    @property
    def name(self) -> str:
        return "INTERPRETER_DYNAMIC_SQL_EVAL"

    def evaluate(self, model: CodeModel) -> List[Detection]:
        detections: List[Detection] = []
        for file in model.files:
            for fn in file.functions:
                if fn.has_dynamic_exec or re.search(r'\bexecute\s+format\s*\(|\bsp_executesql\b|\bexecute\s+immediate\b', fn.body, re.IGNORECASE):
                    loc = SourceLocation(file_path=file.file_path, line_number=fn.line_number)
                    ev = EvidenceItem(
                        rule_name="BEHAVIORAL_INTERPRETER_DYNAMIC_SQL",
                        weight=0.88,
                        description=f"Interpreter pattern: Routine '{fn.name}' dynamically interprets and executes parameterized SQL AST at runtime",
                        location=loc,
                    )
                    detections.append(
                        Detection(
                            pattern_type=PatternType.INTERPRETER_DYNAMIC_SQL_EVAL,
                            target_name=fn.name,
                            location=loc,
                            confidence=Confidence(0.88),
                            evidence=[ev],
                        )
                    )
        return detections


class IteratorCursorFetchLoopRule(Rule):
    @property
    def name(self) -> str:
        return "ITERATOR_CURSOR_FETCH_LOOP"

    def evaluate(self, model: CodeModel) -> List[Detection]:
        detections: List[Detection] = []
        for file in model.files:
            for fn in file.functions:
                if fn.has_cursor or re.search(r'\bcursor\s+for\b|\bfetch\s+(next|prior|first|last)\b|\bfor\s+\w+\s+in\s+select\b', fn.body, re.IGNORECASE):
                    loc = SourceLocation(file_path=file.file_path, line_number=fn.line_number)
                    ev = EvidenceItem(
                        rule_name="BEHAVIORAL_ITERATOR_CURSOR",
                        weight=0.92,
                        description=f"Iterator pattern: Routine '{fn.name}' sequentially iterates over query records via cursor fetch loop",
                        location=loc,
                    )
                    detections.append(
                        Detection(
                            pattern_type=PatternType.ITERATOR_CURSOR_FETCH_LOOP,
                            target_name=fn.name,
                            location=loc,
                            confidence=Confidence(0.92),
                            evidence=[ev],
                        )
                    )
        return detections


class MediatorPubsubNotifyRule(Rule):
    @property
    def name(self) -> str:
        return "MEDIATOR_PUBSUB_NOTIFY"

    def evaluate(self, model: CodeModel) -> List[Detection]:
        detections: List[Detection] = []
        for file in model.files:
            for fn in file.functions:
                if re.search(r'\bpg_notify\s*\(|\bnotify\s+\w+', fn.body, re.IGNORECASE):
                    loc = SourceLocation(file_path=file.file_path, line_number=fn.line_number)
                    ev = EvidenceItem(
                        rule_name="BEHAVIORAL_MEDIATOR_NOTIFY",
                        weight=0.92,
                        description=f"Mediator pattern: Routine '{fn.name}' publishes messages to decoupled event bus via LISTEN/NOTIFY channel",
                        location=loc,
                    )
                    detections.append(
                        Detection(
                            pattern_type=PatternType.MEDIATOR_PUBSUB_NOTIFY,
                            target_name=fn.name,
                            location=loc,
                            confidence=Confidence(0.92),
                            evidence=[ev],
                        )
                    )
        return detections


class MementoPointInTimeFlashbackRule(Rule):
    @property
    def name(self) -> str:
        return "MEMENTO_POINT_IN_TIME_FLASHBACK"

    def evaluate(self, model: CodeModel) -> List[Detection]:
        detections: List[Detection] = []
        for file in model.files:
            for tbl in file.tables:
                col_names = [c.name.lower() for c in tbl.columns]
                has_temporal = (
                    any("valid_from" in c or "sys_start" in c or "effective_date" in c for c in col_names)
                    and any("valid_to" in c or "sys_end" in c or "expiry_date" in c for c in col_names)
                )
                if has_temporal or "system_time" in tbl.name.lower() or "temporal" in tbl.name.lower():
                    loc = SourceLocation(file_path=file.file_path, line_number=tbl.line_number)
                    ev = EvidenceItem(
                        rule_name="BEHAVIORAL_MEMENTO_TEMPORAL",
                        weight=0.92,
                        description=f"Memento pattern: Table '{tbl.name}' implements Temporal / System-Versioned history tracking",
                        location=loc,
                    )
                    detections.append(
                        Detection(
                            pattern_type=PatternType.MEMENTO_POINT_IN_TIME_FLASHBACK,
                            target_name=tbl.name,
                            location=loc,
                            confidence=Confidence(0.92),
                            evidence=[ev],
                        )
                    )
        return detections


class ObserverTriggerAuditBroadcastRule(Rule):
    @property
    def name(self) -> str:
        return "OBSERVER_TRIGGER_AUDIT_BROADCAST"

    def evaluate(self, model: CodeModel) -> List[Detection]:
        detections: List[Detection] = []
        for file in model.files:
            for trg in file.triggers:
                if trg.timing.upper() == "AFTER" and ("INSERT" in trg.events or "UPDATE" in trg.events or "DELETE" in trg.events):
                    loc = SourceLocation(file_path=file.file_path, line_number=trg.line_number)
                    ev = EvidenceItem(
                        rule_name="BEHAVIORAL_OBSERVER_TRIGGER",
                        weight=0.92,
                        description=f"Observer pattern: AFTER trigger '{trg.name}' on '{trg.table_name}' notifies downstream subscribers",
                        location=loc,
                    )
                    detections.append(
                        Detection(
                            pattern_type=PatternType.OBSERVER_TRIGGER_AUDIT_BROADCAST,
                            target_name=trg.name,
                            location=loc,
                            confidence=Confidence(0.92),
                            evidence=[ev],
                        )
                    )
        return detections


class StateMachineStatusConstraintRule(Rule):
    @property
    def name(self) -> str:
        return "STATE_MACHINE_STATUS_CONSTRAINT"

    def evaluate(self, model: CodeModel) -> List[Detection]:
        detections: List[Detection] = []
        for file in model.files:
            for tbl in file.tables:
                for c in tbl.check_constraints:
                    if "status in (" in c.lower() or "state in (" in c.lower() or "status =" in c.lower():
                        loc = SourceLocation(file_path=file.file_path, line_number=tbl.line_number)
                        ev = EvidenceItem(
                            rule_name="BEHAVIORAL_STATE_MACHINE_CHECK",
                            weight=0.90,
                            description=f"State pattern: Table '{tbl.name}' enforces valid state transitions via CHECK constraint ({c})",
                            location=loc,
                        )
                        detections.append(
                            Detection(
                                pattern_type=PatternType.STATE_MACHINE_STATUS_CONSTRAINT,
                                target_name=tbl.name,
                                location=loc,
                                confidence=Confidence(0.90),
                                evidence=[ev],
                            )
                        )
        return detections


class StrategyDynamicPartitionPruningRule(Rule):
    @property
    def name(self) -> str:
        return "STRATEGY_DYNAMIC_PARTITION_PRUNING"

    def evaluate(self, model: CodeModel) -> List[Detection]:
        detections: List[Detection] = []
        for file in model.files:
            for tbl in file.tables:
                if tbl.is_partitioned and tbl.partition_by:
                    loc = SourceLocation(file_path=file.file_path, line_number=tbl.line_number)
                    ev = EvidenceItem(
                        rule_name="BEHAVIORAL_STRATEGY_PRUNING",
                        weight=0.88,
                        description=f"Strategy pattern: Partition strategy '{tbl.partition_by}' dynamically directs queries to physical sub-tables",
                        location=loc,
                    )
                    detections.append(
                        Detection(
                            pattern_type=PatternType.STRATEGY_DYNAMIC_PARTITION_PRUNING,
                            target_name=tbl.name,
                            location=loc,
                            confidence=Confidence(0.88),
                            evidence=[ev],
                        )
                    )
        return detections


class TemplateMethodProceduralSchemaRule(Rule):
    @property
    def name(self) -> str:
        return "TEMPLATE_METHOD_PROCEDURAL_SCHEMA"

    def evaluate(self, model: CodeModel) -> List[Detection]:
        detections: List[Detection] = []
        for file in model.files:
            for fn in file.functions:
                if "begin" in fn.body.lower() and "exception" in fn.body.lower() and "when others" in fn.body.lower():
                    loc = SourceLocation(file_path=file.file_path, line_number=fn.line_number)
                    ev = EvidenceItem(
                        rule_name="BEHAVIORAL_TEMPLATE_METHOD_PROCEDURE",
                        weight=0.90,
                        description=f"Template Method pattern: Routine '{fn.name}' follows canonical structure (BEGIN -> EXECUTE -> EXCEPTION WHEN)",
                        location=loc,
                    )
                    detections.append(
                        Detection(
                            pattern_type=PatternType.TEMPLATE_METHOD_PROCEDURAL_SCHEMA,
                            target_name=fn.name,
                            location=loc,
                            confidence=Confidence(0.90),
                            evidence=[ev],
                        )
                    )
        return detections


class VisitorRecursiveTreeScanRule(Rule):
    @property
    def name(self) -> str:
        return "VISITOR_RECURSIVE_TREE_SCAN"

    def evaluate(self, model: CodeModel) -> List[Detection]:
        detections: List[Detection] = []
        for file in model.files:
            for query in file.queries:
                if query.has_recursive_cte and any(k in query.raw_text.lower() for k in ["path", "level", "depth", "visited"]):
                    loc = SourceLocation(file_path=file.file_path, line_number=query.line_number)
                    ev = EvidenceItem(
                        rule_name="BEHAVIORAL_VISITOR_RECURSIVE_SCAN",
                        weight=0.90,
                        description="Visitor pattern: Recursive query traverses hierarchical graph accumulating path/depth metadata",
                        location=loc,
                    )
                    detections.append(
                        Detection(
                            pattern_type=PatternType.VISITOR_RECURSIVE_TREE_SCAN,
                            target_name="RECURSIVE_VISITOR",
                            location=loc,
                            confidence=Confidence(0.90),
                            evidence=[ev],
                        )
                    )
        return detections
