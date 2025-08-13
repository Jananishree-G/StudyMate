# Contributing to StudyMate

We welcome contributions to StudyMate! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Create a new branch for your feature or bug fix
4. Make your changes
5. Test your changes
6. Submit a pull request

## Development Setup

### Prerequisites

- Python 3.8+
- Git
- Virtual environment tool (venv or conda)

### Setup Steps

1. Clone your fork:
```bash
git clone https://github.com/yourusername/StudyMate.git
cd StudyMate
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
pip install -e .  # Install in development mode
```

4. Install development dependencies:
```bash
pip install pytest black flake8 isort pytest-cov
```

5. Set up pre-commit hooks (optional):
```bash
pip install pre-commit
pre-commit install
```

## Code Style

We follow Python best practices and use automated tools for code formatting:

### Formatting
- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting

Run formatting tools:
```bash
black src/ tests/
isort src/ tests/
flake8 src/ tests/
```

### Code Standards

1. **PEP 8**: Follow Python style guidelines
2. **Type Hints**: Use type hints for function parameters and returns
3. **Docstrings**: Use Google-style docstrings
4. **Comments**: Write clear, concise comments
5. **Variable Names**: Use descriptive variable names

### Example Code Style

```python
def process_document(file_path: Path, chunk_size: int = 1000) -> List[Dict[str, Any]]:
    """
    Process a document and create text chunks.
    
    Args:
        file_path: Path to the document file
        chunk_size: Size of text chunks in characters
        
    Returns:
        List of text chunks with metadata
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If chunk_size is invalid
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if chunk_size <= 0:
        raise ValueError("Chunk size must be positive")
    
    # Process the document
    chunks = []
    # ... implementation
    
    return chunks
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_pdf_processor.py

# Run tests with verbose output
pytest -v
```

### Writing Tests

1. **Test Structure**: Follow the existing test structure
2. **Test Names**: Use descriptive test names
3. **Test Coverage**: Aim for high test coverage
4. **Mock External Services**: Mock API calls and external dependencies

### Test Example

```python
def test_chunk_text_with_overlap():
    """Test text chunking with overlap"""
    text = "This is a test sentence. " * 20
    chunks = chunk_text(text, chunk_size=100, overlap=20)
    
    assert len(chunks) > 1
    assert all(len(chunk) <= 120 for chunk in chunks)  # Allow for sentence boundaries
```

## Contribution Types

### Bug Reports

When reporting bugs, please include:

1. **Description**: Clear description of the bug
2. **Steps to Reproduce**: Detailed steps to reproduce the issue
3. **Expected Behavior**: What you expected to happen
4. **Actual Behavior**: What actually happened
5. **Environment**: OS, Python version, package versions
6. **Screenshots**: If applicable

### Feature Requests

When requesting features, please include:

1. **Use Case**: Why is this feature needed?
2. **Description**: Detailed description of the feature
3. **Examples**: Examples of how it would be used
4. **Alternatives**: Alternative solutions you've considered

### Code Contributions

#### Types of Contributions

1. **Bug Fixes**: Fix existing bugs
2. **New Features**: Add new functionality
3. **Performance Improvements**: Optimize existing code
4. **Documentation**: Improve documentation
5. **Tests**: Add or improve tests

#### Pull Request Process

1. **Branch Naming**: Use descriptive branch names
   - `feature/add-new-embedding-model`
   - `bugfix/fix-pdf-processing-error`
   - `docs/update-installation-guide`

2. **Commit Messages**: Write clear commit messages
   - Use present tense ("Add feature" not "Added feature")
   - Keep first line under 50 characters
   - Include detailed description if needed

3. **Pull Request Description**: Include:
   - Summary of changes
   - Related issue numbers
   - Testing performed
   - Screenshots (if UI changes)

4. **Code Review**: Address feedback from reviewers

## Project Structure

Understanding the project structure helps with contributions:

```
StudyMate/
├── src/                    # Core application code
│   ├── pdf_processor.py   # PDF processing
│   ├── embeddings.py      # Embedding management
│   ├── qa_engine.py       # Q&A engine
│   ├── config.py          # Configuration
│   └── utils.py           # Utility functions
├── frontend/               # Streamlit frontend
│   ├── streamlit_app.py   # Main app
│   └── components/        # UI components
├── tests/                  # Test files
├── docs/                   # Documentation
├── data/                   # Data directories
└── requirements.txt        # Dependencies
```

## Areas for Contribution

### High Priority

1. **Performance Optimization**: Improve processing speed
2. **Error Handling**: Better error messages and recovery
3. **Documentation**: Improve user guides and API docs
4. **Testing**: Increase test coverage
5. **UI/UX**: Enhance user interface

### Medium Priority

1. **New File Formats**: Support for more document types
2. **Advanced Search**: Implement advanced search features
3. **Export Features**: Better export and sharing options
4. **Internationalization**: Multi-language support
5. **Mobile Responsiveness**: Improve mobile experience

### Low Priority

1. **Themes**: Dark mode and custom themes
2. **Plugins**: Plugin system for extensions
3. **Analytics**: Usage analytics and insights
4. **Collaboration**: Multi-user features

## Getting Help

If you need help with contributions:

1. **GitHub Issues**: Ask questions in GitHub issues
2. **Discussions**: Use GitHub Discussions for general questions
3. **Documentation**: Check existing documentation
4. **Code Examples**: Look at existing code for patterns

## Recognition

Contributors will be recognized in:

1. **README**: Contributors section
2. **Release Notes**: Acknowledgment in releases
3. **GitHub**: Contributor graphs and statistics

## License

By contributing to StudyMate, you agree that your contributions will be licensed under the MIT License.

## Code of Conduct

Please note that this project is released with a Contributor Code of Conduct. By participating in this project, you agree to abide by its terms.

### Our Standards

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Respect different viewpoints and experiences
- Show empathy towards other community members

Thank you for contributing to StudyMate!
