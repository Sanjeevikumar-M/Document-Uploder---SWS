import io
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.main import app

client = TestClient(app)

def test_get_documents():
    """Test retrieving documents list."""
    response = client.get("/api/documents")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_upload_valid_document():
    """Test uploading a valid text document."""
    file_content = b"This is a test document content for testing uploads."
    files = {
        "file": ("test_doc.txt", io.BytesIO(file_content), "text/plain")
    }
    response = client.post("/api/documents", files=files)
    assert response.status_code == 201
    data = response.json()
    assert "_id" in data
    assert data["originalName"] == "test_doc.txt"
    assert "test document content" in data["text"]

    # Cleanup the test document
    doc_id = data["_id"]
    del_res = client.delete(f"/api/documents/{doc_id}")
    assert del_res.status_code == 200

def test_upload_invalid_extension():
    """Test that unsupported file types are rejected with 400."""
    files = {
        "file": ("binary_doc.exe", io.BytesIO(b"MZ\x90\x00"), "application/octet-stream")
    }
    response = client.post("/api/documents", files=files)
    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]

def test_delete_document():
    """Test creating and then deleting a document."""
    # First create
    files = {
        "file": ("to_delete.md", io.BytesIO(b"# Heading\nContent to be removed"), "text/markdown")
    }
    create_res = client.post("/api/documents", files=files)
    assert create_res.status_code == 201
    doc_id = create_res.json()["_id"]

    # Now delete
    delete_res = client.delete(f"/api/documents/{doc_id}")
    assert delete_res.status_code == 200
    assert delete_res.json()["id"] == doc_id

    # Trying to delete again should return 404
    second_delete = client.delete(f"/api/documents/{doc_id}")
    assert second_delete.status_code == 404

def test_delete_invalid_id():
    """Test deleting with malformed ObjectId returns 400."""
    response = client.delete("/api/documents/invalid-id-123")
    assert response.status_code == 400

def test_chat_empty_question():
    """Test that empty chat question returns 400."""
    response = client.post("/api/chat", json={"question": ""})
    assert response.status_code == 400

    response_spaces = client.post("/api/chat", json={"question": "   "})
    assert response_spaces.status_code == 400

def test_chat_valid_question():
    """Test asking a question about uploaded documents."""
    # Upload a document first
    content = b"Our expense policy allows 50 USD meal allowance per day."
    files = {
        "file": ("policy_chat.txt", io.BytesIO(content), "text/plain")
    }
    upload_res = client.post("/api/documents", files=files)
    assert upload_res.status_code == 201
    doc_id = upload_res.json()["_id"]

    try:
        response = client.post("/api/chat", json={"question": "What is the meal allowance?"})
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert isinstance(data["sources"], list)
        assert len(data["sources"]) > 0
    finally:
        client.delete(f"/api/documents/{doc_id}")
