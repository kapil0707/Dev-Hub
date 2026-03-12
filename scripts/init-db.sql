-- =============================================================================
-- Universal Dev-Hub — Initial Database Setup
-- =============================================================================
-- PURPOSE: This script runs automatically on first PostgreSQL container start.
-- It creates separate schemas for each microservice for logical isolation.
--
-- WHY SCHEMAS (not separate databases)?
-- On a local dev machine, running 5 separate PostgreSQL databases would waste
-- resources. Instead, we use one database with separate schemas per service.
-- Each service only gets access to its own schema — same isolation, less overhead.
-- In production, you would typically use separate database instances per service.
-- =============================================================================

-- Create schemas for each microservice
CREATE SCHEMA IF NOT EXISTS identity;
CREATE SCHEMA IF NOT EXISTS snippets;
CREATE SCHEMA IF NOT EXISTS automation;
CREATE SCHEMA IF NOT EXISTS blob_storage;
CREATE SCHEMA IF NOT EXISTS analytics;

-- Create a dedicated role for each service (least-privilege principle)
-- In production, each service would have its own DB user with only the
-- permissions it needs (no cross-schema access).
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'identity_svc') THEN
        CREATE ROLE identity_svc WITH LOGIN PASSWORD 'identity_pass_local';
    END IF;
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'snippet_svc') THEN
        CREATE ROLE snippet_svc WITH LOGIN PASSWORD 'snippet_pass_local';
    END IF;
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'automation_svc') THEN
        CREATE ROLE automation_svc WITH LOGIN PASSWORD 'automation_pass_local';
    END IF;
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'blob_svc') THEN
        CREATE ROLE blob_svc WITH LOGIN PASSWORD 'blob_pass_local';
    END IF;
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'analytics_svc') THEN
        CREATE ROLE analytics_svc WITH LOGIN PASSWORD 'analytics_pass_local';
    END IF;
END
$$;

-- Grant each role access ONLY to its own schema
GRANT USAGE ON SCHEMA identity TO identity_svc;
GRANT CREATE ON SCHEMA identity TO identity_svc;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA identity TO identity_svc;

GRANT USAGE ON SCHEMA snippets TO snippet_svc;
GRANT CREATE ON SCHEMA snippets TO snippet_svc;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA snippets TO snippet_svc;

GRANT USAGE ON SCHEMA automation TO automation_svc;
GRANT CREATE ON SCHEMA automation TO automation_svc;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA automation TO automation_svc;

GRANT USAGE ON SCHEMA blob_storage TO blob_svc;
GRANT CREATE ON SCHEMA blob_storage TO blob_svc;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA blob_storage TO blob_svc;

GRANT USAGE ON SCHEMA analytics TO analytics_svc;
GRANT CREATE ON SCHEMA analytics TO analytics_svc;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA analytics TO analytics_svc;

-- NOTE: The actual tables (users, snippets, files, executions, events) are
-- created by Alembic migrations in Phase 1+. This script only sets up
-- the structural prerequisites.
