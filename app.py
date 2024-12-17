"""Prison Visitor Assistance Tool - Streamlit Application."""
import os
import streamlit as st
from src.rag_engine import RAGEngine
from src.config import validate_config

def init_session_state():
    """Initialize session state variables."""
    if 'initialized' not in st.session_state:
        st.session_state.initialized = False
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'rag_engine' not in st.session_state:
        st.session_state.rag_engine = None

def initialize_system():
    """Initialize RAG engine and process policy document."""
    try:
        # Validate configuration
        validate_config()
        
        # Initialize RAG engine
        st.session_state.rag_engine = RAGEngine()
        st.session_state.rag_engine.init_vectorstore()
        
        # Process and ingest all documents
        with st.spinner('Loading all prison documents...'):
            st.session_state.rag_engine.load_all_documents()
        
        st.session_state.initialized = True
        return True
    except Exception as e:
        st.error(f"Configuration error: {str(e)}")
        st.info("Please ensure your .env file is properly configured with the required API credentials.")
        return False

def main():
    """Main application function."""
    st.title("**PrisonPal** 🏢")
    
    # Initialize session state
    init_session_state()
    
    # Initialize system if not already initialized
    if not st.session_state.initialized:
        if not initialize_system():
            st.stop()
    
    # Display example questions
    st.markdown("""
    ### Example Questions You Can Ask:
    - What ID do I need to visit a prison?
    - What is the dress code for prison visitors?
    - What items am I not allowed to bring to a visit?
    """)
    
    # Chat interface
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if query := st.chat_input("Ask a question about prison visits:"):
        st.session_state.chat_history.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)
        
        with st.chat_message("assistant"):
            try:
                answer, sources = st.session_state.rag_engine.process_query(query)
                st.markdown(answer)
                
                if sources:
                    with st.expander("Sources"):
                        for source in sources:
                            st.markdown(f"- {source.page_content[:200]}...")
                
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": answer
                })
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.info("Please try asking your question again.")
    
    # Sidebar controls
    with st.sidebar:
        st.divider()
        if st.button('Clear Chat History'):
            st.session_state.chat_history = []
            st.rerun()

if __name__ == "__main__":
    main()
