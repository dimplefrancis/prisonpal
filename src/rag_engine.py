"""RAG implementation using Cohere and Qdrant for prison visitor assistance."""
import os
from typing import List, Tuple, Optional
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_cohere import CohereEmbeddings, ChatCohere
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain import hub
from langchain.prompts import PromptTemplate
from . import config

class RAGEngine:
    """RAG Engine for prison visitor assistance."""
    
    def __init__(self):
        """Initialize the RAG engine with Cohere and Qdrant clients."""
        self.embedding = CohereEmbeddings(
            model=config.COHERE_EMBEDDING_MODEL,
            cohere_api_key=config.COHERE_API_KEY
        )
        
        self.chat_model = ChatCohere(
            model=config.COHERE_CHAT_MODEL,
            temperature=0.1,
            max_tokens=512,
            cohere_api_key=config.COHERE_API_KEY
        )
        
        self.qdrant_client = QdrantClient(
            url=config.QDRANT_URL,
            api_key=config.QDRANT_API_KEY,
            timeout=60
        )
        
        self.vectorstore = None
        self.init_vectorstore()
        
        # Load all configured PDFs
        self.load_all_documents()
        
    def init_vectorstore(self) -> None:
        """Initialize or connect to the vector store."""
        try:
            # Try to create collection if it doesn't exist
            self.qdrant_client.create_collection(
                collection_name=config.COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=1024,
                    distance=Distance.COSINE
                )
            )
        except Exception as e:
            if "already exists" not in str(e).lower():
                raise e
        
        self.vectorstore = QdrantVectorStore(
            client=self.qdrant_client,
            collection_name=config.COLLECTION_NAME,
            embedding=self.embedding
        )

    def process_document(self, file_path: str) -> List[dict]:
        """
        Process a PDF document and split it into chunks.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            List of document chunks
        """
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        return text_splitter.split_documents(documents)

    def load_all_documents(self) -> None:
        """Load all configured PDF documents into the vector store."""
        # Clear existing documents
        self.clear_vectorstore()
        self.init_vectorstore()
        
        # Process and add each document
        for doc_type, path in config.PDF_PATHS.items():
            try:
                documents = self.process_document(path)
                self.add_documents(documents)
            except Exception as e:
                print(f"Error loading {doc_type} document: {str(e)}")

    def add_documents(self, documents: List[dict]) -> None:
        """
        Add documents to the vector store.
        
        Args:
            documents: List of document chunks to add
        """
        if not self.vectorstore:
            self.init_vectorstore()
        
        self.vectorstore.add_documents(documents)

    def process_query(self, query: str) -> Tuple[str, List]:
        """
        Process a user query using RAG.
        
        Args:
            query: User's question
            
        Returns:
            Tuple of (answer, relevant documents)
        """
        if not self.vectorstore:
            self.init_vectorstore()

        # Configure retriever with similarity threshold
        retriever = self.vectorstore.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={
                "k": 5,
                "score_threshold": 0.6
            }
        )

        # Get relevant documents
        relevant_docs = retriever.get_relevant_documents(query)

        if relevant_docs:
            # Determine the type of query
            query_type = 'general'
            if 'dress' in query.lower() or 'wear' in query.lower():
                query_type = 'dress_code'
            elif 'id' in query.lower() or 'identification' in query.lower():
                query_type = 'id'

            # Create a specific prompt based on query type
            if query_type == 'dress_code':
                prompt = PromptTemplate.from_template(
                    """Based on the prison visitor dress code documents, provide a clear and specific answer about what visitors can and cannot wear.

                    Focus on:
                    1. List all items of clothing that are not allowed
                    2. Mention any exceptions (like religious clothing)
                    3. State what happens if someone doesn't follow the dress code

                    Only include information that is explicitly stated in the documents.

                    Documents:
                    {context}

                    Question: {input}
                    Answer:"""
                )
            elif query_type == 'id':
                prompt = PromptTemplate.from_template(
                    """Based on the prison visitor ID requirement documents, provide a clear and specific answer about identification requirements.

                    Focus on:
                    1. List all acceptable forms of ID
                    2. Mention any exceptions (like for children under 16)
                    3. Explain what happens if someone doesn't have proper ID

                    Only include information that is explicitly stated in the documents.

                    Documents:
                    {context}

                    Question: {input}
                    Answer:"""
                )
            else:
                prompt = PromptTemplate.from_template(
                    """Based on the following documents, provide a clear and specific answer to the question.

                    Only include information that is explicitly stated in the documents.

                    Documents:
                    {context}

                    Question: {input}
                    Answer:"""
                )

            # Create and run the chain
            combine_docs_chain = create_stuff_documents_chain(
                self.chat_model,
                prompt
            )
            retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)
            response = retrieval_chain.invoke({"input": query})
            return response['answer'], relevant_docs

        return "I apologize, but I couldn't find specific information to answer your question in the available documents. Please contact the prison directly for more information.", []

    def clear_vectorstore(self) -> None:
        """Clear all documents from the vector store."""
        if self.qdrant_client.collection_exists(config.COLLECTION_NAME):
            self.qdrant_client.delete_collection(config.COLLECTION_NAME)
        self.vectorstore = None
