# Installation Guide

This guide will help you set up StudyMate on your local machine.

## Prerequisites

- Python 3.8 or higher
- Git
- IBM Watsonx account and API key
- HuggingFace account (optional, for better performance)

## Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/StudyMate.git
cd StudyMate
```

## Step 2: Create Virtual Environment

### Using venv (recommended)
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### Using conda
```bash
conda create -n studymate python=3.8
conda activate studymate
```

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 4: Set Up Environment Variables

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit the `.env` file with your API keys and configuration:

```env
# IBM Watson Configuration
WATSONX_API_KEY=your_watsonx_api_key_here
WATSONX_PROJECT_ID=your_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com

# HuggingFace Configuration (optional)
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
```

## Step 5: Verify Installation

Run the test suite to ensure everything is working:

```bash
pytest tests/
```

## Step 6: Start the Application

```bash
streamlit run main.py
```

The application should open in your browser at `http://localhost:8501`.

## Getting API Keys

### IBM Watsonx API Key

1. Go to [IBM Cloud](https://cloud.ibm.com/)
2. Create an account or sign in
3. Navigate to Watson Machine Learning service
4. Create a new instance
5. Go to Service Credentials and create a new credential
6. Copy the API key and project ID

### HuggingFace API Key (Optional)

1. Go to [HuggingFace](https://huggingface.co/)
2. Create an account or sign in
3. Go to Settings > Access Tokens
4. Create a new token
5. Copy the token

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you've activated your virtual environment
2. **API Key Errors**: Verify your API keys are correct in the `.env` file
3. **Memory Issues**: For large documents, ensure you have sufficient RAM
4. **Port Already in Use**: Change the port with `streamlit run main.py --server.port 8502`

### System Requirements

- **RAM**: Minimum 4GB, recommended 8GB or more
- **Storage**: At least 2GB free space for models and data
- **Internet**: Required for downloading models and API calls

### Performance Optimization

1. **GPU Support**: Install PyTorch with CUDA support for faster embeddings
2. **Model Caching**: Models are cached locally after first download
3. **Batch Processing**: Process multiple documents together for efficiency

## Docker Installation (Alternative)

If you prefer using Docker:

```bash
# Build the image
docker build -t studymate .

# Run the container
docker run -p 8501:8501 -v $(pwd)/.env:/app/.env studymate
```

## Development Setup

For development, install additional dependencies:

```bash
pip install -r requirements.txt
pip install black flake8 isort pytest-cov
```

Set up pre-commit hooks:

```bash
pre-commit install
```

## Next Steps

After installation, check out:
- [Usage Guide](usage.md) - Learn how to use StudyMate
- [API Reference](api_reference.md) - Technical documentation
- [Contributing Guide](../CONTRIBUTING.md) - How to contribute to the project
