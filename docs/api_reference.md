# API Reference

This document provides technical details about StudyMate's internal APIs and modules.

## Core Modules

### PDFProcessor

The `PDFProcessor` class handles PDF text extraction and preprocessing.

#### Methods

##### `extract_text_from_pdf(pdf_path: Path) -> Dict[str, any]`

Extracts text from a PDF file.

**Parameters:**
- `pdf_path`: Path to the PDF file

**Returns:**
- Dictionary containing extracted text and metadata

**Example:**
```python
from pdf_processor import PDFProcessor

processor = PDFProcessor()
result = processor.extract_text_from_pdf(Path("document.pdf"))
print(result['metadata']['total_words'])
```

##### `create_text_chunks(pdf_data: Dict[str, any]) -> List[Dict[str, any]]`

Creates text chunks from processed PDF data.

**Parameters:**
- `pdf_data`: Processed PDF data from `extract_text_from_pdf`

**Returns:**
- List of text chunks with metadata

### EmbeddingManager

The `EmbeddingManager` class handles text embeddings and FAISS indexing.

#### Methods

##### `load_model() -> bool`

Loads the SentenceTransformer model.

**Returns:**
- True if successful, False otherwise

##### `create_embeddings(texts: List[str]) -> np.ndarray`

Creates embeddings for a list of texts.

**Parameters:**
- `texts`: List of text strings

**Returns:**
- NumPy array of embeddings

##### `build_index_from_chunks(chunks: List[Dict[str, any]]) -> bool`

Builds FAISS index from text chunks.

**Parameters:**
- `chunks`: List of text chunks

**Returns:**
- True if successful, False otherwise

##### `search(query: str, k: int = 5) -> List[Dict[str, any]]`

Searches for similar chunks using the query.

**Parameters:**
- `query`: Search query
- `k`: Number of results to return

**Returns:**
- List of similar chunks with scores

### QAEngine

The `QAEngine` class handles question-answering using IBM Watsonx.

#### Methods

##### `initialize_watsonx() -> bool`

Initializes IBM Watsonx client.

**Returns:**
- True if successful, False otherwise

##### `ask_question(question: str, k: int = 5) -> Dict[str, any]`

Complete Q&A pipeline: search + generate answer.

**Parameters:**
- `question`: User's question
- `k`: Number of similar chunks to retrieve

**Returns:**
- Dictionary containing answer and metadata

**Response Format:**
```python
{
    'answer': str,          # Generated answer
    'sources': List[Dict],  # Source documents
    'confidence': float,    # Confidence score (0-100)
    'error': bool          # Error flag
}
```

## Configuration

### Environment Variables

All configuration is managed through environment variables defined in `.env`:

#### Required Variables

- `WATSONX_API_KEY`: IBM Watsonx API key
- `WATSONX_PROJECT_ID`: IBM Watsonx project ID
- `WATSONX_URL`: IBM Watsonx service URL

#### Optional Variables

- `HUGGINGFACE_API_KEY`: HuggingFace API key
- `HUGGINGFACE_MODEL`: Embedding model name
- `MAX_TOKENS`: Maximum tokens for generation
- `TEMPERATURE`: Generation temperature
- `CHUNK_SIZE`: Text chunk size
- `CHUNK_OVERLAP`: Overlap between chunks

### Config Class

The `Config` class provides centralized configuration management:

```python
from config import config

# Access configuration values
print(config.MAX_TOKENS)
print(config.CHUNK_SIZE)

# Validate configuration
if config.validate_config():
    print("Configuration is valid")
```

## Utility Functions

### Text Processing

#### `clean_text(text: str) -> str`

Cleans and normalizes text.

#### `chunk_text(text: str, chunk_size: int, overlap: int) -> List[str]`

Splits text into chunks with overlap.

### File Handling

#### `validate_file_type(filename: str) -> bool`

Validates if file type is allowed.

#### `validate_file_size(file_size: int) -> bool`

Validates if file size is within limits.

#### `save_uploaded_file(uploaded_file, upload_dir: Path) -> Optional[Path]`

Saves uploaded file to disk.

## Data Structures

### Chunk Structure

Text chunks follow this structure:

```python
{
    'chunk_id': str,        # Unique identifier
    'text': str,           # Chunk text content
    'source_file': str,    # Source filename
    'file_path': str,      # Full file path
    'file_hash': str,      # File hash
    'chunk_index': int,    # Index within document
    'char_count': int,     # Character count
    'word_count': int,     # Word count
    'metadata': Dict       # Document metadata
}
```

### Search Result Structure

Search results follow this structure:

```python
{
    'rank': int,           # Result rank
    'score': float,        # Similarity score
    'chunk': Dict          # Chunk data
}
```

## Error Handling

### Exception Types

StudyMate uses standard Python exceptions with descriptive messages:

- `FileNotFoundError`: When PDF files cannot be found
- `ValueError`: For invalid configuration or parameters
- `ConnectionError`: For API connection issues
- `RuntimeError`: For processing errors

### Error Response Format

API methods return error information in a consistent format:

```python
{
    'error': True,
    'message': str,        # Error description
    'code': str           # Error code (optional)
}
```

## Performance Considerations

### Memory Usage

- **Embeddings**: ~1.5MB per 1000 text chunks
- **FAISS Index**: ~4 bytes per dimension per vector
- **Model Loading**: ~400MB for sentence-transformers model

### Optimization Tips

1. **Batch Processing**: Process multiple documents together
2. **Chunk Size**: Optimize chunk size for your use case
3. **Model Caching**: Models are cached after first load
4. **Index Persistence**: Save/load indices to avoid rebuilding

### Scaling Considerations

For large document collections:

1. Use FAISS IVF indices for faster search
2. Implement document sharding
3. Consider distributed processing
4. Use GPU acceleration for embeddings

## Integration Examples

### Basic Usage

```python
from pdf_processor import PDFProcessor
from embeddings import EmbeddingManager
from qa_engine import QAEngine

# Initialize components
processor = PDFProcessor()
embedding_manager = EmbeddingManager()
qa_engine = QAEngine()

# Process documents
pdf_data = processor.extract_text_from_pdf(Path("document.pdf"))
chunks = processor.create_text_chunks(pdf_data)

# Build search index
embedding_manager.build_index_from_chunks(chunks)

# Set up Q&A engine
qa_engine.set_embedding_manager(embedding_manager)

# Ask questions
result = qa_engine.ask_question("What is the main topic?")
print(result['answer'])
```

### Custom Configuration

```python
from config import Config

# Create custom config
class CustomConfig(Config):
    CHUNK_SIZE = 2000
    CHUNK_OVERLAP = 400
    MAX_TOKENS = 2000

# Use custom config
config = CustomConfig()
```

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_pdf_processor.py

# Run with coverage
pytest --cov=src tests/
```

### Test Structure

Tests are organized by module:
- `test_pdf_processor.py`: PDF processing tests
- `test_embeddings.py`: Embedding and search tests
- `test_qa_engine.py`: Q&A engine tests
- `test_streamlit_app.py`: Frontend and utility tests
