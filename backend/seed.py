import os
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path

# Add backend directory to sys.path so app modules can be imported
import sys
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from app.database import get_documents_collection
from app.utils.extract_text import extract_text_from_file

FIXTURES_DIR = BASE_DIR / "seed" / "fixtures"
UPLOADS_DIR = BASE_DIR / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

CONTENT_TYPES = {
    ".txt": "text/plain",
    ".md": "text/markdown",
    ".json": "application/json"
}

def seed_database():
    """Seed initial fixture documents into MongoDB and uploads folder."""
    print("Starting database seeding...")
    collection = get_documents_collection()

    if not FIXTURES_DIR.exists():
        print(f"Fixtures directory not found at {FIXTURES_DIR}")
        return

    fixture_files = list(FIXTURES_DIR.iterdir())
    if not fixture_files:
        print("No fixture files found to seed.")
        return

    seeded_count = 0
    for file_path in fixture_files:
        if file_path.is_dir():
            continue

        original_name = file_path.name
        # Check if already seeded to avoid duplicates
        existing = collection.find_one({"originalName": original_name})
        if existing:
            print(f"[Skip] '{original_name}' already exists in database.")
            continue

        # Generate unique storage filename and copy to uploads
        ext = file_path.suffix.lower()
        unique_filename = f"seed_{uuid.uuid4().hex[:8]}_{original_name}"
        dest_path = UPLOADS_DIR / unique_filename
        shutil.copy2(file_path, dest_path)

        text_content = extract_text_from_file(str(dest_path), original_name)
        content_type = CONTENT_TYPES.get(ext, "text/plain")
        size = file_path.stat().st_size

        doc_data = {
            "originalName": original_name,
            "filename": unique_filename,
            "path": f"uploads/{unique_filename}",
            "contentType": content_type,
            "size": size,
            "text": text_content,
            "createdAt": datetime.now(timezone.utc).isoformat()
        }

        collection.insert_one(doc_data)
        print(f"[Seeded] '{original_name}' successfully inserted.")
        seeded_count += 1

    print(f"Seeding completed. {seeded_count} new documents added.")

if __name__ == "__main__":
    seed_database()
