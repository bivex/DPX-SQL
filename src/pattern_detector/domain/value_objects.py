from enum import Enum
from dataclasses import dataclass
from typing import Optional


class PatternCategory(str, Enum):
    SQL_IDIOMATIC_OPTIMIZATION = "sql_idiomatic_optimization"
    RELATIONAL_INDEXING_SCHEMA = "relational_indexing_schema"
    PROCEDURAL_TRANSACTION_CONTROL = "procedural_transaction_control"
    CREATIONAL = "creational"
    STRUCTURAL = "structural"
    BEHAVIORAL = "behavioral"
    SQL_SECURITY_HAZARDS = "sql_security_hazards"
    SOLID_PRINCIPLES = "solid_principles"


class PatternType(str, Enum):
    # SQL Idiomatic & Query Optimization
    RECURSIVE_CTE_HIERARCHY = "recursive_cte_hierarchy"
    WINDOW_FUNCTION_ANALYTICS = "window_function_analytics"
    UPSERT_MERGE_IDEMPOTENCY = "upsert_merge_idempotency"
    MATERIALIZED_VIEW_CACHE = "materialized_view_cache"
    LATERAL_JOIN_SUBQUERY = "lateral_join_subquery"
    TABLE_PARTITIONING_SHARDING = "table_partitioning_sharding"

    # Relational Indexing & Schema Design
    PARTIAL_CONDITIONAL_INDEX = "partial_conditional_index"
    COVERING_INDEX_INCLUDE = "covering_index_include"
    GIN_GIST_SPECIALIZED_INDEX = "gin_gist_specialized_index"
    COMPOSITE_MULTI_COLUMN_INDEX = "composite_multi_column_index"
    FOREIGN_KEY_CASCADE_TREE = "foreign_key_cascade_tree"

    # Procedural & Transaction Control (PL/pgSQL, T-SQL, PL/SQL)
    STORED_PROCEDURE_ROUTER = "stored_procedure_router"
    TRIGGER_EVENT_INTERCEPTOR = "trigger_event_interceptor"
    TRANSACTION_ISOLATION_GUARD = "transaction_isolation_guard"
    AUTONOMOUS_TRANSACTION_SAVEPOINT = "autonomous_transaction_savepoint"

    # GoF Creational in SQL
    FACTORY_SEQUENCE_ID_GENERATOR = "factory_sequence_id_generator"
    BUILDER_DYNAMIC_QUERY_COMPOSER = "builder_dynamic_query_composer"
    PROTOTYPE_ROW_CLONER = "prototype_row_cloner"
    SINGLETON_CONFIG_PARAM_TABLE = "singleton_config_param_table"
    ABSTRACT_FACTORY_SCHEMA_TENANT = "abstract_factory_schema_tenant"

    # GoF Structural in SQL
    ADAPTER_FOREIGN_DATA_WRAPPER = "adapter_foreign_data_wrapper"
    BRIDGE_POLYMORPHIC_JUNCTION = "bridge_polymorphic_junction"
    COMPOSITE_HIERARCHICAL_TREE = "composite_hierarchical_tree"
    DECORATOR_COMPUTED_AUDIT_LOG = "decorator_computed_audit_log"
    FACADE_REPORTING_VIEW = "facade_reporting_view"
    FLYWEIGHT_LOOKUP_DICTIONARY = "flyweight_lookup_dictionary"
    PROXY_STAGED_LANDING_TABLE = "proxy_staged_landing_table"

    # GoF Behavioral in SQL
    CHAIN_OF_RESPONSIBILITY_TRIGGER_PIPELINE = "chain_of_responsibility_trigger_pipeline"
    COMMAND_ACTION_QUEUE_TABLE = "command_action_queue_table"
    INTERPRETER_DYNAMIC_SQL_EVAL = "interpreter_dynamic_sql_eval"
    ITERATOR_CURSOR_FETCH_LOOP = "iterator_cursor_fetch_loop"
    MEDIATOR_PUBSUB_NOTIFY = "mediator_pubsub_notify"
    MEMENTO_POINT_IN_TIME_FLASHBACK = "memento_point_in_time_flashback"
    OBSERVER_TRIGGER_AUDIT_BROADCAST = "observer_trigger_audit_broadcast"
    STATE_MACHINE_STATUS_CONSTRAINT = "state_machine_status_constraint"
    STRATEGY_DYNAMIC_PARTITION_PRUNING = "strategy_dynamic_partition_pruning"
    TEMPLATE_METHOD_PROCEDURAL_SCHEMA = "template_method_procedural_schema"
    VISITOR_RECURSIVE_TREE_SCAN = "visitor_recursive_tree_scan"

    # SQL Security Hazards & Anti-Patterns
    SQL_INJECTION_DYNAMIC_CONCAT_HAZARD = "sql_injection_dynamic_concat_hazard"
    MISSING_INDEX_FOREIGN_KEY_HAZARD = "missing_index_foreign_key_hazard"
    N_PLUS_ONE_CURSOR_ITERATION_HAZARD = "n_plus_one_cursor_iteration_hazard"
    UNBOUNDED_SELECT_STAR_HAZARD = "unbounded_select_star_hazard"
    DEADLOCK_PRONE_LOCK_ORDERING_HAZARD = "deadlock_prone_lock_ordering_hazard"
    IMPLICIT_TYPE_CASTING_INDEX_HAZARD = "implicit_type_casting_index_hazard"

    # SOLID Principles
    MONOLITHIC_PROCEDURE_SRP = "monolithic_procedure_srp"
    WIDE_TABLE_GOD_SCHEMA_SRP = "wide_table_god_schema_srp"
    FAT_VIEW_INTERFACE_ISP = "fat_view_interface_isp"


class ConfidenceLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"


@dataclass(frozen=True)
class SourceLocation:
    file_path: str
    line_number: int
    column_number: int = 1

    def __str__(self) -> str:
        return f"{self.file_path}:{self.line_number}:{self.column_number}"


@dataclass(frozen=True)
class EvidenceItem:
    rule_name: str
    weight: float
    description: str
    location: Optional[SourceLocation] = None


@dataclass
class Confidence:
    value: float  # 0.0 to 1.0

    @property
    def level(self) -> ConfidenceLevel:
        if self.value >= 0.85:
            return ConfidenceLevel.VERY_HIGH
        if self.value >= 0.70:
            return ConfidenceLevel.HIGH
        if self.value >= 0.50:
            return ConfidenceLevel.MEDIUM
        return ConfidenceLevel.LOW

    @property
    def percentage(self) -> int:
        return int(round(self.value * 100))
