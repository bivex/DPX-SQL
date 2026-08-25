-- ============================================================================
-- Enterprise Multi-Tenant E-Commerce & Financial Ledger SQL Schema
-- Target Dialects: PostgreSQL 16+ / ANSI SQL:2023 / Enterprise RDBMS
-- ============================================================================

-- 1. Sequences & Factory ID Generation
CREATE SEQUENCE tenant_id_seq START WITH 1000;
CREATE SEQUENCE order_id_seq START WITH 100000;

-- 2. Master System Config (Singleton Pattern)
CREATE TABLE system_parameters (
    id INT PRIMARY KEY CHECK (id = 1),
    maintenance_mode BOOLEAN DEFAULT FALSE,
    default_currency VARCHAR(3) DEFAULT 'USD',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Lookup Dictionaries (Flyweight Pattern)
CREATE TABLE order_status_dictionary (
    id INT PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    display_name VARCHAR(100) NOT NULL
);

-- 4. Multi-Tenant Tenants & Hierarchical Organizations (Composite Tree Pattern)
CREATE TABLE organizations (
    id BIGINT PRIMARY KEY DEFAULT nextval('tenant_id_seq'),
    name VARCHAR(255) NOT NULL,
    parent_id BIGINT REFERENCES organizations(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Partitioned Financial Ledger (Strategy & Partitioning Pattern)
CREATE TABLE ledger_transactions (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    organization_id BIGINT NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    account_id UUID NOT NULL,
    amount NUMERIC(18, 4) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    transaction_date DATE NOT NULL,
    status VARCHAR(50) CHECK (status IN ('PENDING', 'POSTED', 'VOID', 'RECONCILED')),
    metadata JSONB,
    PRIMARY KEY (id, transaction_date)
) PARTITION BY RANGE (transaction_date);

-- 6. Indexes: Partial, Covering, and GIN (Indexing Patterns)
CREATE INDEX idx_ledger_active_pending ON ledger_transactions (organization_id, transaction_date) WHERE status = 'PENDING';
CREATE INDEX idx_ledger_covering_acc ON ledger_transactions (account_id) INCLUDE (amount, currency);
CREATE INDEX idx_ledger_metadata_gin ON ledger_transactions USING GIN (metadata);
CREATE INDEX idx_ledger_compound ON ledger_transactions (organization_id, status, transaction_date);

-- 7. Polymorphic Entity Attachments (Bridge Pattern)
CREATE TABLE entity_attachments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    target_type VARCHAR(100) NOT NULL,
    target_id UUID NOT NULL,
    storage_uri VARCHAR(1024) NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. Transactional Outbox Task Queue (Command Pattern)
CREATE TABLE outbox_tasks (
    id BIGINT PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL,
    retry_count INT DEFAULT 0,
    locked_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 9. Staging Buffer (Proxy Pattern)
CREATE UNLOGGED TABLE staging_raw_events (
    batch_id UUID,
    raw_payload TEXT,
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 10. Temporal History Table (Memento Pattern)
CREATE TABLE account_balances_history (
    account_id UUID NOT NULL,
    balance NUMERIC(18, 4) NOT NULL,
    valid_from TIMESTAMP NOT NULL,
    valid_to TIMESTAMP NOT NULL,
    PRIMARY KEY (account_id, valid_from)
);

-- 11. Stored Procedure with Savepoint & Cursor (Template Method & Iterator)
CREATE OR REPLACE FUNCTION process_settlement_batch(target_date DATE) RETURNS void AS $$
DECLARE
    rec RECORD;
    cur_ledger CURSOR FOR 
        SELECT id, amount, account_id FROM ledger_transactions WHERE transaction_date = target_date;
BEGIN
    SAVEPOINT batch_savepoint;
    
    FOR rec IN cur_ledger LOOP
        UPDATE ledger_transactions 
        SET status = 'POSTED' 
        WHERE id = rec.id;
    END LOOP;

    PERFORM pg_notify('ledger_events', '{"status": "settled"}');
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK TO SAVEPOINT batch_savepoint;
        RAISE EXCEPTION 'Settlement failed: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- 12. Security Hazard Function: Unsanitized dynamic SQL
CREATE OR REPLACE FUNCTION query_custom_table(user_input_table TEXT) RETURNS void AS $$
BEGIN
    EXECUTE 'SELECT * FROM ' || user_input_table;
END;
$$ LANGUAGE plpgsql;

-- 13. Decorator / Observer Trigger
CREATE OR REPLACE TRIGGER trg_ledger_audit AFTER INSERT OR UPDATE ON ledger_transactions
FOR EACH ROW EXECUTE FUNCTION notify_audit_stream();

-- 14. Materialized View & Facade View
CREATE MATERIALIZED VIEW mv_daily_financial_summary AS
SELECT 
    l.organization_id,
    o.name AS organization_name,
    l.transaction_date,
    SUM(l.amount) AS total_volume,
    COUNT(l.id) AS tx_count
FROM ledger_transactions l
JOIN organizations o ON o.id = l.organization_id
GROUP BY l.organization_id, o.name, l.transaction_date;

CREATE VIEW v_organization_full_tree AS
SELECT 
    o.id,
    o.name,
    parent.name AS parent_name,
    s.total_volume
FROM organizations o
LEFT JOIN organizations parent ON parent.id = o.parent_id
LEFT JOIN mv_daily_financial_summary s ON s.organization_id = o.id;

-- 15. Advanced Idiomatic Queries
WITH RECURSIVE org_hierarchy AS (
    SELECT id, name, parent_id, 1 AS depth, ARRAY[id] AS visited
    FROM organizations
    WHERE parent_id IS NULL
    UNION ALL
    SELECT o.id, o.name, o.parent_id, h.depth + 1, h.visited || o.id
    FROM organizations o
    JOIN org_hierarchy h ON o.parent_id = h.id
)
SELECT id, name, depth, ROW_NUMBER() OVER (PARTITION BY parent_id ORDER BY id) AS rank_in_parent
FROM org_hierarchy;

-- 16. Upsert & Lateral Join & Deadlock Prone Lock Query
INSERT INTO system_parameters (id, default_currency) 
VALUES (1, 'EUR') 
ON CONFLICT (id) DO UPDATE SET default_currency = EXCLUDED.default_currency;

SELECT l.id, sub.tx_count
FROM ledger_transactions l
CROSS JOIN LATERAL (
    SELECT COUNT(*) AS tx_count FROM outbox_tasks WHERE created_at >= l.transaction_date
) sub;

SELECT * FROM ledger_transactions WHERE status = 'PENDING' FOR UPDATE;
