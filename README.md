# Prison Visitor Assistant Tool

## Overview
An intelligent assistant that streamlines access to prison visiting information in England and Wales. Built with advanced AI technology, this tool helps visitors understand requirements, policies, and procedures by providing accurate, sourced information from official documents.

## 🎯 Purpose
Navigating prison visit requirements can be challenging. This tool aims to:
- Provide instant, accurate answers to visitor questions
- Reduce uncertainty about visit requirements
- Ensure visitors have the correct documentation
- Help maintain family connections through informed visits

## 💡 Key Capabilities

### Information Access
- Real-time answers about visiting requirements
- Document-based responses with source citations
- Fallback to current gov.uk information when needed
- Context-aware responses to follow-up questions

### Technology Stack
- **AI Engine**: Cohere's Command-r7b-12-2024 
- **Vector Storage**: Qdrant Cloud
- **Embeddings**: Cohere embed-english-v3.0
- **Interface**: Streamlit web application
- **Data Sources**: Official prison policy documents + gov.uk

## 🚀 Getting Started

### Prerequisites
You'll need:
1. Cohere API key for AI functionality
2. Qdrant cloud credentials for vector storage

### Environment Configuration
1. Create a `.env` file in the project root with your API credentials:
```plaintext
# API Keys
COHERE_API_KEY=your_cohere_api_key
QDRANT_API_KEY=your_qdrant_api_key

# Qdrant Configuration
QDRANT_URL=your_qdrant_url

# Base URLs (pre-configured)
GOV_UK_BASE_URL=https://www.gov.uk/government/publications/management-of-security-at-visits-policy-framework-closed-estate
GOV_UK_ID_URL=https://www.gov.uk/government/publications/management-of-security-at-visits-policy-framework-open-estate/acceptable-forms-of-identification-id-when-visiting-a-prison-in-england-and-wales-annex-a
GOV_UK_DRESS_CODE_URL=https://www.gov.uk/government/publications/management-of-security-at-visits-policy-framework-closed-estate/dress-code-for-visitors-annex-h
```

### Environment Setup

**Unix/MacOS**
```bash
chmod +x setup.sh
./setup.sh
source venv/bin/activate
```

**Windows**
```cmd
setup.bat
venv\Scripts\activate
```

### Launch Application
After configuring your `.env` file:
```bash
streamlit run app.py
```

The application will automatically load and process the prison policy document on startup.

## 💻 Development

### Project Structure
```
prison_visitor_assistant/
├── app.py              # Main application
├── src/
│   ├── config.py      # Configuration management
│   ├── rag_engine.py  # Core RAG functionality
│   └── web_search.py  # Gov.uk integration
├── data/
│   └── policy.pdf     # Prison policy document
├── .env               # Environment configuration
└── requirements.txt   # Python dependencies
```

### Core Features
1. **Document Processing**
   - Automatic policy document ingestion
   - Intelligent text chunking
   - Vector embedding storage

2. **Query Processing**
   - RAG-based information retrieval
   - Similarity threshold filtering
   - Automatic source fallback
   - Answer generation with citations

3. **User Interface**
   - Intuitive chat interface
   - Source attribution
   - Example questions
   - Chat history management

## 🤝 Support and Contribution

### Getting Help
- Visit [Official Prison Visit Information](https://www.gov.uk/prison-visits)
- Raise an issue in the GitHub repository

### Contributing
We welcome contributions! Areas where you can help:
- Enhanced information retrieval
- Additional policy document support
- Interface improvements
- Documentation updates

## 📖 Documentation

### Configuration
The application uses environment variables for configuration:
- Required API keys and URLs are set in `.env`
- Configuration is validated on startup
- Error messages guide you if any required variables are missing

### Usage Examples
Common queries the assistant can help with:
```plaintext
Q: "What ID do I need to visit a prison?"
Q: "What is the dress code for prison visitors?"
Q: "What items am I not allowed to bring?"
Q: "How long can I visit for?"
```

## 📝 License
MIT License - Free to use, modify, and distribute

## 🙏 Acknowledgments
- Built on advanced AI models from Cohere
- Powered by Qdrant vector database
- Uses official gov.uk sources
- Interface built with Streamlit
