import io


def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    body = r.json()
    assert body["message"] == "Ai-Tutor Backend API"


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "healthy"
    assert "services" in body
    assert body["services"]["vector_db"] == "healthy"


def test_chat(client):
    payload = {"message": "What is web development?", "user_id": "u1"}
    r = client.post("/api/chat", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["query"] == payload["message"]
    assert body["status"] == "success"
    assert isinstance(body["response"], str)


def test_upload_file(client):
    file_content = b"Hello file upload test"
    files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}
    r = client.post("/api/upload", files=files)
    assert r.status_code == 200
    body = r.json()
    assert body["filename"] == "test.txt"
    assert body["status"] == "success"
    assert isinstance(body["chunks_created"], int)


def test_upload_direct(client):
    data = {
        "text": "Direct content",
        "filename": "direct.txt",
        "file_type": "text",
        "source": "direct_upload",
    }
    r = client.post("/api/upload-direct", data=data)
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "success"
    assert body["filename"] == "direct.txt"


def test_upload_text(client):
    data = {
        "content": "Some educational content",
        "title": "My Title",
        "description": "desc",
        "category": "general",
    }
    r = client.post("/api/upload-text", data=data)
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "success"
    assert body["title"] == "My Title"
    assert body["filename"] == "my_title.txt"


def test_list_documents(client):
    r = client.get("/api/documents")
    assert r.status_code == 200
    body = r.json()
    assert "documents" in body
    assert isinstance(body["documents"], list)
    assert body["documents"][0]["filename"] == "doc1.txt"


def test_db_stats(client):
    r = client.get("/api/db-stats")
    assert r.status_code == 200
    body = r.json()
    assert "documents" in body
    assert "chunks" in body


def test_test_db(client):
    r = client.get("/api/test-db")
    assert r.status_code == 200
    body = r.json()
    assert "tests" in body
    assert body["overall_status"] in ("passed", "partial", "failed")


def test_test_query(client):
    payload = {"message": "Ping", "user_id": "u1"}
    r = client.post("/api/test-query", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["test_status"] in ("success", "error")
    assert body["query"] == "Ping"


def test_delete_document(client):
    r = client.delete("/api/documents/123")
    assert r.status_code == 200
    body = r.json()
    assert "deleted successfully" in body["message"]


def test_backup_db(client):
    r = client.post("/api/backup-db")
    assert r.status_code == 200
    body = r.json()
    assert "backup_path" in body
    assert body["message"] == "Database backup created successfully"


def test_reset_db(client):
    r = client.post("/api/reset-db")
    assert r.status_code == 200
    body = r.json()
    assert body["message"] == "Database reset successfully"


