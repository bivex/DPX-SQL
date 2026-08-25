import pytest
from pattern_detector.adapters.inbound.parsers.sql_parser import RegexSqlParser
from pattern_detector.adapters.inbound.detectors.sql_detector import SqlPatternDetector
from pattern_detector.domain.value_objects import PatternType


SAMPLE_RULES_SQL = """
-- Idiomatic & Indexes
CREATE SEQUENCE user_seq;
CREATE TABLE users (
    id BIGINT PRIMARY KEY DEFAULT nextval('user_seq'),
    email VARCHAR(255) NOT NULL,
    status VARCHAR(50) CHECK (status IN ('ACTIVE', 'BANNED', 'SUSPENDED')),
    role_id INT NOT NULL REFERENCES roles(id) ON DELETE CASCADE
);

CREATE TABLE roles (
    id INT PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

CREATE INDEX idx_users_status ON users (status) WHERE status = 'ACTIVE';
CREATE INDEX idx_users_role_status ON users (role_id, status);

CREATE MATERIALIZED VIEW mv_user_stats AS
SELECT role_id, COUNT(*) FROM users GROUP BY role_id;

CREATE UNLOGGED TABLE staging_buffer (
    id UUID PRIMARY KEY,
    data TEXT
);

CREATE TABLE outbox_tasks (
    id BIGINT PRIMARY KEY,
    payload JSONB,
    created_at TIMESTAMP
);

CREATE OR REPLACE FUNCTION bad_dynamic_proc(table_name TEXT) RETURNS void AS $$
BEGIN
    -- Security Hazard: Dynamic concatenation
    EXECUTE 'SELECT * FROM ' || table_name;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trg_user_audit AFTER INSERT OR UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION notify_user_audit();

-- Queries
WITH RECURSIVE cat_tree AS (
    SELECT id, parent_id, 1 AS depth FROM categories WHERE parent_id IS NULL
    UNION ALL
    SELECT c.id, c.parent_id, ct.depth + 1 FROM categories c JOIN cat_tree ct ON c.parent_id = ct.id
)
SELECT * FROM cat_tree;

SELECT id, ROW_NUMBER() OVER (ORDER BY id) FROM users;
SELECT * FROM users ON CONFLICT (id) DO NOTHING;
SELECT * FROM users JOIN LATERAL (SELECT * FROM roles WHERE roles.id = users.role_id) r ON true;
SELECT * FROM users WHERE id = 1 FOR UPDATE;
"""


def test_rule_evaluations():
    parser = RegexSqlParser()
    sql_file = parser.parse_file("rules_test.sql", SAMPLE_RULES_SQL)
    
    from pattern_detector.domain.code_model import CodeModel
    model = CodeModel()
    model.add_file(sql_file)

    detector = SqlPatternDetector()
    report = detector.detect(model)

    detected_types = {d.pattern_type for d in report.detections}

    # Verify Idiomatic Detections
    assert PatternType.RECURSIVE_CTE_HIERARCHY in detected_types
    assert PatternType.WINDOW_FUNCTION_ANALYTICS in detected_types
    assert PatternType.UPSERT_MERGE_IDEMPOTENCY in detected_types
    assert PatternType.MATERIALIZED_VIEW_CACHE in detected_types
    assert PatternType.LATERAL_JOIN_SUBQUERY in detected_types

    # Verify Indexing & Schema
    assert PatternType.PARTIAL_CONDITIONAL_INDEX in detected_types
    assert PatternType.COMPOSITE_MULTI_COLUMN_INDEX in detected_types
    assert PatternType.FOREIGN_KEY_CASCADE_TREE in detected_types

    # Verify Procedural & Creational & Structural & Behavioral
    assert PatternType.STORED_PROCEDURE_ROUTER in detected_types
    assert PatternType.TRIGGER_EVENT_INTERCEPTOR in detected_types
    assert PatternType.TRANSACTION_ISOLATION_GUARD in detected_types
    assert PatternType.FACTORY_SEQUENCE_ID_GENERATOR in detected_types
    assert PatternType.PROXY_STAGED_LANDING_TABLE in detected_types
    assert PatternType.COMMAND_ACTION_QUEUE_TABLE in detected_types
    assert PatternType.STATE_MACHINE_STATUS_CONSTRAINT in detected_types
    assert PatternType.OBSERVER_TRIGGER_AUDIT_BROADCAST in detected_types

    # Verify Security Hazard
    assert PatternType.SQL_INJECTION_DYNAMIC_CONCAT_HAZARD in detected_types
    assert PatternType.DEADLOCK_PRONE_LOCK_ORDERING_HAZARD in detected_types
