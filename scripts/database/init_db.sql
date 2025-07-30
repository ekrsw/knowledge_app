-- Initialize Knowledge Revision System Database
-- Run this script to create the database and user

-- Create database (run as postgres superuser)
CREATE DATABASE knowledge_revision;

-- Create user for the application (optional, can use existing postgres user)
-- CREATE USER knowledge_user WITH ENCRYPTED PASSWORD 'your_password_here';

-- Grant privileges to the user
-- GRANT ALL PRIVILEGES ON DATABASE knowledge_revision TO knowledge_user;