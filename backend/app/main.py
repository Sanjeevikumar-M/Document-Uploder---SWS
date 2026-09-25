from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from .routes.documents import router as documents_router
from .routes.chat import router as chat_router

app = FastAPI(
    title="Document Uploader API",
    description="Full-stack Document Management and AI Q&A Assistant API",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(documents_router)
app.include_router(chat_router)

# Aliases for Swagger and OpenAPI per task specification
@app.get("/", include_in_schema=False)
def root_redirect():
    """Redirect root to interactive Swagger UI documentation."""
    return RedirectResponse(url="/docs")

@app.get("/api/docs", include_in_schema=False)
def api_docs_redirect():
    """Alias for Swagger UI documentation."""
    return RedirectResponse(url="/docs")

@app.get("/api/openapi.json", include_in_schema=False)
def api_openapi_json():
    """Alias for raw OpenAPI specification."""
    return app.openapi()
