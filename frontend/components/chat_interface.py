"""
Chat interface component for StudyMate
"""

import streamlit as st
from typing import List, Dict, Optional
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from qa_engine import QAEngine

def initialize_chat():
    """Initialize chat interface"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'qa_engine' not in st.session_state:
        st.session_state.qa_engine = QAEngine()

def render_chat_interface():
    """Render the main chat interface"""
    st.subheader("💬 Ask Questions About Your Study Materials")
    
    # Check if documents are processed
    if 'embedding_manager' not in st.session_state or st.session_state.embedding_manager.index is None:
        st.warning("⚠️ Please upload and process documents first before asking questions.")
        return
    
    # Set embedding manager in QA engine
    if 'qa_engine' in st.session_state:
        st.session_state.qa_engine.set_embedding_manager(st.session_state.embedding_manager)
    
    # Display chat messages
    display_chat_history()
    
    # Chat input
    handle_chat_input()
    
    # Chat controls
    render_chat_controls()

def display_chat_history():
    """Display chat message history"""
    if 'messages' not in st.session_state:
        return
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Display sources for assistant messages
            if message["role"] == "assistant" and "sources" in message:
                display_sources(message["sources"], message.get("confidence", 0))

def handle_chat_input():
    """Handle chat input and generate responses"""
    if prompt := st.chat_input("Ask a question about your study materials..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = st.session_state.qa_engine.ask_question(prompt)
            
            # Display answer
            st.markdown(response["answer"])
            
            # Display sources and confidence
            if response["sources"]:
                display_sources(response["sources"], response["confidence"])
            
            # Add assistant message to chat history
            assistant_message = {
                "role": "assistant",
                "content": response["answer"],
                "sources": response["sources"],
                "confidence": response["confidence"]
            }
            st.session_state.messages.append(assistant_message)

def display_sources(sources: List[Dict], confidence: float):
    """
    Display sources and confidence information
    
    Args:
        sources: List of source documents
        confidence: Confidence score
    """
    if not sources:
        return
    
    # Confidence indicator
    confidence_color = "green" if confidence > 70 else "orange" if confidence > 40 else "red"
    st.markdown(f"**Confidence:** :{confidence_color}[{confidence:.1f}%]")
    
    # Sources
    with st.expander(f"📚 Sources ({len(sources)} documents)", expanded=False):
        for i, source in enumerate(sources, 1):
            st.markdown(f"**{i}. {source['filename']}**")
            st.markdown(f"*Relevance: {source['score']:.3f}*")
            st.markdown(f"```\n{source['text_preview']}\n```")
            st.markdown("---")

def render_chat_controls():
    """Render chat control buttons"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🗑️ Clear Chat", help="Clear all chat messages"):
            clear_chat_history()
    
    with col2:
        if st.button("📥 Export Chat", help="Export chat history"):
            export_chat_history()
    
    with col3:
        if st.button("🔄 New Session", help="Start a new chat session"):
            start_new_session()

def clear_chat_history():
    """Clear chat message history"""
    st.session_state.messages = []
    if 'qa_engine' in st.session_state:
        st.session_state.qa_engine.clear_conversation_history()
    st.success("✅ Chat history cleared")
    st.rerun()

def export_chat_history():
    """Export chat history to text file"""
    if 'messages' not in st.session_state or not st.session_state.messages:
        st.warning("No chat history to export")
        return
    
    # Create export content
    export_content = "StudyMate Chat History\n"
    export_content += "=" * 50 + "\n\n"
    
    for message in st.session_state.messages:
        role = "You" if message["role"] == "user" else "StudyMate"
        export_content += f"{role}: {message['content']}\n\n"
        
        if message["role"] == "assistant" and "sources" in message:
            export_content += f"Sources:\n"
            for source in message["sources"]:
                export_content += f"- {source['filename']}\n"
            export_content += "\n"
    
    # Provide download
    st.download_button(
        label="📥 Download Chat History",
        data=export_content,
        file_name="studymate_chat_history.txt",
        mime="text/plain"
    )

def start_new_session():
    """Start a new chat session"""
    # Clear chat history
    st.session_state.messages = []
    
    # Clear QA engine history
    if 'qa_engine' in st.session_state:
        st.session_state.qa_engine.clear_conversation_history()
    
    st.success("✅ Started new chat session")
    st.rerun()

def render_sample_questions():
    """Render sample questions to help users get started"""
    if 'embedding_manager' not in st.session_state or st.session_state.embedding_manager.index is None:
        return
    
    st.subheader("💡 Sample Questions")
    st.markdown("Here are some example questions you can ask:")
    
    sample_questions = [
        "What are the main topics covered in these documents?",
        "Can you summarize the key concepts?",
        "What are the important definitions I should know?",
        "Explain the methodology used in this research",
        "What are the conclusions or findings?",
        "How does this relate to [specific topic]?",
        "What examples are provided in the text?",
        "What are the practical applications mentioned?"
    ]
    
    cols = st.columns(2)
    for i, question in enumerate(sample_questions):
        col = cols[i % 2]
        with col:
            if st.button(f"❓ {question}", key=f"sample_q_{i}"):
                # Add question to chat
                st.session_state.messages.append({"role": "user", "content": question})
                st.rerun()

def display_chat_stats():
    """Display chat statistics"""
    if 'messages' not in st.session_state:
        return
    
    total_messages = len(st.session_state.messages)
    user_messages = len([m for m in st.session_state.messages if m["role"] == "user"])
    assistant_messages = len([m for m in st.session_state.messages if m["role"] == "assistant"])
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Messages", total_messages)
    
    with col2:
        st.metric("Questions Asked", user_messages)
    
    with col3:
        st.metric("Answers Given", assistant_messages)
