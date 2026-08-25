import re
from typing import List
from .base import Rule
from ..code_model import CodeModel
from ..detection import Detection
from ..value_objects import PatternType, Confidence, SourceLocation, EvidenceItem


class AdapterForeignDataWrapperRule(Rule):
    @property
    def name(self) -> str:
        return "ADAPTER_FOREIGN_DATA_WRAPPER"

    def evaluate(self, model: CodeModel) -> List[Detection]:
        detections: List[Detection] = []
        fdw_pattern = re.compile(
            r'\bcreate\s+foreign\s+table\b|\bimport\s+foreign\s+schema\b|\bcreate\s+server\b.*?\bforeign\s+data\s+wrapper\b',
            re.IGNORECASE | re.DOTALL,
        )
        for file in model.files:
            if fdw_pattern.search(file.raw_content):
                loc = SourceLocation(file_path=file.file_path, line_number=1)
                ev = EvidenceItem(
                    rule_name="STRUCTURAL_ADAPTER_FDW",
                    weight=0.92,
                    description="Adapter pattern: Foreign Data Wrapper (FDW) adapts external database schemas to relational tables",
                    location=loc,
                )
                detections.append(
                    Detection(
                        pattern_type=PatternType.ADAPTER_FOREIGN_DATA_WRAPPER,
                        target_name="FDW_SERVER",
                        location=loc,
                        confidence=Confidence(0.92),
                        evidence=[ev],
                    )
                )
        return detections


class BridgePolymorphicJunctionRule(Rule):
    @property
    def name(self) -> str:
        return "BRIDGE_POLYMORPHIC_JUNCTION"

    def evaluate(self, model: CodeModel) -> List[Detection]:
        detections: List[Detection] = []
        for file in model.files:
            for tbl in file.tables:
                col_names = [c.name.lower() for c in tbl.columns]
                has_type = any("type" in c or "target_type" in c or "entity_type" in c or "owner_type" in c for c in col_names)
                has_id = any("id" in c or "target_id" in c or "entity_id" in c or "owner_id" in c for c in col_names)
                if has_type and has_id and any(c.endswith("_id") for c in col_names):
                    loc = SourceLocation(file_path=file.file_path, line_number=tbl.line_number)
                    ev = EvidenceItem(
                        rule_name="STRUCTURAL_BRIDGE_POLYMORPHIC",
                        weight=0.88,
                        description=f"Bridge pattern: Table '{tbl.name}' implements polymorphic relation decoupling target types and identifiers",
                        location=loc,
                    )
                    detections.append(
                        Detection(
                            pattern_type=PatternType.BRIDGE_POLYMORPHIC_JUNCTION,
                            target_name=tbl.name,
                            location=loc,
                            confidence=Confidence(0.88),
                            evidence=[ev],
                        )
                    )
        return detections


class CompositeHierarchicalTreeRule(Rule):
    @property
    def name(self) -> str:
        return "COMPOSITE_HIERARCHICAL_TREE"

    def evaluate(self, model: CodeModel) -> List[Detection]:
        detections: List[Detection] = []
        for file in model.files:
            for tbl in file.tables:
                is_self_ref = False
                col_name = ""
                for fk in tbl.foreign_keys:
                    if fk.get("to_table", "").lower() == tbl.name.lower():
                        is_self_ref = True
                        col_name = fk.get("from_col", "parent_id")
                        break
                if not is_self_ref:
                    for col in tbl.columns:
                        if col.name.lower() in ["parent_id", "parent_category_id", "parent_org_id", "ancestor_id"]:
                            is_self_ref = True
                            col_name = col.name
                            break
                if is_self_ref:
                    loc = SourceLocation(file_path=file.file_path, line_number=tbl.line_number)
                    ev = EvidenceItem(
                        rule_name="STRUCTURAL_COMPOSITE_TREE",
                        weight=0.92,
                        description=f"Composite pattern: Table '{tbl.name}' models hierarchical parent-child trees via self-reference '{col_name}'",
                        location=loc,
                    )
                    detections.append(
                        Detection(
                            pattern_type=PatternType.COMPOSITE_HIERARCHICAL_TREE,
                            target_name=tbl.name,
                            location=loc,
                            confidence=Confidence(0.92),
                            evidence=[ev],
                        )
                    )
        return detections


class DecoratorComputedAuditLogRule(Rule):
    @property
    def name(self) -> str:
        return "DECORATOR_COMPUTED_AUDIT_LOG"

    def evaluate(self, model: CodeModel) -> List[Detection]:
        detections: List[Detection] = []
        for file in model.files:
            for trg in file.triggers:
                if any(k in trg.name.lower() for k in ["audit", "log", "history", "timestamp", "version"]):
                    loc = SourceLocation(file_path=file.file_path, line_number=trg.line_number)
                    ev = EvidenceItem(
                        rule_name="STRUCTURAL_DECORATOR_AUDIT",
                        weight=0.95,
                        description=f"Decorator pattern: Trigger '{trg.name}' decorates mutations on '{trg.table_name}' with automated audit/timestamp capture",
                        location=loc,
                    )
                    detections.append(
                        Detection(
                            pattern_type=PatternType.DECORATOR_COMPUTED_AUDIT_LOG,
                            target_name=trg.name,
                            location=loc,
                            confidence=Confidence(0.95),
                            evidence=[ev],
                        )
                    )
        return detections


class FacadeReportingViewRule(Rule):
    @property
    def name(self) -> str:
        return "FACADE_REPORTING_VIEW"

    def evaluate(self, model: CodeModel) -> List[Detection]:
        detections: List[Detection] = []
        for file in model.files:
            for view in file.views:
                join_count = len(re.findall(r'\bjoin\b', view.query_body, re.IGNORECASE))
                if join_count >= 2:
                    loc = SourceLocation(file_path=file.file_path, line_number=view.line_number)
                    ev = EvidenceItem(
                        rule_name="STRUCTURAL_FACADE_VIEW",
                        weight=0.90,
                        description=f"Facade pattern: View '{view.name}' provides simplified interface over {join_count} relational joins",
                        location=loc,
                    )
                    detections.append(
                        Detection(
                            pattern_type=PatternType.FACADE_REPORTING_VIEW,
                            target_name=view.name,
                            location=loc,
                            confidence=Confidence(0.90),
                            evidence=[ev],
                        )
                    )
        return detections


class FlyweightLookupDictionaryRule(Rule):
    @property
    def name(self) -> str:
        return "FLYWEIGHT_LOOKUP_DICTIONARY"

    def evaluate(self, model: CodeModel) -> List[Detection]:
        detections: List[Detection] = []
        for file in model.files:
            for tbl in file.tables:
                col_names = [c.name.lower() for c in tbl.columns]
                is_lookup = False
                if len(tbl.columns) in [2, 3] and any("code" in c or "name" in c or "slug" in c for c in col_names) and any("id" in c for c in col_names):
                    if any(k in tbl.name.lower() for k in ["status", "type", "category", "enum", "role", "currency", "country", "dict"]):
                        is_lookup = True
                if is_lookup:
                    loc = SourceLocation(file_path=file.file_path, line_number=tbl.line_number)
                    ev = EvidenceItem(
                        rule_name="STRUCTURAL_FLYWEIGHT_DICTIONARY",
                        weight=0.90,
                        description=f"Flyweight pattern: Table '{tbl.name}' serves as a shared lookup dictionary for constant values",
                        location=loc,
                    )
                    detections.append(
                        Detection(
                            pattern_type=PatternType.FLYWEIGHT_LOOKUP_DICTIONARY,
                            target_name=tbl.name,
                            location=loc,
                            confidence=Confidence(0.90),
                            evidence=[ev],
                        )
                    )
        return detections


class ProxyStagedLandingTableRule(Rule):
    @property
    def name(self) -> str:
        return "PROXY_STAGED_LANDING_TABLE"

    def evaluate(self, model: CodeModel) -> List[Detection]:
        detections: List[Detection] = []
        for file in model.files:
            for tbl in file.tables:
                if tbl.is_unlogged or tbl.is_temporary or any(k in tbl.name.lower() for k in ["stg_", "staging_", "raw_", "tmp_", "landing_"]):
                    loc = SourceLocation(file_path=file.file_path, line_number=tbl.line_number)
                    ev = EvidenceItem(
                        rule_name="STRUCTURAL_PROXY_STAGING",
                        weight=0.88,
                        description=f"Proxy pattern: Table '{tbl.name}' acts as a transient staging / ingestion buffer",
                        location=loc,
                    )
                    detections.append(
                        Detection(
                            pattern_type=PatternType.PROXY_STAGED_LANDING_TABLE,
                            target_name=tbl.name,
                            location=loc,
                            confidence=Confidence(0.88),
                            evidence=[ev],
                        )
                    )
        return detections
