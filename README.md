# RAG-System# AI RAG System

A production-oriented Retrieval-Augmented Generation (RAG) system built with **Python, Flask, LangChain, FAISS, Hugging Face Embeddings, and Groq LLMs**.

The system allows users to upload a PDF document through a web interface, automatically process the document, convert it into Markdown, split the content into chunks, generate embeddings, store them in a FAISS vector database, and ask questions about the uploaded document using an LLM.

## 🚀 Features

- PDF document upload through a web interface
- Automatic PDF → Markdown conversion
- Text chunking for efficient retrieval
- Hugging Face sentence embeddings
- FAISS vector database
- Semantic document retrieval
- Groq-powered LLM responses
- RAG-based question answering
- Flask REST API
- Simple web frontend
- Environment-variable based API key management
- Automatic replacement of the previous document and vector database

## 🧠 How the RAG System Works

The system follows this pipeline:

```text
User uploads PDF
        ↓
PDF → Markdown
        ↓
Text Loading
        ↓
Text Splitting
        ↓
Embeddings
        ↓
FAISS Vector Database
        ↓
User Question
        ↓
Question Processing
        ↓
Similarity Retrieval
        ↓
Relevant Document Chunks
        ↓
Groq LLM
        ↓
Generated Answer
```

Instead of sending the entire document to the LLM, the system retrieves the most relevant document chunks and provides them as context for generating the answer.

## 🏗️ Project Structure

```text
RAG-System/
│
├── app.py
├── build_database.py
├── requirements.txt
│
├── config/
│   └── config.py
│
├── rag/
│   ├── chains.py
│   ├── embeddings.py
│   ├── loader.py
│   ├── pdf_to_markdown.py
│   ├── pipeline.py
│   ├── prompts.py
│   ├── retriever.py
│   ├── splitter.py
│   ├── vectorstore.py
│   └── test.py
│
├── routes/
│   └── rag_routes.py
│
├── services/
│   └── rag_service.py
│
├── static/
│   ├── script.js
│   └── style.css
│
├── templates/
│   └── index.html
│
├── test_api.py
├── test_conversion.py
├── test_rag.py
└── .gitignore
```

## 🛠️ Technologies

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Flask | Web application and API |
| LangChain | RAG pipeline and LLM integration |
| FAISS | Vector similarity search |
| Hugging Face | Text embeddings |
| Groq | Large Language Model inference |
| PyMuPDF | PDF text extraction |
| python-dotenv | Environment variable management |
| HTML / CSS / JavaScript | Frontend |

## ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/adham3zaam/RAG-System.git
```

Move into the project directory:

```bash
cd RAG-System
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment on Windows:

```powershell
venv\Scripts\activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

## 🔐 Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
EMBEDDING_MODEL=your_embedding_model
LLM_MODEL=your_llm_model
```

Never upload the `.env` file to GitHub.

The project already includes `.env` in `.gitignore`.

## ▶️ Run the Application

Start the Flask application:

```bash
python app.py
```

The application will run locally.

Open the local address shown by Flask in your browser.

## 📄 Using the System

### 1. Upload a PDF

Use the web interface to upload a PDF document.

### 2. Automatic Processing

The system:

1. Saves the uploaded PDF.
2. Converts the PDF into Markdown.
3. Loads the Markdown document.
4. Splits the document into chunks.
5. Generates embeddings.
6. Creates a FAISS vector database.

### 3. Ask Questions

After processing the document, ask questions through the web interface.

The RAG pipeline retrieves the most relevant chunks and sends them as context to the Groq LLM.

## 🔌 API

The application provides endpoints for document upload and question answering.

### Upload PDF

```http
POST /upload
```

Upload a PDF file using the request's file field.

### Ask a Question

```http
POST /ask
```

Send a question to the RAG system and receive the generated answer.

## 🔒 Security

Sensitive information is stored using environment variables.

The following files and directories are excluded from Git:

```text
.env
venv/
data/
vector_db/
__pycache__/
```

This prevents API keys, uploaded documents, generated vector databases, and Python cache files from being committed to the repository.

## 🧪 Testing

The repository includes test files for:

- API functionality
- PDF → Markdown conversion
- RAG functionality

Example:

```bash
python test_conversion.py
```

## 🔮 Future Improvements

- Support for multiple documents
- Persistent document management
- Better conversation memory
- Streaming LLM responses
- Authentication and user accounts
- Cloud deployment
- Docker support
- Advanced document metadata filtering
- Improved frontend UI
- Multi-format document support
- Production monitoring

## 👨‍💻 Author

**Adham Azzam**

Machine Learning & Deep Learning Engineer

GitHub: [adham3zaam](https://github.com/adham3zaam)

## ⭐ Project

If you find this project useful, feel free to star the repository.