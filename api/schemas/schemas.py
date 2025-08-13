"""
Pydantic schemas for StudyMate API
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr, validator
from enum import Enum

# Enums
class DocumentStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ModelType(str, Enum):
    GRANITE_3B = "granite-3b-code-instruct"
    GRANITE_8B = "granite-8b-code-instruct"
    GRANITE_13B = "granite-13b-instruct"

# Base schemas
class BaseSchema(BaseModel):
    class Config:
        from_attributes = True
        use_enum_values = True

# User schemas
class UserBase(BaseSchema):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=255)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserUpdate(BaseSchema):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=255)
    preferred_model: Optional[ModelType] = None
    settings: Optional[Dict[str, Any]] = None

class UserResponse(UserBase):
    id: UUID
    is_active: bool
    is_superuser: bool
    preferred_model: str
    settings: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

class UserLogin(BaseSchema):
    username: str
    password: str

# Token schemas
class Token(BaseSchema):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseSchema):
    username: Optional[str] = None
    user_id: Optional[UUID] = None

# Document schemas
class DocumentBase(BaseSchema):
    filename: str
    file_type: str

class DocumentCreate(DocumentBase):
    original_filename: str
    file_size: int
    mime_type: Optional[str] = None

class DocumentUpdate(BaseSchema):
    filename: Optional[str] = None
    status: Optional[DocumentStatus] = None

class DocumentResponse(DocumentBase):
    id: UUID
    original_filename: str
    file_size: int
    status: DocumentStatus
    total_pages: Optional[int] = None
    total_words: Optional[int] = None
    total_characters: Optional[int] = None
    chunk_count: int
    processing_time: Optional[float] = None
    processing_error: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class DocumentUploadResponse(BaseSchema):
    document_id: UUID
    filename: str
    file_size: int
    status: DocumentStatus
    message: str

# Document chunk schemas
class DocumentChunkBase(BaseSchema):
    chunk_index: int
    text: str
    word_count: int
    character_count: int
    page_number: Optional[int] = None

class DocumentChunkResponse(DocumentChunkBase):
    id: UUID
    document_id: UUID
    embedding_model: Optional[str] = None
    faiss_index_id: Optional[int] = None
    created_at: datetime

# Conversation schemas
class ConversationBase(BaseSchema):
    title: Optional[str] = None

class ConversationCreate(ConversationBase):
    pass

class ConversationUpdate(ConversationBase):
    title: Optional[str] = None

class ConversationResponse(ConversationBase):
    id: UUID
    message_count: int
    total_tokens: int
    created_at: datetime
    updated_at: datetime

# Message schemas
class MessageBase(BaseSchema):
    role: MessageRole
    content: str

class MessageCreate(MessageBase):
    conversation_id: Optional[UUID] = None

class MessageResponse(MessageBase):
    id: UUID
    conversation_id: UUID
    token_count: Optional[int] = None
    model_used: Optional[str] = None
    confidence_score: Optional[float] = None
    processing_time: Optional[float] = None
    generation_params: Optional[Dict[str, Any]] = None
    source_chunks: Optional[List[UUID]] = None
    created_at: datetime

# Q&A schemas
class QuestionRequest(BaseSchema):
    question: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[UUID] = None
    model: Optional[ModelType] = None
    max_results: Optional[int] = Field(default=10, ge=1, le=50)
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)
    top_p: Optional[float] = Field(default=0.9, ge=0.0, le=1.0)
    top_k: Optional[int] = Field(default=50, ge=1, le=100)
    max_new_tokens: Optional[int] = Field(default=512, ge=1, le=2048)

class SourceChunk(BaseSchema):
    chunk_id: UUID
    document_id: UUID
    document_name: str
    text: str
    similarity_score: float
    page_number: Optional[int] = None
    chunk_index: int

class QuestionResponse(BaseSchema):
    answer: str
    confidence_score: float
    model_used: str
    processing_time: float
    source_chunks: List[SourceChunk]
    conversation_id: UUID
    message_id: UUID
    generation_params: Dict[str, Any]

# Search schemas
class SearchRequest(BaseSchema):
    query: str = Field(..., min_length=1, max_length=1000)
    max_results: Optional[int] = Field(default=10, ge=1, le=50)
    min_similarity: Optional[float] = Field(default=0.1, ge=0.0, le=1.0)
    document_ids: Optional[List[UUID]] = None

class SearchResponse(BaseSchema):
    results: List[SourceChunk]
    total_results: int
    processing_time: float

# Model schemas
class ModelInfo(BaseSchema):
    model_id: str
    name: str
    description: str
    max_length: int
    default_params: Dict[str, Any]

class ModelListResponse(BaseSchema):
    models: List[ModelInfo]
    current_model: str

class ModelSwitchRequest(BaseSchema):
    model: ModelType

# Analytics schemas
class DocumentAnalytics(BaseSchema):
    total_documents: int
    total_pages: int
    total_words: int
    total_chunks: int
    processing_time_avg: float
    file_types: Dict[str, int]

class ConversationAnalytics(BaseSchema):
    total_conversations: int
    total_messages: int
    avg_messages_per_conversation: float
    model_usage: Dict[str, int]
    avg_confidence_score: float

class SystemAnalytics(BaseSchema):
    user_count: int
    document_analytics: DocumentAnalytics
    conversation_analytics: ConversationAnalytics
    uptime: float
    memory_usage: Dict[str, float]

# Error schemas
class ErrorResponse(BaseSchema):
    error: str
    detail: Optional[str] = None
    error_code: Optional[str] = None

class ValidationErrorResponse(BaseSchema):
    error: str = "Validation Error"
    details: List[Dict[str, Any]]

# Health check schema
class HealthResponse(BaseSchema):
    status: str
    timestamp: datetime
    version: str
    database: str
    models_loaded: List[str]
    uptime: float

# File upload schemas
class FileUploadResponse(BaseSchema):
    success: bool
    message: str
    files: List[DocumentUploadResponse]
    failed_files: List[Dict[str, str]]

# Batch operation schemas
class BatchDocumentDelete(BaseSchema):
    document_ids: List[UUID]

class BatchOperationResponse(BaseSchema):
    success: bool
    processed: int
    failed: int
    errors: List[str]

# Export schemas
class ExportRequest(BaseSchema):
    format: str = Field(default="json", regex="^(json|csv|pdf)$")
    include_conversations: bool = True
    include_documents: bool = True
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None

class ExportResponse(BaseSchema):
    export_id: UUID
    status: str
    download_url: Optional[str] = None
    expires_at: Optional[datetime] = None
