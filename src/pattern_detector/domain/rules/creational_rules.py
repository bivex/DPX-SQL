import re
from typing import List
from .base import Rule
from ..code_model import CodeModel
from ..detection import Detection
from ..value_objects import PatternType, Confidence, SourceLocation, EvidenceItem


class FactorySequenceIdGeneratorRule(Rule):
    @property
    def name(self) -> str:
        return "FACTORY_SEQUENCE_ID_GENERATOR"

    def evaluate(self, model: CodeModel) -> List[Detection]:
        detections: List[Detection] = []
        for file in model.files:
            for seq in file.sequences:
                loc = SourceLocation(file_path=file.file_path, line_number=1)
                ev = EvidenceItem(
                    rule_name="CREATIONAL_FACTORY_SEQUENCE",
                    weight=0.90,
                    description=f"Factory pattern: Sequence '{seq}' generates monotonic unique identifiers",
                    location=loc,
                )
                detections.append(
                    Detection(
                        pattern_type=PatternType.FACTORY_SEQUENCE_ID_GENERATOR,
                        target_name=seq,
                        location=loc,
                        confidence=Confidence(0.90),
                        evidence=[ev],
                    )
                )
            for tbl in file.tables:
                for col in tbl.columns:
                    if col.default_value and ("nextval(" in col.default_value.lower() or "identity" in col.data_type.lower() or "auto_increment" in col.data_type.lower() or "gen_random_uuid()" in col.default_value.lower()):
                        loc = SourceLocation(file_path=file.file_path, line_number=tbl.line_number)
                        ev = EvidenceItem(
                            rule_name="CREATIONAL_FACTORY_IDENTITY",
                            weight=0.92,
                            description=f"Factory pattern: Column '{tbl.name}.{col.name}' uses Factory ID generator ({col.default_value or col.data_type})",
                            location=loc,
                        )
                        detections.append(
                            Detection(
                                pattern_type=PatternType.FACTORY_SEQUENCE_ID_GENERATOR,
                                target_name=f"{tbl.name}.{col.name}",
                                location=loc,
                                confidence=Confidence(0.92),
                                evidence=[ev],
                            )
                        )
        return detections


class BuilderDynamicQueryComposerRule(Rule):
    @property
    def name(self) -> str:
        return "BUILDER_DYNAMIC_QUERY_COMPOSER"

    def evaluate(self, model: CodeModel) -> List[Detection]:
        detections: List[Detection] = []
        builder_pattern = re.compile(r'\bformat\s*\(\s*[\'"][^\'"]*\%[sIIL]', re.IGNORECASE)
        for file in model.files:
            for fn in file.functions:
                if builder_pattern.search(fn.body) or ("_query :=" in fn.body and "||" in fn.body):
                    loc = SourceLocation(file_path=file.file_path, line_number=fn.line_number)
                    ev = EvidenceItem(
                        rule_name="CREATIONAL_BUILDER_QUERY_COMPOSER",
                        weight=0.88,
                        description=f"Builder pattern: Routine '{fn.name}' incrementally constructs dynamic SQL queries using format()/concatenation",
                        location=loc,
                    )
                    detections.append(
                        Detection(
                            pattern_type=PatternType.BUILDER_DYNAMIC_QUERY_COMPOSER,
                            target_name=fn.name,
                            location=loc,
                            confidence=Confidence(0.88),
                            evidence=[ev],
                        )
                    )
        return detections


class PrototypeRowClonerRule(Rule):
    @property
    def name(self) -> str:
        return "PROTOTYPE_ROW_CLONER"

    def evaluate(self, model: CodeModel) -> List[Detection]:
        detections: List[Detection] = []
        clone_pattern = re.compile(r'\binsert\s+into\s+\w+\s*(\([^)]*\))?\s*select\b', re.IGNORECASE)
        for file in model.files:
            for query in file.queries:
                if clone_pattern.search(query.raw_text):
                    loc = SourceLocation(file_path=file.file_path, line_number=query.line_number)
                    ev = EvidenceItem(
                        rule_name="CREATIONAL_PROTOTYPE_CLONER",
                        weight=0.88,
                        description="Prototype pattern: Cloning existing row prototypes via INSERT INTO ... SELECT",
                        location=loc,
                    )
                    detections.append(
                        Detection(
                            pattern_type=PatternType.PROTOTYPE_ROW_CLONER,
                            target_name="INSERT_SELECT",
                            location=loc,
                            confidence=Confidence(0.88),
                            evidence=[ev],
                        )
                    )
        return detections


class SingletonConfigParamTableRule(Rule):
    @property
    def name(self) -> str:
        return "SINGLETON_CONFIG_PARAM_TABLE"

    def evaluate(self, model: CodeModel) -> List[Detection]:
        detections: List[Detection] = []
        for file in model.files:
            for tbl in file.tables:
                name_lower = tbl.name.lower()
                is_singleton = False
                reason = ""
                
                # Check 1: single row constraint e.g. id = 1 or lock
                for c in tbl.check_constraints:
                    if "id = 1" in c.lower() or "singleton" in c.lower() or "is_singleton" in c.lower():
                        is_singleton = True
                        reason = f"constrained by CHECK ({c})"
                        break
                
                # Check 2: typical config/settings/parameter table
                if not is_singleton and any(k in name_lower for k in ["app_config", "system_settings", "global_parameters", "system_config"]):
                    is_singleton = True
                    reason = "dedicated system configuration table"
                
                if is_singleton:
                    loc = SourceLocation(file_path=file.file_path, line_number=tbl.line_number)
                    ev = EvidenceItem(
                        rule_name="CREATIONAL_SINGLETON_TABLE",
                        weight=0.92,
                        description=f"Singleton pattern: Table '{tbl.name}' manages global configuration state ({reason})",
                        location=loc,
                    )
                    detections.append(
                        Detection(
                            pattern_type=PatternType.SINGLETON_CONFIG_PARAM_TABLE,
                            target_name=tbl.name,
                            location=loc,
                            confidence=Confidence(0.92),
                            evidence=[ev],
                        )
                    )
        return detections


class AbstractFactorySchemaTenantRule(Rule):
    @property
    def name(self) -> str:
        return "ABSTRACT_FACTORY_SCHEMA_TENANT"

    def evaluate(self, model: CodeModel) -> List[Detection]:
        detections: List[Detection] = []
        factory_pattern = re.compile(r'\bcreate\s+schema\s+(if\s+not\s+exists\s+)?(tenant_|org_|client_)', re.IGNORECASE)
        for file in model.files:
            for fn in file.functions:
                if re.search(r'\bcreate\s+schema\b', fn.body, re.IGNORECASE) and re.search(r'\bclone|tenant|provision\b', fn.body, re.IGNORECASE):
                    loc = SourceLocation(file_path=file.file_path, line_number=fn.line_number)
                    ev = EvidenceItem(
                        rule_name="CREATIONAL_ABSTRACT_FACTORY_TENANT",
                        weight=0.88,
                        description=f"Abstract Factory pattern: Routine '{fn.name}' dynamically provisions multi-tenant schemas and tables",
                        location=loc,
                    )
                    detections.append(
                        Detection(
                            pattern_type=PatternType.ABSTRACT_FACTORY_SCHEMA_TENANT,
                            target_name=fn.name,
                            location=loc,
                            confidence=Confidence(0.88),
                            evidence=[ev],
                        )
                    )
        return detections
