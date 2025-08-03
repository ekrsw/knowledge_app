-- Fix alembic version table
DELETE FROM alembic_version;
INSERT INTO alembic_version (version_num) VALUES ('5c5e57c2a070');