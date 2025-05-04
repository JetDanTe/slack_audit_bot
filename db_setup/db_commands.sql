CREATE USER slack_audit WITH PASSWORD 'slack_audit';

CREATE DATABASE slack_audit;

-- Grant CONNECT privilege on the database
GRANT CONNECT ON DATABASE slack_audit TO slack_audit;

-- Connect to the specific database
\c slack_audit

-- Grant USAGE on schema
GRANT USAGE, CREATE ON SCHEMA public TO slack_audit;

-- Grant SELECT, INSERT, UPDATE, REFERENCES privileges on all existing tables
GRANT SELECT, INSERT, UPDATE, REFERENCES ON ALL TABLES IN SCHEMA public TO slack_audit;

-- Grant USAGE, SELECT on all sequences
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO slack_audit;

-- Grant EXECUTE on all functions
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO slack_audit;

ALTER SCHEMA public OWNER TO slack_audit;

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, REFERENCES ON TABLES TO slack_audit;

-- Set default privileges for future sequences
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO slack_audit;

-- Set default privileges for future functions
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT EXECUTE ON FUNCTIONS TO slack_audit;

CREATE TABLE USERS (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    real_name VARCHAR(255) NOT NULL,
    is_deleted BOOLEAN DEFAULT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    is_ignore BOOLEAN DEFAULT FALSE
);