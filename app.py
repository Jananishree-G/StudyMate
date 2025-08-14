"""
StudyMate - Main Application
Clean, modern interface for document Q&A
"""

import streamlit as st
import sys
from pathlib import Path
import json
import time

# Add paths
sys.path.append(str(Path(__file__).parent / "backend"))
sys.path.append(str(Path(__file__).parent / "frontend"))

from backend.manager import StudyMateBackend
from frontend.styles import get_custom_css
from backend.config import config

# Authentication functions removed - Direct access to StudyMate

def initialize_session_state():
    """Initialize session state variables"""
    if 'backend' not in st.session_state:
        st.session_state.backend = StudyMateBackend()
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "home"
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []

def render_header():
    """Render the main header"""
    st.markdown("""
    <div class="main-header fade-in-up">
        <h1>📚 StudyMate</h1>
        <p>Your AI-Powered Academic Assistant</p>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Render the enhanced sidebar navigation"""
    with st.sidebar:
        # App branding
        st.markdown("""
        <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); border-radius: 1rem; margin-bottom: 1rem;">
            <h2 style="color: white; margin: 0;">📚 StudyMate</h2>
            <p style="color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;">AI Academic Assistant</p>
        </div>
        """, unsafe_allow_html=True)

        # Navigation
        st.markdown("### 🧭 Navigation")

        pages = {
            "🏠 Home": "home",
            "📁 Upload Documents": "upload",
            "💬 Chat": "chat",
            "📊 Analytics": "analytics",
            "⚙️ Settings": "settings"
        }

        current_page = st.session_state.current_page

        for page_name, page_key in pages.items():
            # Highlight current page
            button_type = "primary" if page_key == current_page else "secondary"
            if st.button(page_name, key=f"nav_{page_key}", use_container_width=True, type=button_type):
                st.session_state.current_page = page_key
                st.rerun()

        st.markdown("---")

        # Model selection
        st.markdown("### 🤖 AI Model")

        available_models = st.session_state.backend.get_available_models()
        current_model = st.session_state.backend.get_current_model()

        model_options = {key: f"{info['name']}" for key, info in available_models.items()}

        selected_model = st.selectbox(
            "Choose AI Model:",
            options=list(model_options.keys()),
            format_func=lambda x: model_options[x],
            index=list(model_options.keys()).index(current_model) if current_model in model_options else 0,
            help="Select the AI model for answering questions"
        )

        if selected_model != current_model:
            with st.spinner(f"Loading {model_options[selected_model]}..."):
                if st.session_state.backend.set_generation_model(selected_model):
                    st.success(f"✅ Switched to {model_options[selected_model]}")
                    st.rerun()
                else:
                    st.error(f"❌ Failed to load {model_options[selected_model]}")

        # Model info
        model_info = st.session_state.backend.get_model_info()
        if model_info:
            st.info(f"🔄 **Current:** {model_info['name']}")

        st.markdown("---")

        # Enhanced system status
        st.markdown("### 📊 System Status")
        stats = st.session_state.backend.get_system_stats()

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Documents", stats['documents_processed'])
        with col2:
            st.metric("Chunks", stats['total_chunks'])

        # Session info
        session_stats = stats.get('session_stats', {})
        if session_stats:
            st.metric("Questions", session_stats.get('questions_answered', 0))
            st.metric("Session", f"{session_stats.get('session_duration_minutes', 0):.1f}m")

        # Status indicator
        if stats['ready_for_questions']:
            st.success("✅ Ready for questions")
        else:
            st.info("📄 Upload documents to start")

        # Quick stats
        if stats['documents_processed'] > 0:
            with st.expander("📈 Quick Stats"):
                st.write(f"**Unique Sources:** {stats.get('unique_sources', 0)}")
                st.write(f"**Processing Sessions:** {stats.get('processing_history', 0)}")

                qa_stats = stats.get('qa_engine', {})
                if qa_stats.get('conversation', {}).get('avg_confidence', 0) > 0:
                    st.write(f"**Avg Confidence:** {qa_stats['conversation']['avg_confidence']}%")

        st.markdown("---")

        # Action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear Data", use_container_width=True):
                st.session_state.backend.clear_all_data()
                st.session_state.messages = []
                st.success("Data cleared!")
                st.rerun()

        with col2:
            if st.button("📥 Export", use_container_width=True):
                export_data = st.session_state.backend.export_session_data()
                st.download_button(
                    "💾 Download",
                    data=json.dumps(export_data, indent=2),
                    file_name="studymate_session.json",
                    mime="application/json",
                    use_container_width=True
                )

def render_home_page():
    """Render the enhanced home page"""
    # Welcome section
    st.markdown("""
    <div class="custom-card fade-in-up">
        <h2>🎓 Welcome to StudyMate!</h2>
        <p style="font-size: 1.1rem; color: var(--text-secondary);">
            Transform your study experience with AI-powered document analysis. Upload your PDFs,
            ask questions, and get instant, contextual answers from your study materials.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Feature cards
    st.markdown("### ✨ Key Features")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="feature-card fade-in-up">
            <div class="feature-icon">📚</div>
            <h3>Smart Document Processing</h3>
            <p>Advanced PDF text extraction with intelligent chunking and metadata preservation for optimal understanding.</p>
            <div style="margin-top: 1rem;">
                <span style="background: var(--primary-color); color: white; padding: 0.25rem 0.5rem; border-radius: 0.5rem; font-size: 0.8rem;">
                    PyMuPDF Powered
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card fade-in-up">
            <div class="feature-icon">🔍</div>
            <h3>Intelligent Search</h3>
            <p>Advanced TF-IDF based semantic search with enhanced ranking and relevance scoring for precise results.</p>
            <div style="margin-top: 1rem;">
                <span style="background: var(--secondary-color); color: white; padding: 0.25rem 0.5rem; border-radius: 0.5rem; font-size: 0.8rem;">
                    TF-IDF Enhanced
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature-card fade-in-up">
            <div class="feature-icon">💬</div>
            <h3>Interactive Q&A</h3>
            <p>Natural language question answering with source attribution, confidence scoring, and conversation history.</p>
            <div style="margin-top: 1rem;">
                <span style="background: var(--accent-color); color: white; padding: 0.25rem 0.5rem; border-radius: 0.5rem; font-size: 0.8rem;">
                    Context Aware
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Statistics section
    stats = st.session_state.backend.get_system_stats()
    if stats['documents_processed'] > 0:
        st.markdown("### 📊 Your Progress")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Documents Processed",
                stats['documents_processed'],
                help="Total number of PDF documents you've uploaded"
            )

        with col2:
            st.metric(
                "Text Chunks",
                stats['total_chunks'],
                help="Number of text segments created for search"
            )

        with col3:
            session_stats = stats.get('session_stats', {})
            st.metric(
                "Questions Asked",
                session_stats.get('questions_answered', 0),
                help="Total questions you've asked this session"
            )

        with col4:
            st.metric(
                "Session Time",
                f"{session_stats.get('session_duration_minutes', 0):.1f}m",
                help="Time spent in current session"
            )

    # Quick start section
    st.markdown("### 🚀 Quick Start")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📁 Upload Documents", type="primary", use_container_width=True):
            st.session_state.current_page = "upload"
            st.rerun()

    with col2:
        if st.button("💬 Start Chatting", use_container_width=True):
            st.session_state.current_page = "chat"
            st.rerun()

    with col3:
        if st.button("📊 View Analytics", use_container_width=True):
            st.session_state.current_page = "analytics"
            st.rerun()

    # Tips section
    if stats['documents_processed'] == 0:
        st.markdown("### 💡 Getting Started Tips")

        st.markdown("""
        <div class="custom-card">
            <h4>📋 How to Use StudyMate:</h4>
            <ol>
                <li><strong>Upload PDFs:</strong> Click "Upload Documents" and select your study materials</li>
                <li><strong>Wait for Processing:</strong> StudyMate will extract and index the text</li>
                <li><strong>Ask Questions:</strong> Go to "Chat" and ask questions in natural language</li>
                <li><strong>Review Sources:</strong> Check the source documents for each answer</li>
                <li><strong>Explore Analytics:</strong> View detailed statistics about your documents</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

def render_upload_page():
    """Render the enhanced document upload page"""
    st.markdown("## 📁 Upload Study Documents")

    # Upload instructions
    st.markdown("""
    <div class="custom-card">
        <h4>📋 Upload Instructions</h4>
        <ul>
            <li><strong>Supported Format:</strong> PDF files only</li>
            <li><strong>File Size Limit:</strong> 50MB per file</li>
            <li><strong>Maximum Files:</strong> 10 files per upload</li>
            <li><strong>Best Results:</strong> Text-based PDFs work better than scanned images</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # File uploader with enhanced styling
    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type=['pdf'],
        accept_multiple_files=True,
        help="Select one or more PDF files to upload and process",
        label_visibility="collapsed"
    )

    if uploaded_files:
        st.markdown("### 📋 File Validation")

        total_size = 0
        valid_files = []
        invalid_files = []

        # Validate each file
        for file in uploaded_files:
            size_mb = file.size / (1024 * 1024)
            total_size += size_mb

            if size_mb <= 50:  # 50MB limit
                valid_files.append(file)
            else:
                invalid_files.append((file.name, size_mb))

        # Display validation results
        if valid_files:
            st.markdown("#### ✅ Valid Files")

            for file in valid_files:
                size_mb = file.size / (1024 * 1024)
                col1, col2, col3 = st.columns([3, 1, 1])

                with col1:
                    st.write(f"📄 **{file.name}**")
                with col2:
                    st.write(f"{size_mb:.1f} MB")
                with col3:
                    st.success("Valid")

        if invalid_files:
            st.markdown("#### ❌ Invalid Files")

            for filename, size_mb in invalid_files:
                col1, col2, col3 = st.columns([3, 1, 1])

                with col1:
                    st.write(f"📄 **{filename}**")
                with col2:
                    st.write(f"{size_mb:.1f} MB")
                with col3:
                    st.error("Too large")

        # Summary
        if valid_files:
            st.markdown("#### 📊 Upload Summary")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Valid Files", len(valid_files))
            with col2:
                st.metric("Invalid Files", len(invalid_files))
            with col3:
                valid_size = sum(f.size for f in valid_files) / (1024 * 1024)
                st.metric("Total Size", f"{valid_size:.1f} MB")
            with col4:
                st.metric("Estimated Chunks", f"~{len(valid_files) * 15}")

            # Process button
            st.markdown("---")

            col1, col2, col3 = st.columns([1, 2, 1])

            with col2:
                if st.button("🚀 Process Documents", type="primary", use_container_width=True):
                    process_documents(valid_files)
        else:
            st.warning("⚠️ No valid files to process. Please check file sizes and formats.")

    else:
        # Show current documents if any
        stats = st.session_state.backend.get_system_stats()
        if stats['documents_processed'] > 0:
            st.markdown("### 📚 Currently Loaded Documents")

            documents = st.session_state.backend.get_document_list()

            for i, doc in enumerate(documents, 1):
                with st.expander(f"📄 {doc['filename']}"):
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("Pages", doc['pages'])
                    with col2:
                        st.metric("Words", f"{doc['words']:,}")
                    with col3:
                        st.metric("Chunks", doc['chunks'])

            st.info("💡 You can upload additional documents to expand your knowledge base.")

def process_documents(uploaded_files):
    """Process uploaded documents with enhanced progress tracking"""
    # Create progress containers
    progress_container = st.container()
    status_container = st.container()
    results_container = st.container()

    with progress_container:
        st.markdown("### 🔄 Processing Documents")
        progress_bar = st.progress(0)
        status_text = st.empty()

    try:
        # Step 1: Save files temporarily
        status_text.text("💾 Saving uploaded files...")
        progress_bar.progress(10)

        temp_paths = []
        temp_dir = Path("temp")
        temp_dir.mkdir(exist_ok=True)

        for i, uploaded_file in enumerate(uploaded_files):
            temp_path = temp_dir / uploaded_file.name

            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            temp_paths.append(temp_path)

            # Update progress
            progress = 10 + (i + 1) / len(uploaded_files) * 20
            progress_bar.progress(int(progress))

        # Step 2: Process files
        status_text.text("📝 Extracting text from PDFs...")
        progress_bar.progress(40)

        result = st.session_state.backend.process_uploaded_files(temp_paths)

        progress_bar.progress(80)
        status_text.text("🔍 Building search index...")

        # Step 3: Complete
        progress_bar.progress(100)
        status_text.text("✅ Processing complete!")

        # Clean up temp files
        for temp_path in temp_paths:
            if temp_path.exists():
                temp_path.unlink()

        # Remove temp directory if empty
        if temp_dir.exists() and not any(temp_dir.iterdir()):
            temp_dir.rmdir()

        # Display results
        with results_container:
            if result['success']:
                st.success(f"🎉 {result['message']}")

                # Processing statistics
                st.markdown("#### 📊 Processing Results")

                stats = result['stats']

                # Main metrics
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Files Processed", stats.get('successful_files', 0))
                with col2:
                    st.metric("Total Pages", stats.get('total_pages', 0))
                with col3:
                    st.metric("Total Words", f"{stats.get('total_words', 0):,}")
                with col4:
                    st.metric("Text Chunks", result.get('num_chunks', 0))

                # Additional metrics
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Processing Time", f"{result.get('processing_time', 0):.1f}s")
                with col2:
                    st.metric("Average Words/File", f"{stats.get('average_words_per_file', 0):.0f}")
                with col3:
                    st.metric("Total Chunks", result.get('total_chunks', 0))

                # Failed files (if any)
                failed_files = result.get('failed_files', [])
                if failed_files:
                    st.markdown("#### ⚠️ Failed Files")
                    for failed_file in failed_files:
                        st.warning(f"❌ {failed_file['filename']}: {failed_file['error']}")

                # Success actions
                st.markdown("#### 🎯 What's Next?")

                col1, col2, col3 = st.columns(3)

                with col1:
                    if st.button("💬 Start Asking Questions", type="primary", use_container_width=True):
                        st.session_state.current_page = "chat"
                        st.rerun()

                with col2:
                    if st.button("📊 View Analytics", use_container_width=True):
                        st.session_state.current_page = "analytics"
                        st.rerun()

                with col3:
                    if st.button("📁 Upload More", use_container_width=True):
                        st.rerun()

                # Celebration
                st.balloons()

            else:
                st.error(f"❌ Processing failed: {result['message']}")

                # Show any partial results or suggestions
                if 'stats' in result and result['stats']:
                    st.markdown("#### 📋 Partial Results")
                    st.json(result['stats'])

                st.markdown("#### 💡 Troubleshooting Tips")
                st.markdown("""
                - Ensure your PDFs contain readable text (not just images)
                - Check that file sizes are under 50MB
                - Try uploading files one at a time
                - Make sure PDFs are not password protected
                """)

    except Exception as e:
        with results_container:
            st.error(f"❌ An unexpected error occurred: {str(e)}")

            st.markdown("#### 🔧 Error Details")
            st.code(str(e))

            st.markdown("#### 💡 What to try:")
            st.markdown("""
            - Refresh the page and try again
            - Upload fewer files at once
            - Check that your PDFs are valid and readable
            - Contact support if the problem persists
            """)

    finally:
        # Clean up any remaining temp files
        temp_dir = Path("temp")
        if temp_dir.exists():
            for temp_file in temp_dir.glob("*"):
                try:
                    temp_file.unlink()
                except:
                    pass
            try:
                temp_dir.rmdir()
            except:
                pass

def render_chat_page():
    """Render the enhanced chat page"""
    st.markdown("## 💬 Chat with Your Documents")

    # Check if documents are processed
    stats = st.session_state.backend.get_system_stats()

    if not stats['ready_for_questions']:
        st.markdown("""
        <div class="custom-card">
            <h4>⚠️ No Documents Loaded</h4>
            <p>You need to upload and process documents before you can start asking questions.</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            if st.button("📁 Upload Documents", type="primary", use_container_width=True):
                st.session_state.current_page = "upload"
                st.rerun()

        with col2:
            if st.button("🏠 Go to Home", use_container_width=True):
                st.session_state.current_page = "home"
                st.rerun()

        return

    # Chat statistics
    if st.session_state.messages:
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Messages", len(st.session_state.messages))

        with col2:
            user_messages = [m for m in st.session_state.messages if m["role"] == "user"]
            st.metric("Questions Asked", len(user_messages))

        with col3:
            assistant_messages = [m for m in st.session_state.messages if m["role"] == "assistant" and "confidence" in m]
            if assistant_messages:
                avg_confidence = sum(m["confidence"] for m in assistant_messages) / len(assistant_messages)
                st.metric("Avg Confidence", f"{avg_confidence:.1f}%")

    # Display chat messages with enhanced styling
    chat_container = st.container()

    with chat_container:
        for i, message in enumerate(st.session_state.messages):
            if message["role"] == "user":
                # User message
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>You:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)

            else:
                # Assistant message
                st.markdown(f"""
                <div class="chat-message assistant-message">
                    <strong>StudyMate:</strong>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(message["content"])

                # Enhanced source display
                if "sources" in message and message["sources"]:
                    confidence = message.get("confidence", 0)
                    confidence_color = "🟢" if confidence > 70 else "🟡" if confidence > 40 else "🔴"

                    with st.expander(f"📚 Sources ({len(message['sources'])} documents) {confidence_color} {confidence:.1f}% confidence"):
                        for j, source in enumerate(message["sources"], 1):
                            st.markdown(f"**{j}. {source['filename']}**")

                            # Enhanced source metrics
                            col1, col2, col3 = st.columns(3)

                            with col1:
                                st.metric("Similarity", f"{source.get('similarity_score', 0):.3f}")
                            with col2:
                                st.metric("Enhanced Score", f"{source.get('enhanced_score', 0):.3f}")
                            with col3:
                                st.metric("Matched Terms", source.get('matched_terms', 0))

                            # Relevance explanation
                            if 'relevance_explanation' in source:
                                st.info(f"💡 {source['relevance_explanation']}")

                            # Text preview
                            st.markdown("**Text Preview:**")
                            st.markdown(f"```\n{source['text_preview']}\n```")

                            if j < len(message["sources"]):
                                st.markdown("---")

                # Insights (if available)
                if "insights" in message and message["insights"]:
                    insights = message["insights"]
                    if insights.get('suggestion'):
                        st.info(f"💡 **Suggestion:** {insights['suggestion']}")

    # Sample questions for new users
    if not st.session_state.messages:
        st.markdown("### 💡 Sample Questions to Get Started")

        # Get suggested questions from backend
        suggested_questions = st.session_state.backend.qa_engine.suggest_questions(6)

        if suggested_questions:
            col1, col2 = st.columns(2)

            for i, question in enumerate(suggested_questions):
                col = col1 if i % 2 == 0 else col2

                with col:
                    if st.button(f"❓ {question}", key=f"sample_q_{i}", use_container_width=True):
                        # Add question to chat
                        st.session_state.messages.append({"role": "user", "content": question})
                        st.rerun()

        else:
            # Fallback sample questions
            sample_questions = [
                "What are the main topics covered in these documents?",
                "Can you summarize the key concepts?",
                "What are the important definitions?",
                "What examples are provided?",
                "What are the main conclusions?",
                "How do these concepts relate to each other?"
            ]

            col1, col2 = st.columns(2)

            for i, question in enumerate(sample_questions):
                col = col1 if i % 2 == 0 else col2

                with col:
                    if st.button(f"❓ {question}", key=f"fallback_q_{i}", use_container_width=True):
                        st.session_state.messages.append({"role": "user", "content": question})
                        st.rerun()

    # Chat input with enhanced placeholder
    document_count = stats['documents_processed']
    chunk_count = stats['total_chunks']

    placeholder_text = f"Ask a question about your {document_count} document(s) with {chunk_count} searchable sections..."

    if prompt := st.chat_input(placeholder_text):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Generate response
        with st.spinner("🤔 Analyzing your documents..."):
            response = st.session_state.backend.ask_question(prompt)

        # Add assistant message with all metadata
        assistant_message = {
            "role": "assistant",
            "content": response["answer"],
            "sources": response.get("sources", []),
            "confidence": response.get("confidence", 0),
            "insights": response.get("insights", {}),
            "num_results": response.get("num_results", 0)
        }
        st.session_state.messages.append(assistant_message)

        # Rerun to display new messages
        st.rerun()

    # Enhanced chat controls
    if st.session_state.messages:
        st.markdown("---")
        st.markdown("### 🛠️ Chat Controls")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.messages = []
                st.session_state.backend.qa_engine.clear_conversation_history()
                st.rerun()

        with col2:
            if st.button("📥 Export Chat", use_container_width=True):
                export_chat()

        with col3:
            if st.button("📊 Chat Stats", use_container_width=True):
                show_chat_statistics()

        with col4:
            if st.button("🔄 New Session", use_container_width=True):
                st.session_state.messages = []
                st.session_state.backend.qa_engine.clear_conversation_history()
                st.success("Started new chat session!")
                st.rerun()

def show_chat_statistics():
    """Show detailed chat statistics in a modal-like display"""
    conversation_summary = st.session_state.backend.qa_engine.get_conversation_summary()

    if conversation_summary['total_questions'] == 0:
        st.info("No questions asked yet in this session.")
        return

    st.markdown("#### 📊 Chat Session Statistics")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Questions", conversation_summary['total_questions'])

    with col2:
        st.metric("Average Confidence", f"{conversation_summary['avg_confidence']}%")

    with col3:
        st.metric("Topics Discussed", len(conversation_summary['topics']))

    if conversation_summary['topics']:
        st.markdown("**Common Topics:**")
        st.write(", ".join(conversation_summary['topics']))

    if conversation_summary['recent_questions']:
        st.markdown("**Recent Questions:**")
        for i, question in enumerate(conversation_summary['recent_questions'], 1):
            st.write(f"{i}. {question}")

def render_analytics_page():
    """Render the comprehensive analytics page"""
    st.markdown("## 📊 Analytics & Insights")

    stats = st.session_state.backend.get_system_stats()

    if stats['documents_processed'] == 0:
        st.markdown("""
        <div class="custom-card">
            <h4>📄 No Data Available</h4>
            <p>Upload and process some documents to see detailed analytics and insights.</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("📁 Upload Documents", type="primary"):
            st.session_state.current_page = "upload"
            st.rerun()

        return

    # Get detailed analytics
    detailed_analytics = st.session_state.backend.get_detailed_analytics()

    # Overview metrics
    st.markdown("### 📈 Overview")

    col1, col2, col3, col4 = st.columns(4)

    doc_analytics = detailed_analytics['document_analytics']

    with col1:
        st.metric("Documents", doc_analytics['total_documents'])

    with col2:
        st.metric("Total Pages", doc_analytics['total_pages'])

    with col3:
        st.metric("Total Words", f"{doc_analytics['total_words']:,}")

    with col4:
        st.metric("File Size", f"{doc_analytics['total_size_mb']} MB")

    # Document analytics
    st.markdown("### 📚 Document Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📊 Document Metrics")

        metrics_data = {
            "Average Pages per Document": doc_analytics['avg_pages_per_doc'],
            "Average Words per Document": f"{doc_analytics['avg_words_per_doc']:,.0f}",
            "Total Text Chunks": stats['total_chunks'],
            "Unique Sources": stats.get('unique_sources', 0)
        }

        for metric, value in metrics_data.items():
            st.write(f"**{metric}:** {value}")

    with col2:
        st.markdown("#### 🔍 Search Engine Stats")

        search_analytics = detailed_analytics['search_analytics']

        search_data = {
            "Vocabulary Size": f"{search_analytics.get('vocabulary_size', 0):,} terms",
            "Average Document Length": f"{search_analytics.get('average_doc_length', 0):.1f} tokens",
            "Total Tokens": f"{search_analytics.get('total_tokens', 0):,}",
            "Index Status": "✅ Ready" if search_analytics.get('indexed', False) else "❌ Not Ready"
        }

        for metric, value in search_data.items():
            st.write(f"**{metric}:** {value}")

    # Document details
    st.markdown("### 📋 Document Details")

    documents = st.session_state.backend.get_document_list()

    for i, doc in enumerate(documents, 1):
        with st.expander(f"📄 {i}. {doc['filename']}"):
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Pages", doc['pages'])
            with col2:
                st.metric("Words", f"{doc['words']:,}")
            with col3:
                st.metric("Chunks", doc['chunks'])
            with col4:
                words_per_page = doc['words'] / doc['pages'] if doc['pages'] > 0 else 0
                st.metric("Words/Page", f"{words_per_page:.0f}")

    # Processing analytics
    processing_analytics = detailed_analytics['processing_analytics']

    if processing_analytics['total_processing_sessions'] > 0:
        st.markdown("### ⚙️ Processing Performance")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Processing Sessions", processing_analytics['total_processing_sessions'])

        with col2:
            st.metric("Success Rate", f"{processing_analytics['successful_sessions']}/{processing_analytics['total_processing_sessions']}")

        with col3:
            st.metric("Avg Processing Time", f"{processing_analytics['avg_processing_time']:.1f}s")

    # Q&A analytics
    qa_analytics = detailed_analytics['qa_analytics']

    if qa_analytics['total_questions'] > 0:
        st.markdown("### 💬 Q&A Performance")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Questions Asked", qa_analytics['total_questions'])

        with col2:
            st.metric("Average Confidence", f"{qa_analytics['avg_confidence']}%")

        with col3:
            st.metric("Topics Discussed", len(qa_analytics.get('topics', [])))

        # Topic analysis
        if qa_analytics.get('topics'):
            st.markdown("#### 🏷️ Most Discussed Topics")

            topics_text = ", ".join(qa_analytics['topics'][:10])  # Top 10 topics
            st.write(topics_text)

        # Recent questions
        if qa_analytics.get('recent_questions'):
            st.markdown("#### ❓ Recent Questions")

            for i, question in enumerate(qa_analytics['recent_questions'], 1):
                st.write(f"{i}. {question}")

    # Session analytics
    session_stats = stats.get('session_stats', {})

    if session_stats:
        st.markdown("### 📅 Session Information")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Session Duration", f"{session_stats.get('session_duration_minutes', 0):.1f} minutes")

        with col2:
            st.metric("Documents This Session", session_stats.get('documents_processed', 0))

        with col3:
            st.metric("Questions This Session", session_stats.get('questions_answered', 0))

    # Export options
    st.markdown("### 📥 Export Options")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📊 Export Analytics", use_container_width=True):
            analytics_json = json.dumps(detailed_analytics, indent=2)
            st.download_button(
                "💾 Download Analytics JSON",
                data=analytics_json,
                file_name="studymate_analytics.json",
                mime="application/json",
                use_container_width=True
            )

    with col2:
        if st.button("📋 Export Session Data", use_container_width=True):
            session_data = st.session_state.backend.export_session_data()
            session_json = json.dumps(session_data, indent=2)
            st.download_button(
                "💾 Download Session Data",
                data=session_json,
                file_name="studymate_session.json",
                mime="application/json",
                use_container_width=True
            )

def export_chat():
    """Export enhanced chat history with metadata"""
    if not st.session_state.messages:
        st.warning("No chat history to export")
        return

    # Create detailed export content
    export_content = "StudyMate Chat History\n"
    export_content += "=" * 60 + "\n"
    export_content += f"Export Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
    export_content += f"Total Messages: {len(st.session_state.messages)}\n"

    # Add session statistics
    stats = st.session_state.backend.get_system_stats()
    export_content += f"Documents Processed: {stats['documents_processed']}\n"
    export_content += f"Total Chunks: {stats['total_chunks']}\n"
    export_content += "=" * 60 + "\n\n"

    # Export each message with metadata
    for i, message in enumerate(st.session_state.messages, 1):
        role = "You" if message["role"] == "user" else "StudyMate"
        export_content += f"Message {i} - {role}:\n"
        export_content += f"{message['content']}\n"

        # Add metadata for assistant messages
        if message["role"] == "assistant":
            if "confidence" in message:
                export_content += f"Confidence: {message['confidence']:.1f}%\n"

            if "sources" in message and message["sources"]:
                export_content += f"Sources ({len(message['sources'])}):\n"
                for j, source in enumerate(message["sources"], 1):
                    export_content += f"  {j}. {source['filename']} (Score: {source.get('similarity_score', 0):.3f})\n"

        export_content += "\n" + "-" * 40 + "\n\n"

    # Provide download options
    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            label="📄 Download as Text",
            data=export_content,
            file_name=f"studymate_chat_{time.strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True
        )

    with col2:
        # JSON export
        chat_data = {
            "export_info": {
                "export_date": time.strftime('%Y-%m-%d %H:%M:%S'),
                "total_messages": len(st.session_state.messages),
                "session_stats": stats
            },
            "messages": st.session_state.messages
        }

        st.download_button(
            label="📊 Download as JSON",
            data=json.dumps(chat_data, indent=2),
            file_name=f"studymate_chat_{time.strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )

def render_settings_page():
    """Render the settings and configuration page"""
    st.markdown("## ⚙️ Settings & Configuration")

    # Application settings
    st.markdown("### 🎛️ Application Settings")

    with st.expander("📊 Current Configuration", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Text Processing:**")
            st.write(f"• Chunk Size: {config.CHUNK_SIZE} characters")
            st.write(f"• Chunk Overlap: {config.CHUNK_OVERLAP} characters")
            st.write(f"• Min Chunk Size: {config.MIN_CHUNK_SIZE} characters")

        with col2:
            st.markdown("**Search Settings:**")
            st.write(f"• Max Search Results: {config.MAX_SEARCH_RESULTS}")
            st.write(f"• Min Similarity Score: {config.MIN_SIMILARITY_SCORE}")
            st.write(f"• Allowed Extensions: {', '.join(config.ALLOWED_EXTENSIONS)}")

    # File settings
    st.markdown("### 📁 File Management")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Upload Limits:**")
        st.write(f"• Max File Size: {config.MAX_FILE_SIZE_MB} MB")
        st.write(f"• Max Files per Upload: {config.MAX_FILES_UPLOAD}")
        st.write(f"• Supported Formats: {', '.join(config.ALLOWED_EXTENSIONS).upper()}")

    with col2:
        st.markdown("**Storage Locations:**")
        st.write(f"• Upload Directory: `{config.UPLOAD_DIR}`")
        st.write(f"• Processed Directory: `{config.PROCESSED_DIR}`")
        st.write(f"• Logs Directory: `{config.LOGS_DIR}`")

    # System information
    st.markdown("### 💻 System Information")

    stats = st.session_state.backend.get_system_stats()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Current Session:**")
        session_stats = stats.get('session_stats', {})
        st.write(f"• Session Duration: {session_stats.get('session_duration_minutes', 0):.1f} minutes")
        st.write(f"• Documents Processed: {session_stats.get('documents_processed', 0)}")
        st.write(f"• Questions Answered: {session_stats.get('questions_answered', 0)}")

    with col2:
        st.markdown("**System Status:**")
        st.write(f"• Total Documents: {stats['documents_processed']}")
        st.write(f"• Total Chunks: {stats['total_chunks']}")
        st.write(f"• Ready for Questions: {'✅ Yes' if stats['ready_for_questions'] else '❌ No'}")

    # Data management
    st.markdown("### 🗂️ Data Management")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🗑️ Clear All Documents", use_container_width=True):
            if st.button("⚠️ Confirm Clear All", type="secondary", use_container_width=True):
                st.session_state.backend.clear_all_data()
                st.session_state.messages = []
                st.success("All data cleared successfully!")
                st.rerun()

    with col2:
        if st.button("💬 Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.session_state.backend.qa_engine.clear_conversation_history()
            st.success("Chat history cleared!")
            st.rerun()

    with col3:
        if st.button("🔄 Reset Session", use_container_width=True):
            # Reset session stats but keep documents
            st.session_state.backend.session_stats['questions_answered'] = 0
            st.session_state.messages = []
            st.session_state.backend.qa_engine.clear_conversation_history()
            st.success("Session reset!")
            st.rerun()

    # Advanced settings
    st.markdown("### 🔧 Advanced Options")

    with st.expander("🐛 Debug Information"):
        st.markdown("**Search Engine Debug:**")

        if stats['ready_for_questions']:
            debug_info = st.session_state.backend.qa_engine.search_engine.search_debug("test query")
            st.json(debug_info)
        else:
            st.info("Upload documents to see debug information")

    with st.expander("📊 Detailed Statistics"):
        if stats['documents_processed'] > 0:
            detailed_stats = st.session_state.backend.get_detailed_analytics()
            st.json(detailed_stats)
        else:
            st.info("No detailed statistics available")

    # About section
    st.markdown("### ℹ️ About StudyMate")

    st.markdown("""
    <div class="custom-card">
        <h4>📚 StudyMate v1.0.0</h4>
        <p><strong>AI-Powered Academic Assistant</strong></p>

        <p><strong>Technologies Used:</strong></p>
        <ul>
            <li>🐍 Python 3.8+</li>
            <li>🎨 Streamlit (Web Interface)</li>
            <li>📄 PyMuPDF (PDF Processing)</li>
            <li>🔍 TF-IDF (Search Algorithm)</li>
            <li>📊 Pandas & NumPy (Data Processing)</li>
            <li>🧠 Scikit-learn (Machine Learning)</li>
        </ul>

        <p><strong>Features:</strong></p>
        <ul>
            <li>✅ Smart PDF text extraction</li>
            <li>✅ Intelligent text chunking</li>
            <li>✅ Advanced semantic search</li>
            <li>✅ Interactive Q&A interface</li>
            <li>✅ Comprehensive analytics</li>
            <li>✅ Export capabilities</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main application function - Direct access without authentication"""
    st.set_page_config(
        page_title="StudyMate - AI Academic Assistant",
        page_icon="📚",
        layout="wide"
    )

    # Apply custom CSS
    st.markdown(get_custom_css(), unsafe_allow_html=True)

    # Initialize session state
    initialize_session_state()

    # Render header
    render_header()

    # Render sidebar
    render_sidebar()

    # Render main content based on current page
    current_page = st.session_state.current_page

    try:
        if current_page == "home":
            render_home_page()
        elif current_page == "upload":
            render_upload_page()
        elif current_page == "chat":
            render_chat_page()
        elif current_page == "analytics":
            render_analytics_page()
        elif current_page == "settings":
            render_settings_page()
        else:
            render_home_page()

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.markdown("### 🔧 Troubleshooting")
        st.markdown("""
        - Try refreshing the page
        - Clear your browser cache
        - Check the console for detailed error messages
        - Go back to the Home page and try again
        """)

        if st.button("🏠 Go to Home"):
            st.session_state.current_page = "home"
            st.rerun()

if __name__ == "__main__":
    main()
