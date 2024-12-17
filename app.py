"""Prison Visitor Assistance Tool - Streamlit Application."""
import os
import streamlit as st
from src.rag_engine import RAGEngine
from src.config import validate_config
import tempfile

def init_session_state():
    """Initialize session state variables."""
    if 'api_keys_submitted' not in st.session_state:
        st.session_state.api_keys_submitted = False
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'rag_engine' not in st.session_state:
        st.session_state.rag_engine = None

def sidebar_api_form():
    """Create sidebar form for API credentials."""
    with st.sidebar:
        st.header("API Credentials")
        
        if st.session_state.api_keys_submitted:
            st.success("API credentials verified")
            if st.button("Reset Credentials"):
                st.session_state.clear()
                st.rerun()
            return True
        
        with st.form("api_credentials"):
            cohere_key = st.text_input("Cohere API Key", type="password")
            qdrant_key = st.text_input("Qdrant API Key", type="password", 
                                     help="Enter your Qdrant API key")
            qdrant_url = st.text_input("Qdrant URL", 
                                     placeholder="https://xyz-example.eu-central.aws.cloud.qdrant.io:6333",
                                     help="Enter your Qdrant instance URL")
            
            if st.form_submit_button("Submit Credentials"):
                try:
                    # Set environment variables
                    os.environ['COHERE_API_KEY'] = cohere_key
                    os.environ['QDRANT_API_KEY'] = qdrant_key
                    os.environ['QDRANT_URL'] = qdrant_url
                    
                    # Validate configuration
                    validate_config()
                    
                    # Initialize RAG engine
                    st.session_state.rag_engine = RAGEngine()
                    st.session_state.rag_engine.init_vectorstore()
                    
                    st.session_state.api_keys_submitted = True
                    st.success("Credentials verified!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Configuration failed: {str(e)}")
        return False

def process_uploaded_file(file):
    """Process uploaded PDF file."""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(file.getvalue())
            tmp_path = tmp_file.name
            
            texts = st.session_state.rag_engine.process_document(tmp_path)
            st.session_state.rag_engine.add_documents(texts)
            
            os.unlink(tmp_path)
            return True
    except Exception as e:
        st.error(f"Error processing document: {str(e)}")
        return False

def main():
    """Main application function."""
    st.title("**PrisonPal** 🏢")
    
    # Initialize session state
    init_session_state()
    
    # Handle API credentials
    if not sidebar_api_form():
        st.info("Please enter your API credentials in the sidebar to continue.")
        st.stop()
    
    # File upload section
    uploaded_file = st.file_uploader("Upload Prison Policy Document (PDF)", type=["pdf"])
    if uploaded_file is not None and 'processed_file' not in st.session_state:
        with st.spinner('Processing document... This may take a while.'):
            if process_uploaded_file(uploaded_file):
                st.session_state.processed_file = True
                st.success('Document uploaded and processed successfully!')
            else:
                st.error('Failed to process document. Please try again.')
    
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
        col1, col2 = st.columns(2)
        with col1:
            if st.button('Clear Chat'):
                st.session_state.chat_history = []
                st.rerun()
        with col2:
            if st.button('Clear All Data'):
                try:
                    if st.session_state.rag_engine:
                        st.session_state.rag_engine.clear_vectorstore()
                    st.session_state.chat_history = []
                    st.session_state.processed_file = False
                    st.success("All data cleared successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error clearing data: {str(e)}")

if __name__ == "__main__":
    main()