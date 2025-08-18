-- Create test user and database for CI/CD
CREATE USER test_user WITH PASSWORD 'test_pass';
CREATE DATABASE test_db OWNER test_user;
GRANT ALL PRIVILEGES ON DATABASE test_db TO test_user;

-- Also create a test database for the main user
CREATE DATABASE fast_zero_test OWNER fast_zero_user;
GRANT ALL PRIVILEGES ON DATABASE fast_zero_test TO fast_zero_user;