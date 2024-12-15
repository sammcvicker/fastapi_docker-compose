from postgres.database import database
from documents.documents_schema import Document


async def insert_document(user_id: int, title: str) -> Document:
    query = "INSERT INTO documents (user_id, title) VALUES ($1, $2) RETURNING id, user_id, title"
    async with database.pool.acquire() as connection:
        row = await connection.fetchrow(query, user_id, title)
        return Document(id=row["id"], user_id=row["user_id"], title=row["title"])


async def get_documents_by_user_id(user_id: int) -> list[Document]:
    query = "SELECT id, user_id, title, content FROM documents WHERE user_id = $1"
    async with database.pool.acquire() as connection:
        rows = await connection.fetch(query, user_id)
        return [
            Document(
                id=row["id"],
                user_id=row["user_id"],
                title=row["title"],
                content=row["content"],
            )
            for row in rows
        ]


async def edit_document(
    user_id: int, document_id: int, title: str, content: str
) -> Document:
    query = "UPDATE documents SET title = $1, content = $2 WHERE id = $3 AND user_id = $4 RETURNING id, user_id, title, content"
    async with database.pool.acquire() as connection:
        row = await connection.fetchrow(query, title, content, document_id, user_id)
        return Document(
            id=row["id"],
            user_id=row["user_id"],
            title=row["title"],
            content=row["content"],
        )
