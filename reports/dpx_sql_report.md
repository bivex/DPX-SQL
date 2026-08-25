# 🐘 DPX-SQL Analysis Report

- **Target Path**: `benchmarks/ecommerce_enterprise_schema.sql`
- **Scanned Files**: `1`
- **Execution Time**: `0.0015s`
- **Total Detections**: `45`

## 📊 Category Breakdown

| Category | Detections |
|---|:---:|
| `behavioral` | 10 |
| `relational_indexing_schema` | 7 |
| `sql_idiomatic_optimization` | 6 |
| `creational` | 6 |
| `structural` | 6 |
| `procedural_transaction_control` | 5 |
| `sql_security_hazards` | 5 |

## 🔍 Findings & Detections

| # | Category | Pattern Type | Target | Confidence | Location | Summary |
|---|---|---|---|:---:|---|---|
| 1 | `sql_idiomatic_optimization` | `recursive_cte_hierarchy` | `WITH_RECURSIVE` | **95%** [VERY_HIGH] | `ecommerce_enterprise_schema.sql:144` | Hierarchical graph or tree traversal using WITH RECURSIVE queries with anchor and recursive members. |
| 2 | `sql_idiomatic_optimization` | `window_function_analytics` | `OVER()` | **92%** [VERY_HIGH] | `ecommerce_enterprise_schema.sql:144` | Analytical aggregations and ranking across partitions (ROW_NUMBER, RANK, DENSE_RANK, LAG, LEAD, SUM OVER). |
| 3 | `sql_idiomatic_optimization` | `upsert_merge_idempotency` | `UPSERT/MERGE` | **92%** [VERY_HIGH] | `ecommerce_enterprise_schema.sql:157` | Atomic insert-or-update idempotency using ON CONFLICT DO UPDATE or standard ANSI MERGE INTO. |
| 4 | `sql_idiomatic_optimization` | `materialized_view_cache` | `mv_daily_financial_summary` | **90%** [VERY_HIGH] | `ecommerce_enterprise_schema.sql:122` | Precomputed query caching and indexing via CREATE MATERIALIZED VIEW with REFRESH strategy. |
| 5 | `sql_idiomatic_optimization` | `lateral_join_subquery` | `JOIN_LATERAL` | **90%** [VERY_HIGH] | `ecommerce_enterprise_schema.sql:161` | Correlated subquery evaluation per row using CROSS/LEFT JOIN LATERAL or APPLY. |
| 6 | `sql_idiomatic_optimization` | `table_partitioning_sharding` | `ledger_transactions` | **92%** [VERY_HIGH] | `ecommerce_enterprise_schema.sql:34` | Horizontal data partitioning by RANGE, LIST, or HASH for high-volume storage scalability. |
| 7 | `relational_indexing_schema` | `partial_conditional_index` | `idx_ledger_active_pending` | **95%** [VERY_HIGH] | `ecommerce_enterprise_schema.sql:47` | Space-saving index defined over a subset of rows using CREATE INDEX ... WHERE filter. |
| 8 | `relational_indexing_schema` | `covering_index_include` | `idx_ledger_covering_acc` | **92%** [VERY_HIGH] | `ecommerce_enterprise_schema.sql:48` | Index-only scans avoiding heap lookups via CREATE INDEX ... INCLUDE (columns). |
| 9 | `relational_indexing_schema` | `gin_gist_specialized_index` | `idx_ledger_metadata_gin` | **95%** [VERY_HIGH] | `ecommerce_enterprise_schema.sql:49` | Inverted or search-tree indexing for JSONB, array elements, PostGIS geometry, or full-text tsvector. |
| 10 | `relational_indexing_schema` | `composite_multi_column_index` | `idx_ledger_active_pending` | **90%** [VERY_HIGH] | `ecommerce_enterprise_schema.sql:47` | Multi-column compound B-tree index optimizing multi-predicate queries and sorting. |
| 11 | `relational_indexing_schema` | `composite_multi_column_index` | `idx_ledger_compound` | **90%** [VERY_HIGH] | `ecommerce_enterprise_schema.sql:50` | Multi-column compound B-tree index optimizing multi-predicate queries and sorting. |
| 12 | `relational_indexing_schema` | `foreign_key_cascade_tree` | `organizations->organizations` | **90%** [VERY_HIGH] | `ecommerce_enterprise_schema.sql:26` | Declarative referential integrity with ON DELETE/UPDATE CASCADE or SET NULL rules. |
| 13 | `relational_indexing_schema` | `foreign_key_cascade_tree` | `ledger_transactions->organizations` | **90%** [VERY_HIGH] | `ecommerce_enterprise_schema.sql:34` | Declarative referential integrity with ON DELETE/UPDATE CASCADE or SET NULL rules. |
| 14 | `procedural_transaction_control` | `stored_procedure_router` | `process_settlement_batch` | **92%** [VERY_HIGH] | `ecommerce_enterprise_schema.sql:88` | Encapsulated business logic and multi-step transaction workflow inside server-side routines. |
| 15 | `procedural_transaction_control` | `stored_procedure_router` | `query_custom_table` | **92%** [VERY_HIGH] | `ecommerce_enterprise_schema.sql:111` | Encapsulated business logic and multi-step transaction workflow inside server-side routines. |
| 16 | `procedural_transaction_control` | `trigger_event_interceptor` | `trg_ledger_audit` | **95%** [VERY_HIGH] | `ecommerce_enterprise_schema.sql:118` | Automated lifecycle event interception via BEFORE/AFTER INSERT/UPDATE/DELETE FOR EACH ROW. |
| 17 | `procedural_transaction_control` | `transaction_isolation_guard` | `ISOLATION_LOCK` | **92%** [VERY_HIGH] | `ecommerce_enterprise_schema.sql:167` | Explicit concurrency and consistency locking (SERIALIZABLE, REPEATABLE READ, SELECT FOR UPDATE). |
| 18 | `procedural_transaction_control` | `autonomous_transaction_savepoint` | `process_settlement_batch` | **90%** [VERY_HIGH] | `ecommerce_enterprise_schema.sql:88` | Granular rollback boundaries and nested transaction checkpoints using SAVEPOINT / RELEASE. |
| 19 | `creational` | `factory_sequence_id_generator` | `tenant_id_seq` | **90%** [VERY_HIGH] | `ecommerce_enterprise_schema.sql:1` | Factory pattern generating unique primary keys or UUIDs via CREATE SEQUENCE / GENERATED ALWAYS AS IDENTITY. |
| 20 | `creational` | `factory_sequence_id_generator` | `order_id_seq` | **90%** [VERY_HIGH] | `ecommerce_enterprise_schema.sql:1` | Factory pattern generating unique primary keys or UUIDs via CREATE SEQUENCE / GENERATED ALWAYS AS IDENTITY. |
| 21 | `creational` | `factory_sequence_id_generator` | `organizations.id` | **92%** [VERY_HIGH] | `ecommerce_enterprise_schema.sql:26` | Factory pattern generating unique primary keys or UUIDs via CREATE SEQUENCE / GENERATED ALWAYS AS IDENTITY. |
| 22 | `creational` | `factory_sequence_id_generator` | `ledger_transactions.id` | **92%** [VERY_HIGH] | `ecommerce_enterprise_schema.sql:34` | Factory pattern generating unique primary keys or UUIDs via CREATE SEQUENCE / GENERATED ALWAYS AS IDENTITY. |
| 23 | `creational` | `factory_sequence_id_generator` | `entity_attachments.id` | **92%** [VERY_HIGH] | `ecommerce_enterprise_schema.sql:53` | Factory pattern generating unique primary keys or UUIDs via CREATE SEQUENCE / GENERATED ALWAYS AS IDENTITY. |
| 24 | `creational` | `singleton_config_param_table` | `system_parameters` | **92%** [VERY_HIGH] | `ecommerce_enterprise_schema.sql:11` | Singleton pattern managing global system configuration in a constrained 1-row table or key-value store. |
| 25 | `structural` | `bridge_polymorphic_junction` | `entity_attachments` | **88%** [VERY_HIGH] | `ecommerce_enterprise_schema.sql:53` | Bridge pattern decoupling entity types from relations via polymorphic target_type + target_id junction. |
| 26 | `structural` | `composite_hierarchical_tree` | `organizations` | **92%** [VERY_HIGH] | `ecommerce_enterprise_schema.sql:26` | Composite pattern modeling parent-child trees via self-referencing foreign keys or closure tables. |
| 27 | `structural` | `decorator_computed_audit_log` | `trg_ledger_audit` | **95%** [VERY_HIGH] | `ecommerce_enterprise_schema.sql:118` | Decorator pattern augmenting table modifications with automated shadow audit logs and timestamps. |
| 28 | `structural` | `facade_reporting_view` | `v_organization_full_tree` | **90%** [VERY_HIGH] | `ecommerce_enterprise_schema.sql:133` | Facade pattern providing unified simplified read interface over complex normalized multi-table joins. |
| 29 | `structural` | `flyweight_lookup_dictionary` | `order_status_dictionary` | **90%** [VERY_HIGH] | `ecommerce_enterprise_schema.sql:19` | Flyweight pattern deduplicating repeating string constants into small integer foreign key dictionary tables. |
| 30 | `structural` | `proxy_staged_landing_table` | `staging_raw_events` | **88%** [VERY_HIGH] | `ecommerce_enterprise_schema.sql:72` | Proxy pattern buffering raw batch data into unlogged/temporary staging tables before ingestion. |
| 31 | `behavioral` | `command_action_queue_table` | `outbox_tasks` | **92%** [VERY_HIGH] | `ecommerce_enterprise_schema.sql:62` | Command pattern storing asynchronous transactional tasks or events in a work queue table (SKIP LOCKED). |
| 32 | `behavioral` | `interpreter_dynamic_sql_eval` | `query_custom_table` | **88%** [VERY_HIGH] | `ecommerce_enterprise_schema.sql:111` | Interpreter pattern evaluating parameterized dynamic expressions at runtime via EXECUTE / sp_executesql. |
| 33 | `behavioral` | `iterator_cursor_fetch_loop` | `process_settlement_batch` | **92%** [VERY_HIGH] | `ecommerce_enterprise_schema.sql:88` | Iterator pattern sequentially traversing large query result sets using CURSOR FOR ... FETCH NEXT. |
| 34 | `behavioral` | `mediator_pubsub_notify` | `process_settlement_batch` | **92%** [VERY_HIGH] | `ecommerce_enterprise_schema.sql:88` | Mediator pattern broadcasting decoupled change notifications across services via LISTEN / NOTIFY. |
| 35 | `behavioral` | `memento_point_in_time_flashback` | `account_balances_history` | **92%** [VERY_HIGH] | `ecommerce_enterprise_schema.sql:79` | Memento pattern preserving temporal snapshots via System-Versioned / Temporal tables or Change Data Capture (CDC). |
| 36 | `behavioral` | `observer_trigger_audit_broadcast` | `trg_ledger_audit` | **92%** [VERY_HIGH] | `ecommerce_enterprise_schema.sql:118` | Observer pattern publishing table modification events to observer subscriber tables or event streams. |
| 37 | `behavioral` | `state_machine_status_constraint` | `ledger_transactions` | **90%** [VERY_HIGH] | `ecommerce_enterprise_schema.sql:34` | State pattern enforcing valid lifecycle status transitions via CHECK constraints or trigger guards. |
| 38 | `behavioral` | `strategy_dynamic_partition_pruning` | `ledger_transactions` | **88%** [VERY_HIGH] | `ecommerce_enterprise_schema.sql:34` | Strategy pattern selecting optimized storage partitions dynamically based on query filter keys. |
| 39 | `behavioral` | `template_method_procedural_schema` | `process_settlement_batch` | **90%** [VERY_HIGH] | `ecommerce_enterprise_schema.sql:88` | Template Method pattern executing standard transaction workflow (begin -> hook -> commit -> catch). |
| 40 | `behavioral` | `visitor_recursive_tree_scan` | `RECURSIVE_VISITOR` | **90%** [VERY_HIGH] | `ecommerce_enterprise_schema.sql:144` | Visitor pattern executing domain operations across all nodes in a hierarchical tree via recursive query. |
| 41 | `sql_security_hazards` | `sql_injection_dynamic_concat_hazard` | `query_custom_table` | **95%** [VERY_HIGH] | `ecommerce_enterprise_schema.sql:113` | Unsanitized string concatenation in dynamic EXECUTE statements risking arbitrary SQL injection. |
| 42 | `sql_security_hazards` | `missing_index_foreign_key_hazard` | `organizations.parent_id` | **88%** [VERY_HIGH] | `ecommerce_enterprise_schema.sql:26` | Foreign key column without corresponding index causing full table scans and table-level locks on DELETE. |
| 43 | `sql_security_hazards` | `n_plus_one_cursor_iteration_hazard` | `process_settlement_batch` | **90%** [VERY_HIGH] | `ecommerce_enterprise_schema.sql:88` | Row-by-Row cursor loop (RBAR) executing queries inside iteration instead of vectorized set-based operations. |
| 44 | `sql_security_hazards` | `unbounded_select_star_hazard` | `query_custom_table` | **85%** [VERY_HIGH] | `ecommerce_enterprise_schema.sql:111` | Production view or procedure using SELECT * risking schema drift breakage and excessive IO. |
| 45 | `sql_security_hazards` | `deadlock_prone_lock_ordering_hazard` | `FOR_UPDATE` | **88%** [VERY_HIGH] | `ecommerce_enterprise_schema.sql:167` | SELECT FOR UPDATE without explicit ORDER BY risking concurrent deadlock under high contention. |
