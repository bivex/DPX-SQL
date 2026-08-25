# 🐘 DPX-SQL: Architectural Pattern & Static Analysis Engine for SQL & Databases

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Architecture: Hexagonal DDD](https://img.shields.io/badge/Architecture-Hexagonal%20DDD-green.svg)](https://en.wikipedia.org/wiki/Hexagonal_architecture_(software))
[![Patterns: 43 Rules](https://img.shields.io/badge/Patterns-43%20Rules-orange.svg)](#-supported-patterns--hazard-catalog)

**DPX-SQL** is a high-performance static analysis and architectural pattern detection engine for SQL schemas, stored procedures, triggers, views, and complex queries across **PostgreSQL, MySQL, SQLite, Oracle PL/SQL, Microsoft T-SQL, Snowflake, and ANSI SQL**.

Built with **Hexagonal Clean Architecture (DDD)**, DPX-SQL maps relational data models and procedural code to **43 architectural patterns, GoF design patterns in RDBMS, schema indexing strategies, and database security hazards**.

---

## 🏛️ Architecture & Design Philosophy

DPX-SQL follows Domain-Driven Design and Ports & Adapters (Hexagonal) architecture:

```
src/pattern_detector/
├── domain/                      # Core business logic & invariants (Zero external dependencies)
│   ├── code_model.py            # AST/Schema Model (SqlTable, SqlColumn, SqlIndex, SqlFunction, etc.)
│   ├── detection.py             # Detection & DetectionReport aggregates
│   ├── pattern.py               # 43 Pattern catalog definitions & weights
│   ├── value_objects.py         # Confidence, SourceLocation, PatternCategory, PatternType
│   └── rules/                   # 43 Pattern Detection Rules
│       ├── idiomatic_rules.py   # CTEs, Window Functions, Upsert, Lateral Joins, Partitioning
│       ├── indexing_rules.py    # Partial, Covering, GIN/GiST, Composite, Cascade FKs
│       ├── procedural_rules.py  # Stored Procedures, Triggers, Savepoints, Isolation
│       ├── creational_rules.py  # Factory Sequences, Builders, Prototypes, Singletons
│       ├── structural_rules.py  # FDW Adapters, Bridges, Composite Trees, Decorator Audits
│       ├── behavioral_rules.py  # Command Queues, Dynamic Interpreters, Cursor Iterators
│       ├── security_rules.py    # SQL Injection, Missing FK Indexes, RBAR Loops, Deadlocks
│       └── solid_principles_rules.py # SRP Monolithic Routines, Wide God Tables, Fat Views
├── ports/                       # Interfaces defining domain boundaries
│   ├── inbound/                 # ParserPort, PatternDetectorPort
│   └── outbound/                # ExporterPort (HTML, JSON, Markdown, SARIF)
├── adapters/                    # Concrete technology implementations
│   ├── inbound/
│   │   ├── parsers/             # RegexSqlParser (Single-pass multi-dialect SQL parser)
│   │   ├── detectors/           # SqlPatternDetector engine
│   │   └── cli/                 # Typer & Rich interactive CLI
│   └── outbound/
│       └── exporters/           # Interactive HTML HUD, SARIF v2.1.0, JSON, Markdown
└── application/
    └── scan_service.py          # Orchestration service
```

---

## 🔍 Supported Patterns & Hazard Catalog (43 Rules)

| Category | Pattern Type | Target / Construct | Default Weight | Description |
|---|---|---|:---:|---|
| **SQL Idiomatic** | `recursive_cte_hierarchy` | `WITH RECURSIVE` | 95% | Hierarchical graph/tree traversal queries |
| | `window_function_analytics` | `OVER (PARTITION BY ...)` | 92% | Analytical ranking, window aggregations, lag/lead |
| | `upsert_merge_idempotency` | `ON CONFLICT / MERGE` | 92% | Atomic insert-or-update idempotent operations |
| | `materialized_view_cache` | `MATERIALIZED VIEW` | 90% | Precomputed physical query cache and refresh |
| | `lateral_join_subquery` | `JOIN LATERAL / APPLY` | 90% | Correlated subquery evaluation per row |
| | `table_partitioning_sharding` | `PARTITION BY RANGE/LIST` | 92% | Horizontal storage sharding for high volumes |
| **Relational Indexing** | `partial_conditional_index` | `CREATE INDEX ... WHERE` | 95% | Space-saving partial indexes with predicates |
| | `covering_index_include` | `CREATE INDEX ... INCLUDE`| 92% | Index-only scans avoiding heap page fetches |
| | `gin_gist_specialized_index` | `USING GIN / GIST` | 95% | Specialized access methods for JSONB/Arrays/PostGIS |
| | `composite_multi_column_index`| `INDEX (col1, col2)` | 90% | Multi-column B-tree indexes for compound filters |
| | `foreign_key_cascade_tree` | `ON DELETE CASCADE` | 90% | Declarative referential cascade delete/update trees |
| **Procedural Logic** | `stored_procedure_router` | `FUNCTION / PROCEDURE` | 92% | Server-side transactional business logic encapsulation |
| | `trigger_event_interceptor` | `TRIGGER BEFORE/AFTER` | 95% | Table lifecycle event interception and mutation |
| | `transaction_isolation_guard` | `SERIALIZABLE / FOR UPDATE`| 92% | Concurrency locking and strict isolation guards |
| | `autonomous_transaction_savepoint` | `SAVEPOINT / RELEASE` | 90% | Granular rollback boundaries within transactions |
| **GoF Creational** | `factory_sequence_id_generator` | `SEQUENCE / IDENTITY` | 90% | Monotonic unique key factory generation |
| | `builder_dynamic_query_composer`| `format() / dynamic query`| 88% | Incremental parameterized SQL query builder |
| | `prototype_row_cloner` | `INSERT INTO ... SELECT` | 88% | Row prototyping and template record cloning |
| | `singleton_config_param_table` | `CHECK (id = 1) / config` | 92% | Constrained global single-row configuration table |
| | `abstract_factory_schema_tenant`| `CREATE SCHEMA tenant_` | 88% | Dynamic multi-tenant schema object provisioning |
| **GoF Structural** | `adapter_foreign_data_wrapper` | `postgres_fdw / linked` | 92% | Heterogeneous remote database schema adapter |
| | `bridge_polymorphic_junction` | `type + id junction` | 88% | Polymorphic relation decoupling target entities |
| | `composite_hierarchical_tree` | `parent_id self-ref` | 92% | Self-referencing hierarchical composite tree models |
| | `decorator_computed_audit_log` | `audit / history trigger`| 95% | Automated table mutation audit logging decorator |
| | `facade_reporting_view` | `VIEW with >= 2 joins` | 90% | Simplified query interface over normalized joins |
| | `flyweight_lookup_dictionary` | `status / enum dictionary`| 90% | Deduplicating string constants into integer FK lookups |
| | `proxy_staged_landing_table` | `UNLOGGED / staging` | 88% | Transient buffer table for batch ETL ingestion |
| **GoF Behavioral** | `chain_of_responsibility_trigger_pipeline` | `>= 2 triggers / table` | 90% | Sequential ordered trigger pipeline execution |
| | `command_action_queue_table` | `outbox / task queue` | 92% | Transactional outbox / command queue table |
| | `interpreter_dynamic_sql_eval` | `EXECUTE format(...)` | 88% | Dynamic runtime evaluation of parameterized queries |
| | `iterator_cursor_fetch_loop` | `CURSOR FOR ... FETCH` | 92% | Sequential cursor traversal of large result sets |
| | `mediator_pubsub_notify` | `LISTEN / NOTIFY` | 92% | Decoupled event bus messaging across services |
| | `memento_point_in_time_flashback`| `Temporal / valid_from` | 92% | System-versioned temporal snapshot history |
| | `observer_trigger_audit_broadcast` | `AFTER INSERT/UPDATE` | 92% | Change notification broadcasting to subscribers |
| | `state_machine_status_constraint` | `CHECK (status IN ...)` | 90% | State machine lifecycle constraint validation |
| | `strategy_dynamic_partition_pruning`| `PARTITION BY strategy`| 88% | Dynamic query execution path routing to sub-tables |
| | `template_method_procedural_schema`| `BEGIN -> EXECUTE -> EXCEPTION` | 90% | Canonical stored routine control flow |
| | `visitor_recursive_tree_scan`| `RECURSIVE with depth` | 90% | Accumulating graph metrics across tree nodes |
| **Security Hazards** | `sql_injection_dynamic_concat_hazard`| `EXECUTE '...' \|\| var` | 95% | Unsanitized string concatenation in dynamic SQL |
| | `missing_index_foreign_key_hazard` | `FK without index` | 88% | Unindexed FK causing full table scans on DELETE |
| | `n_plus_one_cursor_iteration_hazard`| `DML inside cursor loop`| 90% | Row-By-Agonizing-Row (RBAR) anti-pattern |
| | `unbounded_select_star_hazard` | `SELECT * in view/func` | 85% | Schema drift risk and cache thrashing |
| | `deadlock_prone_lock_ordering_hazard`| `FOR UPDATE without ORDER`| 88% | Deadlock vulnerability under concurrent locking |
| | `implicit_type_casting_index_hazard`| `WHERE LOWER(col)` | 85% | Function call invalidating B-tree index lookups |
| **SOLID Principles** | `monolithic_procedure_srp` | `Procedure > 80 lines` | 85% | Overly large stored routine violating SRP |
| | `wide_table_god_schema_srp` | `Table >= 25 cols` | 85% | Denormalized God Table violating Single Responsibility |
| | `fat_view_interface_isp` | `View >= 6 joins` | 85% | Monolithic view interface violating ISP |

---

## ⚡ Installation & CLI Usage

```bash
# Clone repository
git clone https://github.com/bivex/DPX-SQL.git
cd DPX-SQL

# Install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### 🚀 Running Analysis

```bash
# 1. Quick scan on schema / SQL files
dpx-sql scan schema/

# 2. Export Full Interactive HTML HUD + SARIF + JSON + Markdown
dpx-sql scan database/ \
    -H reports/dpx_sql_hud.html \
    -J reports/dpx_sql_findings.json \
    -M reports/dpx_sql_report.md \
    -S reports/dpx_sql_report.sarif

# 3. View 43 supported pattern catalog
dpx-sql catalog
```

---

## 🌐 The DPX Multi-Language Static Analysis Family (28 Languages)

| # | Language | Repository | Ecosystem & Focus |
|:---:|---|---|---|
| 1 | **Clojure** | [`bivex/DPX`](https://github.com/bivex/DPX) | Lisp S-Expressions, Protocols, Multimethods |
| 2 | **C** | [`bivex/DPX-C`](https://github.com/bivex/DPX-C) | Memory Safety, Struct VTables, Idiomatic C11/C23 |
| 3 | **Cairo** | [`bivex/DPX-Cairo`](https://github.com/bivex/DPX-Cairo) | Starknet Smart Contracts, ZK-Rollup Invariants |
| 4 | **C++** | [`bivex/DPX-Cpp`](https://github.com/bivex/DPX-Cpp) | RAII, CRTP, Concepts, Modern C++20/23 |
| 5 | **C#** | [`bivex/DPX-CSharp`](https://github.com/bivex/DPX-CSharp) | .NET 9, Roslyn AST, Linq, Records |
| 6 | **Dart** | [`bivex/DPX-Dart`](https://github.com/bivex/DPX-Dart) | Dart 3.x, Flutter, BLoC, Riverpod, Isolates |
| 7 | **Elixir** | [`bivex/DPX-Elixir`](https://github.com/bivex/DPX-Elixir) | BEAM OTP, GenServer, Supervisors |
| 8 | **Erlang** | [`bivex/DPX-Erlang`](https://github.com/bivex/DPX-Erlang) | Fault Tolerance, Actor Model, OTP Behaviors |
| 9 | **Gleam** | [`bivex/DPX-Gleam`](https://github.com/bivex/DPX-Gleam) | Type-Safe BEAM, Actor Concurrency |
| 10 | **Go** | [`bivex/DPX-Go`](https://github.com/bivex/DPX-Go) | Goroutines, Channels, Composition, Interfaces |
| 11 | **Haskell** | [`bivex/DPX-Haskell`](https://github.com/bivex/DPX-Haskell) | Pure Functional, Monads, Typeclasses, Arrows |
| 12 | **Huff** | [`bivex/DPX-Huff`](https://github.com/bivex/DPX-Huff) | Low-Level EVM Bytecode & Opcodes |
| 13 | **Java** | [`bivex/DPX-Java`](https://github.com/bivex/DPX-Java) | Spring Boot, Enterprise Java, JVM Invariants |
| 14 | **Julia** | [`bivex/DPX-Julia`](https://github.com/bivex/DPX-Julia) | Multiple Dispatch, Scientific Computing |
| 15 | **Kotlin** | [`bivex/DPX-Kotlin`](https://github.com/bivex/DPX-Kotlin) | Coroutines, Multiplatform, Functional DSLs |
| 16 | **Lua** | [`bivex/DPX-Lua`](https://github.com/bivex/DPX-Lua) | Metatables, Coroutines, LuaJIT, Neovim |
| 17 | **Mojo** | [`bivex/DPX-Mojo`](https://github.com/bivex/DPX-Mojo) | SIMD Hardware, Memory Lifetimes, AI Systems |
| 18 | **Move** | [`bivex/DPX-Move`](https://github.com/bivex/DPX-Move) | Aptos & Sui Resource Safety, Linear Types |
| 19 | **OCaml** | [`bivex/DPX-OCaml`](https://github.com/bivex/DPX-OCaml) | Algebraic Data Types, Functors, Polymorphism |
| 20 | **PHP** | [`bivex/DPX-Php`](https://github.com/bivex/DPX-Php) | Modern PHP 8.4, Attributes, Traits, Laravel |
| 21 | **Python** | [`bivex/DPX-Py`](https://github.com/bivex/DPX-Py) | Metaprogramming, Protocols, Hexagonal DDD |
| 22 | **Rust** | [`bivex/DPX-Rust`](https://github.com/bivex/DPX-Rust) | Zero-Cost Abstractions, Borrow Checker, Traits |
| 23 | **Solidity** | [`bivex/DPX-Solidity`](https://github.com/bivex/DPX-Solidity) | DeFi Security, Reentrancy, EVM Yul/Assembly |
| 24 | **SQL** | [`bivex/DPX-SQL`](https://github.com/bivex/DPX-SQL) | **PostgreSQL, MySQL, SQLite, T-SQL, PL/SQL** |
| 25 | **Swift** | [`bivex/DPX-Swift`](https://github.com/bivex/DPX-Swift) | Protocol-Oriented Programming, Actors |
| 26 | **TypeScript** | [`bivex/DPX-TypeScript`](https://github.com/bivex/DPX-TypeScript) | Generics, Conditional Types, Clean Architecture |
| 27 | **Yul** | [`bivex/DPX-Yul`](https://github.com/bivex/DPX-Yul) | EVM Intermediate Representation Optimization |
| 28 | **Zig** | [`bivex/DPX-Zig`](https://github.com/bivex/DPX-Zig) | Comptime, Manual Memory Allocators, C ABI |

## 📄 License

MIT License © 2026 Bivex
