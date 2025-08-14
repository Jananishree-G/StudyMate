#!/usr/bin/env python3
"""
StudyMate Backend API with Authentication
FastAPI backend with user authentication, PDF processing, and Q&A chatbot
"""

import os
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from pathlib import Path
import sqlite3
import json

from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
import jwt
from passlib.context import CryptContext
import uvicorn

# Initialize FastAPI app
app = FastAPI(
    title="StudyMate API",
    description="Advanced AI Academic Assistant with Authentication",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://localhost:8502", "http://localhost:8503"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security configuration
SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Database configuration
DATABASE_PATH = "studymate.db"

# Pydantic models
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: Optional[str]
    is_active: bool
    created_at: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class DocumentResponse(BaseModel):
    id: str
    filename: str
    file_size: int
    status: str
    chunk_count: int
    created_at: str

class ChatMessage(BaseModel):
    message: str
    document_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    sources: List[Dict[str, Any]]
    confidence: float

# Database helper functions
def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize database with required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            full_name TEXT,
            hashed_password TEXT NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create documents table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            original_filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            file_type TEXT NOT NULL,
            status TEXT DEFAULT 'uploaded',
            chunk_count INTEGER DEFAULT 0,
            owner_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (owner_id) REFERENCES users (id)
        )
    ''')
    
    # Create document_chunks table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS document_chunks (
            id TEXT PRIMARY KEY,
            chunk_index INTEGER NOT NULL,
            text TEXT NOT NULL,
            word_count INTEGER NOT NULL,
            page_number INTEGER,
            document_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (document_id) REFERENCES documents (id)
        )
    ''')
    
    # Create conversations table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            title TEXT,
            user_id TEXT NOT NULL,
            document_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (document_id) REFERENCES documents (id)
        )
    ''')
    
    # Create messages table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            conversation_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Authentication functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user_by_username(username: str):
    """Get user by username"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_id(user_id: str):
    """Get user by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def create_user(user_data: UserCreate):
    """Create new user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    user_id = secrets.token_urlsafe(16)
    hashed_password = get_password_hash(user_data.password)
    
    try:
        cursor.execute('''
            INSERT INTO users (id, username, email, full_name, hashed_password)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, user_data.username, user_data.email, user_data.full_name, hashed_password))
        conn.commit()
        conn.close()
        return get_user_by_id(user_id)
    except sqlite3.IntegrityError:
        conn.close()
        return None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = get_user_by_username(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# API Routes
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_database()
    print("✅ StudyMate API started successfully")
    print("📊 Database initialized")
    print("🔐 Authentication system ready")

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "StudyMate API", "status": "running", "version": "1.0.0"}

@app.post("/auth/register", response_model=Token)
async def register(user_data: UserCreate):
    """Register new user"""
    # Check if user already exists
    existing_user = get_user_by_username(user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Create user
    user = create_user(user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create user"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    
    user_response = UserResponse(
        id=user["id"],
        username=user["username"],
        email=user["email"],
        full_name=user["full_name"],
        is_active=bool(user["is_active"]),
        created_at=user["created_at"]
    )
    
    return Token(access_token=access_token, token_type="bearer", user=user_response)

@app.post("/auth/login", response_model=Token)
async def login(user_data: UserLogin):
    """Login user"""
    user = get_user_by_username(user_data.username)
    if not user or not verify_password(user_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    
    user_response = UserResponse(
        id=user["id"],
        username=user["username"],
        email=user["email"],
        full_name=user["full_name"],
        is_active=bool(user["is_active"]),
        created_at=user["created_at"]
    )
    
    return Token(access_token=access_token, token_type="bearer", user=user_response)

@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(
        id=current_user["id"],
        username=current_user["username"],
        email=current_user["email"],
        full_name=current_user["full_name"],
        is_active=bool(current_user["is_active"]),
        created_at=current_user["created_at"]
    )

# PDF Processing functions
def process_pdf_file(file_path: str, filename: str, user_id: str):
    """Process uploaded PDF file"""
    try:
        import PyMuPDF as fitz

        # Open PDF
        doc = fitz.open(file_path)

        # Extract text from all pages
        full_text = ""
        page_texts = []

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            page_texts.append({"page": page_num + 1, "text": text})
            full_text += text + "\n"

        doc.close()

        # Create document record
        doc_id = secrets.token_urlsafe(16)
        file_size = os.path.getsize(file_path)

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO documents (id, filename, original_filename, file_path, file_size, file_type, owner_id, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (doc_id, filename, filename, file_path, file_size, "pdf", user_id, "processing"))

        # Create text chunks
        chunks = create_text_chunks(full_text, page_texts)
        chunk_count = 0

        for i, chunk in enumerate(chunks):
            chunk_id = secrets.token_urlsafe(16)
            cursor.execute('''
                INSERT INTO document_chunks (id, chunk_index, text, word_count, page_number, document_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (chunk_id, i, chunk["text"], chunk["word_count"], chunk.get("page"), doc_id))
            chunk_count += 1

        # Update document status
        cursor.execute('''
            UPDATE documents SET status = ?, chunk_count = ? WHERE id = ?
        ''', ("processed", chunk_count, doc_id))

        conn.commit()
        conn.close()

        return {"document_id": doc_id, "chunks": chunk_count, "status": "processed"}

    except Exception as e:
        # Update document status to failed
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE documents SET status = ? WHERE id = ?", ("failed", doc_id))
        conn.commit()
        conn.close()
        raise e

def create_text_chunks(text: str, page_texts: List[Dict], chunk_size: int = 1000, overlap: int = 200):
    """Create text chunks from document text"""
    chunks = []
    words = text.split()

    for i in range(0, len(words), chunk_size - overlap):
        chunk_words = words[i:i + chunk_size]
        chunk_text = " ".join(chunk_words)

        # Find which page this chunk belongs to
        page_num = 1
        for page_data in page_texts:
            if chunk_text[:100] in page_data["text"]:
                page_num = page_data["page"]
                break

        chunks.append({
            "text": chunk_text,
            "word_count": len(chunk_words),
            "page": page_num
        })

    return chunks

# PDF Upload endpoint
@app.post("/documents/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload and process PDF document"""
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported"
        )

    # Create upload directory
    upload_dir = Path("data/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Save uploaded file
    file_path = upload_dir / f"{secrets.token_urlsafe(8)}_{file.filename}"

    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Process PDF
        result = process_pdf_file(str(file_path), file.filename, current_user["id"])

        # Get document info
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM documents WHERE id = ?", (result["document_id"],))
        doc = cursor.fetchone()
        conn.close()

        return DocumentResponse(
            id=doc["id"],
            filename=doc["filename"],
            file_size=doc["file_size"],
            status=doc["status"],
            chunk_count=doc["chunk_count"],
            created_at=doc["created_at"]
        )

    except Exception as e:
        # Clean up file on error
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process document: {str(e)}"
        )

@app.get("/documents", response_model=List[DocumentResponse])
async def get_user_documents(current_user: dict = Depends(get_current_user)):
    """Get user's documents"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents WHERE owner_id = ? ORDER BY created_at DESC", (current_user["id"],))
    documents = cursor.fetchall()
    conn.close()

    return [
        DocumentResponse(
            id=doc["id"],
            filename=doc["filename"],
            file_size=doc["file_size"],
            status=doc["status"],
            chunk_count=doc["chunk_count"],
            created_at=doc["created_at"]
        )
        for doc in documents
    ]

# Chatbot Q&A functions
def search_document_chunks(query: str, document_id: str, limit: int = 5):
    """Search document chunks for relevant content"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Simple text search (can be enhanced with vector search later)
    cursor.execute('''
        SELECT * FROM document_chunks
        WHERE document_id = ? AND text LIKE ?
        ORDER BY chunk_index
        LIMIT ?
    ''', (document_id, f"%{query}%", limit))

    chunks = cursor.fetchall()
    conn.close()

    return [dict(chunk) for chunk in chunks]

def generate_answer(question: str, context_chunks: List[Dict], document_id: str):
    """Generate answer using context chunks"""
    try:
        # Import IBM Granite model (fallback to simple response if not available)
        try:
            import sys
            sys.path.append('.')
            from backend.manager import StudyMateBackend

            backend = StudyMateBackend()

            # Combine context from chunks
            context = "\n\n".join([chunk["text"][:500] for chunk in context_chunks])

            # Generate answer using the backend
            answer = backend.get_answer(question, context=context)
            confidence = 0.8  # Default confidence

        except Exception as e:
            # Fallback to simple answer generation
            if context_chunks:
                context = "\n".join([chunk["text"][:200] for chunk in context_chunks])
                answer = f"Based on the document content, here's what I found:\n\n{context[:500]}..."
                confidence = 0.6
            else:
                answer = "I couldn't find relevant information in the document to answer your question."
                confidence = 0.2

        # Prepare sources
        sources = []
        for chunk in context_chunks:
            sources.append({
                "chunk_id": chunk["id"],
                "page": chunk.get("page_number", 1),
                "text": chunk["text"][:200] + "..." if len(chunk["text"]) > 200 else chunk["text"]
            })

        return {
            "answer": answer,
            "sources": sources,
            "confidence": confidence
        }

    except Exception as e:
        return {
            "answer": f"I encountered an error while processing your question: {str(e)}",
            "sources": [],
            "confidence": 0.1
        }

def save_conversation(user_id: str, document_id: str, question: str, answer: str):
    """Save conversation to database"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create or get conversation
    conversation_id = secrets.token_urlsafe(16)
    cursor.execute('''
        INSERT INTO conversations (id, user_id, document_id, title)
        VALUES (?, ?, ?, ?)
    ''', (conversation_id, user_id, document_id, question[:50] + "..."))

    # Save user message
    message_id = secrets.token_urlsafe(16)
    cursor.execute('''
        INSERT INTO messages (id, role, content, conversation_id)
        VALUES (?, ?, ?, ?)
    ''', (message_id, "user", question, conversation_id))

    # Save assistant message
    message_id = secrets.token_urlsafe(16)
    cursor.execute('''
        INSERT INTO messages (id, role, content, conversation_id)
        VALUES (?, ?, ?, ?)
    ''', (message_id, "assistant", answer, conversation_id))

    conn.commit()
    conn.close()

    return conversation_id

# Chatbot endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat_with_document(
    chat_data: ChatMessage,
    current_user: dict = Depends(get_current_user)
):
    """Chat with uploaded document"""
    if not chat_data.document_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document ID is required"
        )

    # Verify user owns the document
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents WHERE id = ? AND owner_id = ?",
                  (chat_data.document_id, current_user["id"]))
    document = cursor.fetchone()
    conn.close()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # Search for relevant chunks
    relevant_chunks = search_document_chunks(chat_data.message, chat_data.document_id)

    # Generate answer
    result = generate_answer(chat_data.message, relevant_chunks, chat_data.document_id)

    # Save conversation
    save_conversation(current_user["id"], chat_data.document_id, chat_data.message, result["answer"])

    return ChatResponse(
        response=result["answer"],
        sources=result["sources"],
        confidence=result["confidence"]
    )

@app.get("/conversations")
async def get_user_conversations(current_user: dict = Depends(get_current_user)):
    """Get user's conversations"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT c.*, d.filename
        FROM conversations c
        LEFT JOIN documents d ON c.document_id = d.id
        WHERE c.user_id = ?
        ORDER BY c.created_at DESC
    ''', (current_user["id"],))
    conversations = cursor.fetchall()
    conn.close()

    return [dict(conv) for conv in conversations]

@app.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get messages from a conversation"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Verify user owns the conversation
    cursor.execute("SELECT * FROM conversations WHERE id = ? AND user_id = ?",
                  (conversation_id, current_user["id"]))
    conversation = cursor.fetchone()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Get messages
    cursor.execute("SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at",
                  (conversation_id,))
    messages = cursor.fetchall()
    conn.close()

    return [dict(msg) for msg in messages]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
