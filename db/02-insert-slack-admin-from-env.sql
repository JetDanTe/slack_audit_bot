-- This approach uses psql variables to insert admin user
-- The variables are set from environment variables when this script runs

-- Insert admin user with ON CONFLICT to handle re-runs
INSERT INTO users (id, name, real_name, is_deleted, is_admin, is_ignore)
VALUES (:'admin_slack_id', :'admin_name', :'admin_real_name', false, true, false)
ON CONFLICT (id)
DO UPDATE SET
    name = EXCLUDED.name,
    real_name = EXCLUDED.real_name,
    is_admin = true,
    is_deleted = false,
    is_ignore = false;

-- Verify admin user was created
SELECT id, name, real_name, is_admin FROM users WHERE is_admin = true;