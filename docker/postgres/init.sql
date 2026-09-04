-- Active Chess Database Initialization Script

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Note: Database tables will be created by the backend application using SQLAlchemy
-- The backend will create all necessary tables (users, courses, enrollments, etc.)
-- on first startup via Base.metadata.create_all()

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO chess_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO chess_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO chess_user;
