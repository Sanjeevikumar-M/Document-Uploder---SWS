from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

class DocumentResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(alias="_id")
    originalName: str
    filename: str
    path: str
    contentType: Optional[str] = "text/plain"
    size: int
    text: Optional[str] = ""
    createdAt: str

class ChatSource(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(alias="_id")
    originalName: str

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[ChatSource] = []
