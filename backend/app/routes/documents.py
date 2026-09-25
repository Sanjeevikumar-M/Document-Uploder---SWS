import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from ..database import get_documents_collection, serialize_doc
from ..models.document import DocumentResponse
from ..utils.extract_text import extract_text_from_bytes, is_supported_format

router = APIRouter(prefix="/api/documents", tags=["Documents"])

UPLOADS_DIR = Path(__file__).resolve().parent.parent.parent / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

@router.get("", response_model=List[DocumentResponse])
def get_documents():
    """Retrieve all documents sorted newest first."""
    collection = get_documents_collection()
    cursor = collection.find().sort("createdAt", -1)
    docs = [serialize_doc(doc) for doc in cursor]
    return docs

@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(file: UploadFile = File(...)):
    """Upload a document, save to disk, extract text, and store metadata in MongoDB."""
    if not file or not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )

    if not is_supported_format(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format. Supported formats are: .txt, .md, .json"
        )

    try:
        content = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read file: {e}"
        )

    # Extract text from content
    try:
        extracted_text = extract_text_from_bytes(content, file.filename)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Text extraction failed: {e}"
        )

    # Generate safe unique filename
    safe_name = Path(file.filename).name.replace(" ", "_")
    unique_filename = f"{uuid.uuid4().hex[:8]}_{safe_name}"
    file_path = UPLOADS_DIR / unique_filename

    # Save to disk
    with open(file_path, "wb") as f:
        f.write(content)

    doc_data = {
        "originalName": file.filename,
        "filename": unique_filename,
        "path": f"uploads/{unique_filename}",
        "contentType": file.content_type or "text/plain",
        "size": len(content),
        "text": extracted_text,
        "createdAt": datetime.now(timezone.utc).isoformat()
    }

    collection = get_documents_collection()
    result = collection.insert_one(doc_data)
    doc_data["_id"] = str(result.inserted_id)

    return doc_data

@router.delete("/{doc_id}")
def delete_document(doc_id: str):
    """Delete a document by ID and remove its file from disk."""
    try:
        obj_id = ObjectId(doc_id)
    except InvalidId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid document ID format"
        )

    collection = get_documents_collection()
    doc = collection.find_one({"_id": obj_id})
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # Delete local file if it exists
    filename = doc.get("filename")
    if filename:
        file_path = UPLOADS_DIR / filename
        if file_path.exists():
            try:
                os.remove(file_path)
            except OSError:
                pass

    collection.delete_one({"_id": obj_id})
    return {"message": "Document deleted successfully", "id": doc_id}

@router.get("/{doc_id}/download")
def download_document(doc_id: str):
    """Download a stored document by its ID."""
    try:
        obj_id = ObjectId(doc_id)
    except InvalidId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid document ID format"
        )

    collection = get_documents_collection()
    doc = collection.find_one({"_id": obj_id})
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    filename = doc.get("filename")
    if not filename:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File path missing")

    file_path = UPLOADS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found on disk")

    return FileResponse(
        path=str(file_path),
        filename=doc.get("originalName", filename),
        media_type=doc.get("contentType", "application/octet-stream")
    )
