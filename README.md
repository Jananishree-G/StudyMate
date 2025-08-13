# StudyMate - AI-Powered Academic Assistant

StudyMate is an AI-powered academic assistant that enables students to interact with their study materials—such as textbooks, lecture notes, and research papers—in a conversational, question-answering format.

## Project Structure

```
StudyMate/
├── src/
│   ├── __init__.py
│   ├── pdf_processor.py
│   ├── embeddings.py
│   ├── qa_engine.py
│   ├── config.py
│   └── utils.py
├── frontend/
│   ├── __init__.py
│   ├── streamlit_app.py
│   └── components/
│       ├── __init__.py
│       ├── file_uploader.py
│       ├── chat_interface.py
│       └── sidebar.py
├── data/
│   ├── uploads/
│   ├── processed/
│   └── embeddings/
├── tests/
│   ├── __init__.py
│   ├── test_pdf_processor.py
│   ├── test_embeddings.py
│   ├── test_qa_engine.py
│   └── test_streamlit_app.py
├── docs/
│   ├── installation.md
│   ├── usage.md
│   └── api_reference.md
├── .env.example
├── .gitignore
├── requirements.txt
├── setup.py
├── README.md
└── main.py
```

## Features

- **Conversational Q&A from Academic PDFs** – Ask natural-language questions and receive contextual answers
- **Accurate Text Extraction** – Efficient PDF processing using PyMuPDF
- **Semantic Search** – FAISS and SentenceTransformers for precise question matching
- **LLM-Based Answers** – IBM Watsonx's Mixtral-8x7B-Instruct model for informative responses
- **User-Friendly Interface** – Intuitive Streamlit-based frontend

## Technologies

- Python 3.8+
- Streamlit
- IBM Watson
- HuggingFace Transformers
- PyMuPDF
- Mistral
- FAISS
- SentenceTransformers

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/StudyMate.git
cd StudyMate
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

## Usage

1. Start the application:
```bash
streamlit run main.py
```

2. Open your browser and navigate to `http://localhost:8501`

3. Upload your PDF documents

4. Start asking questions about your study materials!

## Configuration

Create a `.env` file with the following variables:

```
WATSONX_API_KEY=your_watsonx_api_key
WATSONX_PROJECT_ID=your_project_id
WATSONX_URL=your_watsonx_url
HUGGINGFACE_API_KEY=your_huggingface_api_key
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License

## Support

For support, please open an issue on GitHub or contact the development team.
