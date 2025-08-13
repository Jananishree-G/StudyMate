# 🚀 StudyMate Setup Guide

This guide will help you set up StudyMate with proper environment variables and API keys.

## 📋 Prerequisites

Before starting, make sure you have:
- Python 3.8 or higher installed
- Git installed
- An IBM Cloud account (for Watson API)
- A HuggingFace account (optional, for better performance)

## 🔧 Step-by-Step Setup

### Step 1: Navigate to Project Directory

```bash
cd Documents/augment-projects/Study_Mate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Get IBM Watson API Credentials

1. **Go to IBM Cloud**: https://cloud.ibm.com/
2. **Sign up or log in** to your account
3. **Create Watson Machine Learning service**:
   - Search for "Watson Machine Learning"
   - Click "Create"
   - Choose a plan (Lite plan is free)
4. **Get your credentials**:
   - Go to your Watson ML service instance
   - Click on "Service credentials"
   - Create new credentials if none exist
   - Copy the `apikey` and `url`
5. **Get Project ID**:
   - Go to Watson Studio: https://dataplatform.cloud.ibm.com/
   - Create a new project or use existing one
   - Copy the Project ID from project settings

### Step 4: Get HuggingFace API Key (Optional)

1. **Go to HuggingFace**: https://huggingface.co/
2. **Sign up or log in**
3. **Go to Settings > Access Tokens**: https://huggingface.co/settings/tokens
4. **Create a new token**
5. **Copy the token**

### Step 5: Configure Environment Variables

#### Option A: Use the Setup Script (Recommended)

```bash
python setup_env.py
```

Follow the interactive prompts to enter your API keys.

#### Option B: Manual Configuration

1. **Copy the environment template**:
```bash
cp .env.example .env
```

2. **Edit the .env file**:
```bash
# Open .env file in your text editor
notepad .env  # On Windows
# or
nano .env     # On Linux/Mac
```

3. **Replace the placeholder values**:
```env
# IBM Watson Configuration - REQUIRED
WATSONX_API_KEY=your_actual_api_key_here
WATSONX_PROJECT_ID=your_actual_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com

# HuggingFace Configuration - OPTIONAL
HUGGINGFACE_API_KEY=your_actual_huggingface_token_here
```

### Step 6: Verify Your Setup

```bash
python check_env.py
```

This will verify that all required environment variables are properly configured.

### Step 7: Run the Application

```bash
streamlit run main.py
```

The application should open in your browser at `http://localhost:8501`.

## 🔍 Troubleshooting

### Common Issues

#### 1. "Module not found" errors
```bash
# Make sure you're in the right directory
cd Documents/augment-projects/Study_Mate

# Install dependencies
pip install -r requirements.txt
```

#### 2. "API key not found" errors
```bash
# Check your environment variables
python check_env.py

# If needed, reconfigure
python setup_env.py
```

#### 3. "Permission denied" errors
```bash
# On Windows, run as administrator
# On Linux/Mac, check file permissions
chmod +x setup_env.py
chmod +x check_env.py
```

#### 4. Watson API connection errors
- Verify your API key is correct
- Check that your Watson ML service is active
- Ensure you're using the correct region URL
- Verify your project ID is correct

### Environment Variable Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `WATSONX_API_KEY` | ✅ Yes | IBM Watson API key | `abc123...` |
| `WATSONX_PROJECT_ID` | ✅ Yes | Watson project ID | `def456...` |
| `WATSONX_URL` | ✅ Yes | Watson service URL | `https://us-south.ml.cloud.ibm.com` |
| `HUGGINGFACE_API_KEY` | ❌ No | HuggingFace token | `hf_abc123...` |

### Testing Your Setup

1. **Check environment**:
```bash
python check_env.py
```

2. **Run tests**:
```bash
pytest tests/
```

3. **Start the application**:
```bash
streamlit run main.py
```

4. **Upload a test PDF** and ask a question to verify everything works.

## 🎯 Quick Start Commands

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment (interactive)
python setup_env.py

# 3. Verify setup
python check_env.py

# 4. Run the application
streamlit run main.py
```

## 📞 Getting Help

If you encounter issues:

1. **Check the logs**: Look in the `logs/` directory for error messages
2. **Verify credentials**: Run `python check_env.py`
3. **Check documentation**: See `docs/installation.md` for detailed instructions
4. **Test connection**: Try the IBM Watson API directly in their console

## 🔒 Security Notes

- Never commit your `.env` file to version control
- Keep your API keys secure and don't share them
- Regenerate API keys if you suspect they've been compromised
- Use environment variables for all sensitive configuration

## 🎉 Success!

Once everything is set up, you should see:
- ✅ All environment variables configured
- ✅ Application starts without errors
- ✅ You can upload PDFs and ask questions
- ✅ AI responses are generated successfully

Happy studying with StudyMate! 📚🤖
