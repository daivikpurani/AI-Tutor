import json
import io
import pytest
from fastapi.testclient import TestClient

# Import the FastAPI app module
import backend_python.main as main_app


class FakeVectorDB:
    async def health_check(self):
        return "healthy"

    async def add_documents(self, chunks, filename):
        return True

    async def add_document_direct(self, text: str, filename: str, metadata: dict):
        return True

    async def list_documents(self):
        return [
            {"filename": "doc1.txt", "chunk_count": 3, "file_type": "text", "total_size": 123},
            {"filename": "doc2.txt", "chunk_count": 2, "file_type": "text", "total_size": 456},
        ]

    async def get_database_stats(self):
        return {
            "documents": 2,
            "chunks": 5,
            "last_updated": "2024-01-01T00:00:00",
            "collections": [{"name": "default", "count": 5}],
        }

    async def search_similar(self, query: str, n_results: int = 5):
        return [
            {
                "text": f"Relevant content for {query}",
                "metadata": {"filename": "doc1.txt"},
                "distance": 0.5,
            }
        ]

    async def delete_document(self, document_id: str):
        return True

    async def backup_database(self, backup_path: str):
        return True

    async def reset_database(self):
        return True


class FakeQueryHandler:
    async def process_query(self, query: str, user_id: str = None, conversation_history=None, mode: str = "exploration"):
        return {
            "response": f"Echo: {query}",
            "query": query,
            "user_id": user_id,
            "timestamp": "2024-01-01T00:00:00",
            "context_chunks_used": 1,
            "status": "success",
        }

    async def process_query_with_metadata(self, query: str, user_id: str = None, conversation_history=None, mode: str = "exploration"):
        return {
            "response": f"Echo: {query}",
            "query": query,
            "user_id": user_id,
            "timestamp": "2024-01-01T00:00:00",
            "context_chunks_used": 1,
            "status": "success",
            "llm_provider": "mock",
            "llm_model": "mock",
            "llm_usage": {},
            "llm_metadata": {},
            "citations": [],
            "tldr": f"Echo: {query}"[:160],
        }

    async def process_query_streaming(self, query: str, user_id: str = None, websocket=None, manager=None, mode: str = "exploration"):
        await manager.send_personal_message(json.dumps({
            "type": "chunk",
            "content": "Hello ",
            "timestamp": "2024-01-01T00:00:00"
        }), websocket)
        await manager.send_personal_message(json.dumps({
            "type": "chunk",
            "content": "World",
            "timestamp": "2024-01-01T00:00:00"
        }), websocket)
        await manager.send_personal_message(json.dumps({
            "type": "complete",
            "message": "Response complete",
            "timestamp": "2024-01-01T00:00:00"
        }), websocket)


@pytest.fixture(scope="session")
def app():
    # Monkeypatch globals in main to use fakes
    main_app.vector_db = FakeVectorDB()
    main_app.query_handler = FakeQueryHandler()
    return main_app.app


@pytest.fixture()
def client(app):
    with TestClient(app) as c:
        yield c


