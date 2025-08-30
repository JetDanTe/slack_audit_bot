-- Create users table matching your SQLAlchemy model
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR PRIMARY KEY NOT NULL,
    name VARCHAR NOT NULL,
    real_name VARCHAR NOT NULL,
    is_deleted BOOLEAN,
    is_admin BOOLEAN DEFAULT FALSE,
    is_ignore BOOLEAN DEFAULT FALSE
);
