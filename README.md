# Document Uploader & AI Assistant

A lightweight, full-stack document management and question-answering application built with **React 18 + Vite**, **Python + FastAPI**, and **MongoDB Atlas**.

---

## 🚀 Overview

The **Document Uploader** system allows users to upload, view, download, and delete text documents (`.txt`, `.md`, `.json`), automatically extracting their text content and storing metadata in MongoDB. It features a built-in **AI Document Assistant (Chatbot)** that ranks relevant documents using keyword overlap and answers questions with cited document sources.

---

## ✨ Features

- **Document Upload**:
  - Drag-and-drop or file browser interface.
  - Supports `.txt`, `.md`, and `.json` formats with validation.
  - Automatically extracts content and generates safe unique filenames.
- **Document Management**:
  - View all uploaded documents sorted newest first.
  - Toggle live text previews directly from the dashboard.
  - Download original files or delete documents (removes record from MongoDB and disk).
- **AI Document Assistant (Chatbot)**:
  - Answers user questions grounded in uploaded documents.
  - Automatic keyword overlap scoring and relevance ranking.
  - Generates clear answers and cites the source documents used.
  - Works out of the box without requiring external API keys (with optional OpenAI support).
- **Interactive API Documentation**:
  - Automatically generated Swagger UI at `/docs` (and `/api/docs`).
  - OpenAPI 3.0 JSON specification at `/openapi.json` (and `/api/openapi.json`).
- **Comprehensive Test Suite**:
  - 100% passing tests using `pytest` and `FastAPI TestClient`.

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 18, Vite, Lucide Icons, CSS3 |
| **Backend** | Python 3.11+, FastAPI, Uvicorn |
| **Database** | MongoDB Atlas / PyMongo (with resilient fallback) |
| **File Storage** | Local filesystem (`backend/uploads/`) |
| **API Docs** | Swagger UI & OpenAPI |
| **Testing** | Pytest, FastAPI TestClient, HTTPX |

---

## 📁 Project Structure

```text
Document Uploader/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app instance, CORS & Swagger routes
│   │   ├── database.py          # MongoDB Atlas client & connection helper
│   │   ├── models/
│   │   │   └── document.py      # Pydantic schemas (Document, Chat, Sources)
│   │   ├── routes/
│   │   │   ├── documents.py     # GET, POST, DELETE, DOWNLOAD endpoints
│   │   │   └── chat.py          # POST /api/chat endpoint
│   │   ├── services/
│   │   │   └── chat_service.py  # Keyword ranking & document retrieval logic
│   │   └── utils/
│   │       ├── extract_text.py  # Text parser for .txt, .md, .json
│   │       └── llm.py           # Context synthesis & LLM answering
│   ├── seed/
│   │   └── fixtures/            # Initial sample documents
│   │       ├── expense-policy.txt
│   │       ├── project-brief.txt
│   │       └── welcome.md
│   ├── tests/
│   │   └── test_documents.py    # Pytest test suite for all endpoints
│   ├── uploads/                 # Local uploaded files storage
│   ├── .env                     # Backend environment configuration
│   ├── requirements.txt         # Python dependencies
│   └── seed.py                  # Script to seed database from fixtures
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Chatbot.jsx      # Interactive chat UI with source tags
│   │   │   ├── DocumentList.jsx # Table with preview, download, delete
│   │   │   └── UploadForm.jsx   # Drag-and-drop file upload form
│   │   ├── api.js               # API service connecting to FastAPI
│   │   ├── App.jsx              # Main layout dashboard
│   │   ├── index.css            # Modern styling and responsive layout
│   │   └── main.jsx             # React entry point
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── package.json                 # Root npm workspace configuration
└── README.md
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/documents` | Retrieve all documents (sorted newest first) |
| `POST` | `/api/documents` | Upload a file (`multipart/form-data`, field: `file`) |
| `DELETE` | `/api/documents/{id}` | Delete document from MongoDB and disk |
| `GET` | `/api/documents/{id}/download` | Download the stored original file |
| `POST` | `/api/chat` | Ask questions about uploaded documents |
| `GET` | `/docs` or `/api/docs` | Interactive Swagger UI API documentation |
| `GET` | `/openapi.json` | Raw OpenAPI specification |

### Sample Chat Request & Response

**Request (`POST /api/chat`):**
```json
{
  "question": "What is the daily meal allowance?"
}
```

**Response (`200 OK`):**
```json
{
  "answer": "Based on expense-policy.txt, here is the relevant information:\n\n- Daily meal allowance is 40 USD for domestic travel and 65 USD for international travel. Alcohol is not reimbursable.",
  "sources": [
    {
      "_id": "66f3e1a0b32...",
      "originalName": "expense-policy.txt"
    }
  ]
}
```

---

## 🚦 Getting Started

### Prerequisites

- **Python**: 3.11 or higher
- **Node.js**: v18.0.0 or higher
- **MongoDB**: MongoDB Atlas URI or local MongoDB instance

---

### 1. Installation

#### Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Frontend Setup
```bash
# In the root directory or frontend directory
npm install
```

---

### 2. Environment Configuration

Create a `.env` file inside `backend/`:
```env
MONGO_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
MONGO_DB_NAME=document_uploader
PORT=4000
UPLOADS_DIR=uploads
```

---

### 3. Seed Sample Data (Optional)

To seed initial documents (`expense-policy.txt`, `project-brief.txt`, `welcome.md`):
```bash
python backend/seed.py
```

---

### 4. Running the Application

#### Start Backend (Port 4000)
```bash
backend\.venv\Scripts\python -m uvicorn app.main:app --host 0.0.0.0 --port 4000 --app-dir backend
```
- API Base: `http://localhost:4000`
- Swagger Docs: `http://localhost:4000/docs`

#### Start Frontend (Port 3000)
```bash
# From the root directory:
npm run dev -w frontend

# Or from frontend/ directory:
npm run dev
```
- Frontend UI: `http://localhost:3000`

---

## 🧪 Running Tests

The application includes unit and integration tests using `pytest` and FastAPI's `TestClient`:

```bash
# Run tests from the project root
backend\.venv\Scripts\pytest backend\tests -v
```

All 7 test suites cover:
- Document listing (`GET /api/documents`)
- Document upload and text extraction (`POST /api/documents`)
- Validation of unsupported file types (returns HTTP 400)
- Document deletion and cleanup (`DELETE /api/documents/{id}`)
- Error handling for missing IDs (returns HTTP 404)
- Empty question validation in chat (returns HTTP 400)
- Keyword-based retrieval and answer generation in chat (`POST /api/chat`)

---

## 📄 License

This project is licensed under the MIT License.