-- Initialize database for JurChat
CREATE DATABASE IF NOT EXISTS jurchat;

-- Create user if not exists
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'jurchat_user') THEN

      CREATE ROLE jurchat_user LOGIN PASSWORD 'jurchat_password';
   END IF;
END
$do$;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE jurchat TO jurchat_user;

-- Create extensions
\c jurchat;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
