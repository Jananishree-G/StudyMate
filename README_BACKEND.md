# 📚 StudyMate - AI Academic Assistant

## 🎉 Complete Backend Solution with Authentication & PDF Q&A

StudyMate is a comprehensive AI-powered academic assistant that allows users to upload PDF documents, process them with advanced AI models, and engage in intelligent conversations about the content.

## ✨ Features

### 🔐 **Authentication System**
- User registration and login
- JWT token-based authentication
- Secure password hashing with bcrypt
- User session management

### 📄 **PDF Document Management**
- Upload PDF files with validation
- Automatic text extraction and processing
- Document chunking for AI processing
- Status tracking (uploaded → processing → processed)
- File metadata storage

### 🤖 **AI-Powered Q&A Chatbot**
- Chat with uploaded PDF documents
- Context-aware responses using document content
- IBM Granite model integration
- Source citation and confidence scoring
- Conversation history storage

### 💾 **Database Integration**
- SQLite database for production use
- User data and document metadata storage
- Chat history and conversation tracking
- Proper relational data modeling

### 🎨 **Modern Web Interface**
- Beautiful Streamlit frontend
- Responsive design with custom CSS
- User dashboard and document management
- Real-time chat interface
- Document upload with progress tracking

## 🚀 Quick Start

### Option 1: One-Click Startup (Recommended)
```bash
python start_studymate.py
```

### Option 2: Manual Startup
```bash
# Terminal 1: Start Backend API
python backend_api.py

# Terminal 2: Start Frontend App
streamlit run studymate_app.py --server.port 8501
```

## 📊 Application URLs

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend App** | http://localhost:8501 | Main user interface |
| **Backend API** | http://localhost:8000 | REST API server |
| **API Documentation** | http://localhost:8000/docs | Interactive API docs |

## 🔧 System Architecture

### Backend Components
```
📦 Backend API (FastAPI)
├── 🔐 Authentication (JWT + bcrypt)
├── 📄 PDF Processing (PyMuPDF)
├── 🤖 AI Integration (IBM Granite)
├── 💾 Database (SQLite)
└── 🔍 Vector Search (FAISS)
```

### Frontend Components
```
🎨 Frontend App (Streamlit)
├── 🔑 Login/Register Pages
├── 📄 Document Management
├── 💬 Chat Interface
├── 📊 User Dashboard
└── ⚙️ Settings Panel
```

### Database Schema
```sql
📊 Database Tables:
├── users (authentication & profiles)
├── documents (PDF metadata & status)
├── document_chunks (processed text chunks)
├── conversations (chat sessions)
└── messages (individual chat messages)
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- pip package manager

### Dependencies Installation
```bash
pip install fastapi uvicorn streamlit PyMuPDF passlib[bcrypt] PyJWT python-multipart requests transformers sentence-transformers faiss-cpu torch
```

### Environment Setup
The application automatically creates a `.env` file with default settings. Key configurations:

```env
DATABASE_URL=sqlite:///./studymate.db
HUGGINGFACE_TOKEN=your_token_here
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

## 📖 Usage Guide

### 1. **User Registration**
- Open http://localhost:8501
- Click "Register" tab
- Fill in username, email, and password
- Account is created and you're automatically logged in

### 2. **Document Upload**
- Navigate to "Document Management"
- Click "Choose a PDF file"
- Select your PDF document
- Click "Upload & Process"
- Wait for processing to complete

### 3. **Chat with Documents**
- Go to "Chat with Documents"
- Select a processed document
- Ask questions about the document content
- Get AI-powered answers with source citations

### 4. **View Dashboard**
- Check "Dashboard" for statistics
- View recent activity and usage metrics
- Monitor document processing status

## 🔌 API Endpoints

### Authentication
```http
POST /auth/register    # Register new user
POST /auth/login       # Login user
GET  /auth/me          # Get current user info
```

### Document Management
```http
POST /documents/upload # Upload PDF document
GET  /documents        # Get user's documents
```

### Chat & Q&A
```http
POST /chat                           # Chat with document
GET  /conversations                  # Get user conversations
GET  /conversations/{id}/messages    # Get conversation messages
```

## 🤖 AI Models Integration

### IBM Granite Models
- **granite-3b-code-instruct**: Primary Q&A model
- **granite-8b-code-instruct**: Enhanced performance model
- Automatic model loading and fallback handling

### Embedding Models
- **sentence-transformers/all-MiniLM-L6-v2**: Document embeddings
- FAISS vector database for similarity search
- Context-aware answer generation

## 💾 Database Features

### User Management
- Secure user authentication
- Profile information storage
- Account creation timestamps

### Document Storage
- PDF file metadata
- Processing status tracking
- Chunk count and file size metrics
- Owner relationship management

### Conversation History
- Complete chat history storage
- Message threading and organization
- Source attribution and confidence scores

## 🔒 Security Features

### Authentication Security
- JWT token-based authentication
- Bcrypt password hashing
- Secure session management
- Token expiration handling

### Data Protection
- User data isolation
- Document ownership validation
- API endpoint protection
- Input validation and sanitization

## 🎯 Advanced Features

### PDF Processing
- Multi-page document support
- Text extraction with page numbers
- Intelligent text chunking
- Processing status tracking

### AI Integration
- Context-aware question answering
- Source citation and page references
- Confidence scoring for responses
- Fallback handling for model errors

### User Experience
- Real-time processing status
- Progress indicators
- Error handling and user feedback
- Responsive design for all devices

## 🚀 Production Deployment

### Environment Variables
```env
SECRET_KEY=your-production-secret-key
DATABASE_URL=postgresql://user:pass@host:port/db
HUGGINGFACE_TOKEN=your-hf-token
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements_backend.txt
EXPOSE 8000 8501
CMD ["python", "start_studymate.py"]
```

## 📊 Monitoring & Analytics

### Built-in Metrics
- User registration and activity
- Document upload and processing stats
- Chat interaction analytics
- System performance monitoring

### Dashboard Features
- Real-time statistics
- Usage trends and patterns
- Document processing metrics
- User engagement tracking

## 🎉 Success Indicators

✅ **Authentication System**: Complete user management with secure login/register  
✅ **PDF Processing**: Full document upload, processing, and storage  
✅ **AI Chatbot**: Intelligent Q&A with document context and source citations  
✅ **Database Integration**: Proper data storage and retrieval  
✅ **Modern UI**: Beautiful, responsive web interface  
✅ **Production Ready**: Scalable architecture with proper error handling  

## 🔧 Troubleshooting

### Common Issues
1. **API Connection Failed**: Ensure backend is running on port 8000
2. **Document Processing Stuck**: Check PDF file format and size
3. **Login Issues**: Verify database is initialized properly
4. **Model Loading Errors**: Check HuggingFace token and internet connection

### Support
- Check logs in terminal output
- Verify all dependencies are installed
- Ensure ports 8000 and 8501 are available
- Review API documentation at http://localhost:8000/docs

---

**StudyMate - Your Complete AI Academic Assistant Solution! 🚀**
