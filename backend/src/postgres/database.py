import asyncpg
import logging

logger = logging.getLogger(__name__)

# dropdb -U sam "fastapi_docker-compose"
# createdb -U sam -h localhost "my-new-database"
DATABASE_URL = "postgresql://sam:1234@localhost:5432/fastapi_docker-compose"

SCHEMA = """--sql
-- Users table to store user information
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    hashed_password TEXT NOT NULL
);

-- Documents table with foreign key reference to users
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    CONSTRAINT fk_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents(user_id);
"""


class Postgres:
    def __init__(self, database_url: str):
        self.database_url = database_url

    async def connect(self):
        self.pool = await asyncpg.create_pool(self.database_url)

    async def initialize_schema(self) -> None:
        """Initialize the database schema."""
        if not self.pool:
            await self.connect()
        try:
            async with self.pool.acquire() as conection:
                await conection.execute(SCHEMA)
                logger.info("Database schema initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database schema: {e}")
            raise

    async def disconnect(self):
        await self.pool.close()


database = Postgres(DATABASE_URL)
