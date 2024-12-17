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
from . import config
from .web_search import GovUKSearcher

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
        self.web_searcher = GovUKSearcher()
        
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
        Process a user query using RAG with fallback to web search.
        
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
                "score_threshold": 0.7
            }
        )

        # Get relevant documents
        relevant_docs = retriever.get_relevant_documents(query)

        # If relevant documents found, use RAG
        if relevant_docs:
            retrieval_qa_prompt = hub.pull("langchain-ai/retrieval-qa-chat")
            combine_docs_chain = create_stuff_documents_chain(
                self.chat_model, 
                retrieval_qa_prompt
            )
            retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)
            response = retrieval_chain.invoke({"input": query})
            return response['answer'], relevant_docs

        # If no relevant documents, try web search fallback
        if "id" in query.lower():
            content = self.web_searcher.get_id_requirements()
        elif "dress" in query.lower() or "wear" in query.lower():
            content = self.web_searcher.get_dress_code()
        else:
            content = None

        if content:
            # Use chat model to formulate response from web content
            prompt = f"""Based on the following information from gov.uk, answer the user's question: {query}

            Information:
            {content}

            Please provide a clear and concise answer focused specifically on what was asked."""
            
            response = self.chat_model.invoke(prompt).content
            return response, []

        # If all else fails, provide a generic response
        return "I apologize, but I couldn't find specific information to answer your question. Please contact the prison directly or visit gov.uk for more information.", []

    def clear_vectorstore(self) -> None:
        """Clear all documents from the vector store."""
        if self.qdrant_client.collection_exists(config.COLLECTION_NAME):
            self.qdrant_client.delete_collection(config.COLLECTION_NAME)
        self.vectorstore = None