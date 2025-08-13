# Usage Guide

This guide explains how to use StudyMate effectively for your academic needs.

## Getting Started

### 1. Upload Documents

1. Start the application: `streamlit run main.py`
2. Navigate to the "Upload Documents" section
3. Click "Choose PDF files" and select your study materials
4. Click "Process Files" to extract text and build the search index

**Supported Formats:**
- PDF files (primary format)
- Text files (.txt)
- Word documents (.docx)

**File Limits:**
- Maximum file size: 50MB per file
- Maximum files: 10 files per session
- Total recommended size: Under 500MB

### 2. Ask Questions

Once your documents are processed:

1. Go to the "Chat" section
2. Type your question in natural language
3. Press Enter or click Send
4. Review the AI-generated answer and sources

## Best Practices

### Writing Effective Questions

**Good Questions:**
- "What are the main principles of machine learning discussed in Chapter 3?"
- "Explain the methodology used in the research study"
- "What are the key differences between supervised and unsupervised learning?"
- "Summarize the conclusions from the experiment results"

**Less Effective Questions:**
- "What is this about?" (too vague)
- "Tell me everything" (too broad)
- "Is this correct?" (without context)

### Question Types That Work Well

1. **Definitional Questions**
   - "What is [concept]?"
   - "Define [term] according to the document"

2. **Explanatory Questions**
   - "How does [process] work?"
   - "Explain the relationship between [A] and [B]"

3. **Comparative Questions**
   - "What are the differences between [A] and [B]?"
   - "Compare [method 1] and [method 2]"

4. **Analytical Questions**
   - "What are the advantages and disadvantages of [approach]?"
   - "What evidence supports [claim]?"

5. **Summary Questions**
   - "Summarize the main points of [chapter/section]"
   - "What are the key takeaways from [topic]?"

## Features Overview

### Document Processing

**Text Extraction:**
- Automatic text extraction from PDFs
- Preservation of document structure
- Metadata extraction (title, author, etc.)

**Text Chunking:**
- Intelligent text segmentation
- Overlap between chunks for context
- Optimized chunk sizes for better retrieval

### Search and Retrieval

**Semantic Search:**
- Vector-based similarity search
- Context-aware matching
- Relevance scoring

**Source Attribution:**
- Links to original documents
- Page references when available
- Confidence scores for answers

### Chat Interface

**Conversation Features:**
- Persistent chat history
- Context-aware responses
- Follow-up question support

**Export Options:**
- Download chat history
- Save important Q&A pairs
- Export to text format

## Advanced Usage

### Working with Multiple Documents

When you have multiple documents:

1. **Cross-Document Questions:**
   - "Compare the approaches discussed in Document A and Document B"
   - "What common themes appear across all documents?"

2. **Document-Specific Questions:**
   - "According to the Smith paper, what is the main hypothesis?"
   - "In the textbook chapter, how is [concept] defined?"

### Improving Answer Quality

1. **Be Specific:**
   - Include specific terms or concepts
   - Reference particular sections or chapters
   - Use domain-specific vocabulary

2. **Provide Context:**
   - "In the context of [topic], explain [concept]"
   - "Based on the experimental results, what can we conclude about [hypothesis]?"

3. **Ask Follow-up Questions:**
   - "Can you elaborate on [specific point]?"
   - "What examples are provided for [concept]?"

### Managing Large Document Sets

**Organization Tips:**
- Group related documents together
- Use descriptive filenames
- Process documents in batches by topic

**Performance Optimization:**
- Process smaller batches for faster response
- Clear cache periodically for memory management
- Use specific questions to get targeted results

## Troubleshooting

### Common Issues and Solutions

**No Results Found:**
- Try rephrasing your question
- Use different keywords or synonyms
- Check if the topic is covered in your documents
- Ensure documents were processed successfully

**Poor Answer Quality:**
- Make questions more specific
- Include more context in your query
- Check if the source documents contain relevant information
- Try breaking complex questions into simpler parts

**Slow Performance:**
- Reduce the number of documents
- Clear browser cache
- Check internet connection
- Restart the application

**Processing Errors:**
- Ensure PDF files are not corrupted
- Check file size limits
- Verify file format compatibility
- Try processing files individually

### Getting Better Results

1. **Document Quality:**
   - Use high-quality, text-based PDFs
   - Avoid scanned images without OCR
   - Ensure documents are complete and readable

2. **Question Formulation:**
   - Start with broad questions, then get specific
   - Use terminology from your documents
   - Ask one concept at a time

3. **Iterative Approach:**
   - Build on previous answers
   - Ask clarifying questions
   - Explore different aspects of topics

## Tips for Different Use Cases

### Research Papers
- Ask about methodology, results, and conclusions
- Compare findings across multiple papers
- Extract key statistics and data points

### Textbooks
- Focus on definitions and concepts
- Ask for examples and applications
- Request summaries of chapters or sections

### Lecture Notes
- Clarify confusing points
- Ask for elaboration on brief notes
- Connect concepts across different lectures

### Study Guides
- Test your understanding with questions
- Ask for practice problems or examples
- Request comprehensive reviews of topics

## Next Steps

- Explore the [API Reference](api_reference.md) for technical details
- Check out advanced configuration options
- Join our community for tips and support
