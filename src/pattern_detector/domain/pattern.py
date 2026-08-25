from dataclasses import dataclass
from typing import Dict
from .value_objects import PatternCategory, PatternType


@dataclass(frozen=True)
class PatternMetadata:
    pattern_type: PatternType
    name: str
    category: PatternCategory
    description: str
    default_weight: float


PATTERN_CATALOG: Dict[PatternType, PatternMetadata] = {
    # SQL Idiomatic & Query Optimization
    PatternType.RECURSIVE_CTE_HIERARCHY: PatternMetadata(
        pattern_type=PatternType.RECURSIVE_CTE_HIERARCHY,
        name="Recursive CTE Hierarchy",
        category=PatternCategory.SQL_IDIOMATIC_OPTIMIZATION,
        description="Hierarchical graph or tree traversal using WITH RECURSIVE queries with anchor and recursive members.",
        default_weight=0.95,
    ),
    PatternType.WINDOW_FUNCTION_ANALYTICS: PatternMetadata(
        pattern_type=PatternType.WINDOW_FUNCTION_ANALYTICS,
        name="Window Function Analytics",
        category=PatternCategory.SQL_IDIOMATIC_OPTIMIZATION,
        description="Analytical aggregations and ranking across partitions (ROW_NUMBER, RANK, DENSE_RANK, LAG, LEAD, SUM OVER).",
        default_weight=0.92,
    ),
    PatternType.UPSERT_MERGE_IDEMPOTENCY: PatternMetadata(
        pattern_type=PatternType.UPSERT_MERGE_IDEMPOTENCY,
        name="Upsert Merge Idempotency",
        category=PatternCategory.SQL_IDIOMATIC_OPTIMIZATION,
        description="Atomic insert-or-update idempotency using ON CONFLICT DO UPDATE or standard ANSI MERGE INTO.",
        default_weight=0.92,
    ),
    PatternType.MATERIALIZED_VIEW_CACHE: PatternMetadata(
        pattern_type=PatternType.MATERIALIZED_VIEW_CACHE,
        name="Materialized View Cache",
        category=PatternCategory.SQL_IDIOMATIC_OPTIMIZATION,
        description="Precomputed query caching and indexing via CREATE MATERIALIZED VIEW with REFRESH strategy.",
        default_weight=0.90,
    ),
    PatternType.LATERAL_JOIN_SUBQUERY: PatternMetadata(
        pattern_type=PatternType.LATERAL_JOIN_SUBQUERY,
        name="Lateral Join Subquery",
        category=PatternCategory.SQL_IDIOMATIC_OPTIMIZATION,
        description="Correlated subquery evaluation per row using CROSS/LEFT JOIN LATERAL or APPLY.",
        default_weight=0.90,
    ),
    PatternType.TABLE_PARTITIONING_SHARDING: PatternMetadata(
        pattern_type=PatternType.TABLE_PARTITIONING_SHARDING,
        name="Table Partitioning & Sharding",
        category=PatternCategory.SQL_IDIOMATIC_OPTIMIZATION,
        description="Horizontal data partitioning by RANGE, LIST, or HASH for high-volume storage scalability.",
        default_weight=0.92,
    ),

    # Relational Indexing & Schema Design
    PatternType.PARTIAL_CONDITIONAL_INDEX: PatternMetadata(
        pattern_type=PatternType.PARTIAL_CONDITIONAL_INDEX,
        name="Partial Conditional Index",
        category=PatternCategory.RELATIONAL_INDEXING_SCHEMA,
        description="Space-saving index defined over a subset of rows using CREATE INDEX ... WHERE filter.",
        default_weight=0.95,
    ),
    PatternType.COVERING_INDEX_INCLUDE: PatternMetadata(
        pattern_type=PatternType.COVERING_INDEX_INCLUDE,
        name="Covering Index (INCLUDE)",
        category=PatternCategory.RELATIONAL_INDEXING_SCHEMA,
        description="Index-only scans avoiding heap lookups via CREATE INDEX ... INCLUDE (columns).",
        default_weight=0.92,
    ),
    PatternType.GIN_GIST_SPECIALIZED_INDEX: PatternMetadata(
        pattern_type=PatternType.GIN_GIST_SPECIALIZED_INDEX,
        name="GIN/GiST Specialized Index",
        category=PatternCategory.RELATIONAL_INDEXING_SCHEMA,
        description="Inverted or search-tree indexing for JSONB, array elements, PostGIS geometry, or full-text tsvector.",
        default_weight=0.95,
    ),
    PatternType.COMPOSITE_MULTI_COLUMN_INDEX: PatternMetadata(
        pattern_type=PatternType.COMPOSITE_MULTI_COLUMN_INDEX,
        name="Composite Multi-Column Index",
        category=PatternCategory.RELATIONAL_INDEXING_SCHEMA,
        description="Multi-column compound B-tree index optimizing multi-predicate queries and sorting.",
        default_weight=0.90,
    ),
    PatternType.FOREIGN_KEY_CASCADE_TREE: PatternMetadata(
        pattern_type=PatternType.FOREIGN_KEY_CASCADE_TREE,
        name="Foreign Key Cascade Tree",
        category=PatternCategory.RELATIONAL_INDEXING_SCHEMA,
        description="Declarative referential integrity with ON DELETE/UPDATE CASCADE or SET NULL rules.",
        default_weight=0.90,
    ),

    # Procedural & Transaction Control (PL/pgSQL, T-SQL, PL/SQL)
    PatternType.STORED_PROCEDURE_ROUTER: PatternMetadata(
        pattern_type=PatternType.STORED_PROCEDURE_ROUTER,
        name="Stored Procedure Router",
        category=PatternCategory.PROCEDURAL_TRANSACTION_CONTROL,
        description="Encapsulated business logic and multi-step transaction workflow inside server-side routines.",
        default_weight=0.92,
    ),
    PatternType.TRIGGER_EVENT_INTERCEPTOR: PatternMetadata(
        pattern_type=PatternType.TRIGGER_EVENT_INTERCEPTOR,
        name="Trigger Event Interceptor",
        category=PatternCategory.PROCEDURAL_TRANSACTION_CONTROL,
        description="Automated lifecycle event interception via BEFORE/AFTER INSERT/UPDATE/DELETE FOR EACH ROW.",
        default_weight=0.95,
    ),
    PatternType.TRANSACTION_ISOLATION_GUARD: PatternMetadata(
        pattern_type=PatternType.TRANSACTION_ISOLATION_GUARD,
        name="Transaction Isolation Guard",
        category=PatternCategory.PROCEDURAL_TRANSACTION_CONTROL,
        description="Explicit concurrency and consistency locking (SERIALIZABLE, REPEATABLE READ, SELECT FOR UPDATE).",
        default_weight=0.92,
    ),
    PatternType.AUTONOMOUS_TRANSACTION_SAVEPOINT: PatternMetadata(
        pattern_type=PatternType.AUTONOMOUS_TRANSACTION_SAVEPOINT,
        name="Autonomous Transaction Savepoint",
        category=PatternCategory.PROCEDURAL_TRANSACTION_CONTROL,
        description="Granular rollback boundaries and nested transaction checkpoints using SAVEPOINT / RELEASE.",
        default_weight=0.90,
    ),

    # GoF Creational in SQL
    PatternType.FACTORY_SEQUENCE_ID_GENERATOR: PatternMetadata(
        pattern_type=PatternType.FACTORY_SEQUENCE_ID_GENERATOR,
        name="Factory Sequence ID Generator",
        category=PatternCategory.CREATIONAL,
        description="Factory pattern generating unique primary keys or UUIDs via CREATE SEQUENCE / GENERATED ALWAYS AS IDENTITY.",
        default_weight=0.90,
    ),
    PatternType.BUILDER_DYNAMIC_QUERY_COMPOSER: PatternMetadata(
        pattern_type=PatternType.BUILDER_DYNAMIC_QUERY_COMPOSER,
        name="Builder Dynamic Query Composer",
        category=PatternCategory.CREATIONAL,
        description="Builder pattern incrementally constructing structured SQL queries via format() or string assembly.",
        default_weight=0.88,
    ),
    PatternType.PROTOTYPE_ROW_CLONER: PatternMetadata(
        pattern_type=PatternType.PROTOTYPE_ROW_CLONER,
        name="Prototype Row Cloner",
        category=PatternCategory.CREATIONAL,
        description="Prototype pattern cloning existing template rows into new records via INSERT INTO ... SELECT.",
        default_weight=0.88,
    ),
    PatternType.SINGLETON_CONFIG_PARAM_TABLE: PatternMetadata(
        pattern_type=PatternType.SINGLETON_CONFIG_PARAM_TABLE,
        name="Singleton Config Parameter Table",
        category=PatternCategory.CREATIONAL,
        description="Singleton pattern managing global system configuration in a constrained 1-row table or key-value store.",
        default_weight=0.92,
    ),
    PatternType.ABSTRACT_FACTORY_SCHEMA_TENANT: PatternMetadata(
        pattern_type=PatternType.ABSTRACT_FACTORY_SCHEMA_TENANT,
        name="Abstract Factory Schema Tenant",
        category=PatternCategory.CREATIONAL,
        description="Abstract Factory pattern dynamically provisioning tenant schema objects in multi-tenant architectures.",
        default_weight=0.88,
    ),

    # GoF Structural in SQL
    PatternType.ADAPTER_FOREIGN_DATA_WRAPPER: PatternMetadata(
        pattern_type=PatternType.ADAPTER_FOREIGN_DATA_WRAPPER,
        name="Adapter Foreign Data Wrapper",
        category=PatternCategory.STRUCTURAL,
        description="Adapter pattern querying heterogeneous remote databases via postgres_fdw, dblink, or Linked Servers.",
        default_weight=0.92,
    ),
    PatternType.BRIDGE_POLYMORPHIC_JUNCTION: PatternMetadata(
        pattern_type=PatternType.BRIDGE_POLYMORPHIC_JUNCTION,
        name="Bridge Polymorphic Junction",
        category=PatternCategory.STRUCTURAL,
        description="Bridge pattern decoupling entity types from relations via polymorphic target_type + target_id junction.",
        default_weight=0.88,
    ),
    PatternType.COMPOSITE_HIERARCHICAL_TREE: PatternMetadata(
        pattern_type=PatternType.COMPOSITE_HIERARCHICAL_TREE,
        name="Composite Hierarchical Tree",
        category=PatternCategory.STRUCTURAL,
        description="Composite pattern modeling parent-child trees via self-referencing foreign keys or closure tables.",
        default_weight=0.92,
    ),
    PatternType.DECORATOR_COMPUTED_AUDIT_LOG: PatternMetadata(
        pattern_type=PatternType.DECORATOR_COMPUTED_AUDIT_LOG,
        name="Decorator Computed Audit Log",
        category=PatternCategory.STRUCTURAL,
        description="Decorator pattern augmenting table modifications with automated shadow audit logs and timestamps.",
        default_weight=0.95,
    ),
    PatternType.FACADE_REPORTING_VIEW: PatternMetadata(
        pattern_type=PatternType.FACADE_REPORTING_VIEW,
        name="Facade Reporting View",
        category=PatternCategory.STRUCTURAL,
        description="Facade pattern providing unified simplified read interface over complex normalized multi-table joins.",
        default_weight=0.90,
    ),
    PatternType.FLYWEIGHT_LOOKUP_DICTIONARY: PatternMetadata(
        pattern_type=PatternType.FLYWEIGHT_LOOKUP_DICTIONARY,
        name="Flyweight Lookup Dictionary",
        category=PatternCategory.STRUCTURAL,
        description="Flyweight pattern deduplicating repeating string constants into small integer foreign key dictionary tables.",
        default_weight=0.90,
    ),
    PatternType.PROXY_STAGED_LANDING_TABLE: PatternMetadata(
        pattern_type=PatternType.PROXY_STAGED_LANDING_TABLE,
        name="Proxy Staged Landing Table",
        category=PatternCategory.STRUCTURAL,
        description="Proxy pattern buffering raw batch data into unlogged/temporary staging tables before ingestion.",
        default_weight=0.88,
    ),

    # GoF Behavioral in SQL
    PatternType.CHAIN_OF_RESPONSIBILITY_TRIGGER_PIPELINE: PatternMetadata(
        pattern_type=PatternType.CHAIN_OF_RESPONSIBILITY_TRIGGER_PIPELINE,
        name="Chain of Responsibility Trigger Pipeline",
        category=PatternCategory.BEHAVIORAL,
        description="Chain of Responsibility sequencing ordered triggers (validation -> normalization -> audit).",
        default_weight=0.90,
    ),
    PatternType.COMMAND_ACTION_QUEUE_TABLE: PatternMetadata(
        pattern_type=PatternType.COMMAND_ACTION_QUEUE_TABLE,
        name="Command Action Queue Table",
        category=PatternCategory.BEHAVIORAL,
        description="Command pattern storing asynchronous transactional tasks or events in a work queue table (SKIP LOCKED).",
        default_weight=0.92,
    ),
    PatternType.INTERPRETER_DYNAMIC_SQL_EVAL: PatternMetadata(
        pattern_type=PatternType.INTERPRETER_DYNAMIC_SQL_EVAL,
        name="Interpreter Dynamic SQL Eval",
        category=PatternCategory.BEHAVIORAL,
        description="Interpreter pattern evaluating parameterized dynamic expressions at runtime via EXECUTE / sp_executesql.",
        default_weight=0.88,
    ),
    PatternType.ITERATOR_CURSOR_FETCH_LOOP: PatternMetadata(
        pattern_type=PatternType.ITERATOR_CURSOR_FETCH_LOOP,
        name="Iterator Cursor Fetch Loop",
        category=PatternCategory.BEHAVIORAL,
        description="Iterator pattern sequentially traversing large query result sets using CURSOR FOR ... FETCH NEXT.",
        default_weight=0.92,
    ),
    PatternType.MEDIATOR_PUBSUB_NOTIFY: PatternMetadata(
        pattern_type=PatternType.MEDIATOR_PUBSUB_NOTIFY,
        name="Mediator PubSub Notify",
        category=PatternCategory.BEHAVIORAL,
        description="Mediator pattern broadcasting decoupled change notifications across services via LISTEN / NOTIFY.",
        default_weight=0.92,
    ),
    PatternType.MEMENTO_POINT_IN_TIME_FLASHBACK: PatternMetadata(
        pattern_type=PatternType.MEMENTO_POINT_IN_TIME_FLASHBACK,
        name="Memento Point-in-Time Flashback",
        category=PatternCategory.BEHAVIORAL,
        description="Memento pattern preserving temporal snapshots via System-Versioned / Temporal tables or Change Data Capture (CDC).",
        default_weight=0.92,
    ),
    PatternType.OBSERVER_TRIGGER_AUDIT_BROADCAST: PatternMetadata(
        pattern_type=PatternType.OBSERVER_TRIGGER_AUDIT_BROADCAST,
        name="Observer Trigger Audit Broadcast",
        category=PatternCategory.BEHAVIORAL,
        description="Observer pattern publishing table modification events to observer subscriber tables or event streams.",
        default_weight=0.92,
    ),
    PatternType.STATE_MACHINE_STATUS_CONSTRAINT: PatternMetadata(
        pattern_type=PatternType.STATE_MACHINE_STATUS_CONSTRAINT,
        name="State Machine Status Constraint",
        category=PatternCategory.BEHAVIORAL,
        description="State pattern enforcing valid lifecycle status transitions via CHECK constraints or trigger guards.",
        default_weight=0.90,
    ),
    PatternType.STRATEGY_DYNAMIC_PARTITION_PRUNING: PatternMetadata(
        pattern_type=PatternType.STRATEGY_DYNAMIC_PARTITION_PRUNING,
        name="Strategy Dynamic Partition Pruning",
        category=PatternCategory.BEHAVIORAL,
        description="Strategy pattern selecting optimized storage partitions dynamically based on query filter keys.",
        default_weight=0.88,
    ),
    PatternType.TEMPLATE_METHOD_PROCEDURAL_SCHEMA: PatternMetadata(
        pattern_type=PatternType.TEMPLATE_METHOD_PROCEDURAL_SCHEMA,
        name="Template Method Procedural Schema",
        category=PatternCategory.BEHAVIORAL,
        description="Template Method pattern executing standard transaction workflow (begin -> hook -> commit -> catch).",
        default_weight=0.90,
    ),
    PatternType.VISITOR_RECURSIVE_TREE_SCAN: PatternMetadata(
        pattern_type=PatternType.VISITOR_RECURSIVE_TREE_SCAN,
        name="Visitor Recursive Tree Scan",
        category=PatternCategory.BEHAVIORAL,
        description="Visitor pattern executing domain operations across all nodes in a hierarchical tree via recursive query.",
        default_weight=0.90,
    ),

    # SQL Security Hazards & Anti-Patterns
    PatternType.SQL_INJECTION_DYNAMIC_CONCAT_HAZARD: PatternMetadata(
        pattern_type=PatternType.SQL_INJECTION_DYNAMIC_CONCAT_HAZARD,
        name="SQL Injection Dynamic Concatenation Hazard",
        category=PatternCategory.SQL_SECURITY_HAZARDS,
        description="Unsanitized string concatenation in dynamic EXECUTE statements risking arbitrary SQL injection.",
        default_weight=0.95,
    ),
    PatternType.MISSING_INDEX_FOREIGN_KEY_HAZARD: PatternMetadata(
        pattern_type=PatternType.MISSING_INDEX_FOREIGN_KEY_HAZARD,
        name="Missing Index on Foreign Key Hazard",
        category=PatternCategory.SQL_SECURITY_HAZARDS,
        description="Foreign key column without corresponding index causing full table scans and table-level locks on DELETE.",
        default_weight=0.88,
    ),
    PatternType.N_PLUS_ONE_CURSOR_ITERATION_HAZARD: PatternMetadata(
        pattern_type=PatternType.N_PLUS_ONE_CURSOR_ITERATION_HAZARD,
        name="N+1 Cursor Iteration Hazard (RBAR)",
        category=PatternCategory.SQL_SECURITY_HAZARDS,
        description="Row-by-Row cursor loop (RBAR) executing queries inside iteration instead of vectorized set-based operations.",
        default_weight=0.90,
    ),
    PatternType.UNBOUNDED_SELECT_STAR_HAZARD: PatternMetadata(
        pattern_type=PatternType.UNBOUNDED_SELECT_STAR_HAZARD,
        name="Unbounded SELECT * Hazard",
        category=PatternCategory.SQL_SECURITY_HAZARDS,
        description="Production view or procedure using SELECT * risking schema drift breakage and excessive IO.",
        default_weight=0.85,
    ),
    PatternType.DEADLOCK_PRONE_LOCK_ORDERING_HAZARD: PatternMetadata(
        pattern_type=PatternType.DEADLOCK_PRONE_LOCK_ORDERING_HAZARD,
        name="Deadlock-Prone Unordered Lock Hazard",
        category=PatternCategory.SQL_SECURITY_HAZARDS,
        description="SELECT FOR UPDATE without explicit ORDER BY risking concurrent deadlock under high contention.",
        default_weight=0.88,
    ),
    PatternType.IMPLICIT_TYPE_CASTING_INDEX_HAZARD: PatternMetadata(
        pattern_type=PatternType.IMPLICIT_TYPE_CASTING_INDEX_HAZARD,
        name="Function Call on Indexed Column Hazard",
        category=PatternCategory.SQL_SECURITY_HAZARDS,
        description="Applying functions (LOWER, DATE) directly to indexed columns in WHERE clause invalidating index lookups.",
        default_weight=0.85,
    ),

    # SOLID Principles
    PatternType.MONOLITHIC_PROCEDURE_SRP: PatternMetadata(
        pattern_type=PatternType.MONOLITHIC_PROCEDURE_SRP,
        name="Monolithic Stored Procedure (SRP Violation)",
        category=PatternCategory.SOLID_PRINCIPLES,
        description="Excessively long stored procedure (>100 lines) handling multiple disparate business operations.",
        default_weight=0.85,
    ),
    PatternType.WIDE_TABLE_GOD_SCHEMA_SRP: PatternMetadata(
        pattern_type=PatternType.WIDE_TABLE_GOD_SCHEMA_SRP,
        name="Wide God Table Schema (SRP Violation)",
        category=PatternCategory.SOLID_PRINCIPLES,
        description="Table defining excessive columns (>= 30), violating Single Responsibility and schema normalization.",
        default_weight=0.85,
    ),
    PatternType.FAT_VIEW_INTERFACE_ISP: PatternMetadata(
        pattern_type=PatternType.FAT_VIEW_INTERFACE_ISP,
        name="Fat View Interface (ISP Violation)",
        category=PatternCategory.SOLID_PRINCIPLES,
        description="View joining excessive tables (>= 8) creating monolithic interface coupling and slow execution.",
        default_weight=0.85,
    ),
}
