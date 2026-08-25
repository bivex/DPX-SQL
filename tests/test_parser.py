import pytest
from pattern_detector.adapters.inbound.parsers.sql_parser import RegexSqlParser


SAMPLE_SQL = """
CREATE SEQUENCE user_id_seq START WITH 1;

CREATE TABLE organizations (
    id BIGINT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    parent_id BIGINT REFERENCES organizations(id) ON DELETE CASCADE
);

CREATE UNLOGGED TABLE staging_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    payload JSONB NOT NULL,
    status VARCHAR(50) CHECK (status IN ('PENDING', 'PROCESSED', 'FAILED'))
);

CREATE INDEX idx_org_parent ON organizations (parent_id) WHERE parent_id IS NOT NULL;
CREATE INDEX idx_events_payload ON staging_events USING GIN (payload);
CREATE INDEX idx_events_covering ON staging_events (status) INCLUDE (payload);

CREATE MATERIALIZED VIEW mv_org_summary AS
SELECT o.id, o.name, COUNT(sub.id) AS sub_count
FROM organizations o
LEFT JOIN organizations sub ON sub.parent_id = o.id
GROUP BY o.id, o.name;

CREATE OR REPLACE FUNCTION process_task(task_id BIGINT) RETURNS void AS $$
DECLARE
    cur CURSOR FOR SELECT * FROM staging_events;
BEGIN
    SAVEPOINT sp1;
    EXECUTE 'SELECT count(*) FROM ' || 'dynamic_tbl';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trg_audit_org AFTER INSERT OR UPDATE ON organizations
FOR EACH ROW EXECUTE FUNCTION notify_audit_log();

WITH RECURSIVE org_tree AS (
    SELECT id, parent_id, 1 AS depth FROM organizations WHERE parent_id IS NULL
    UNION ALL
    SELECT o.id, o.parent_id, ot.depth + 1 FROM organizations o JOIN org_tree ot ON o.parent_id = ot.id
)
SELECT * FROM org_tree;

SELECT id, name, ROW_NUMBER() OVER (PARTITION BY parent_id ORDER BY id) FROM organizations;
"""


def test_regex_sql_parser():
    parser = RegexSqlParser()
    sql_file = parser.parse_file("schema.sql", SAMPLE_SQL)

    assert len(sql_file.sequences) == 1
    assert sql_file.sequences[0] == "user_id_seq"

    assert len(sql_file.tables) == 2
    orgs_tbl = next(t for t in sql_file.tables if t.name == "organizations")
    assert len(orgs_tbl.columns) >= 3
    assert len(orgs_tbl.foreign_keys) >= 1
    assert orgs_tbl.foreign_keys[0]["to_table"] == "organizations"

    stg_tbl = next(t for t in sql_file.tables if t.name == "staging_events")
    assert stg_tbl.is_unlogged is True
    assert len(stg_tbl.check_constraints) >= 1

    assert len(sql_file.indexes) == 3
    gin_idx = next(i for i in sql_file.indexes if i.name == "idx_events_payload")
    assert gin_idx.index_type == "GIN"

    partial_idx = next(i for i in sql_file.indexes if i.name == "idx_org_parent")
    assert partial_idx.is_partial is True

    inc_idx = next(i for i in sql_file.indexes if i.name == "idx_events_covering")
    assert "payload" in inc_idx.includes

    assert len(sql_file.views) == 1
    assert sql_file.views[0].is_materialized is True

    assert len(sql_file.functions) == 1
    fn = sql_file.functions[0]
    assert fn.name == "process_task"
    assert fn.has_dynamic_exec is True
    assert fn.has_cursor is True
    assert fn.has_savepoint is True

    assert len(sql_file.triggers) == 1
    trg = sql_file.triggers[0]
    assert trg.name == "trg_audit_org"
    assert trg.timing == "AFTER"
    assert "INSERT" in trg.events

    assert len(sql_file.queries) >= 2
    rec_q = next((q for q in sql_file.queries if q.has_recursive_cte), None)
    assert rec_q is not None

    win_q = next((q for q in sql_file.queries if q.has_window_func), None)
    assert win_q is not None
