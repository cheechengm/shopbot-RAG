# 🛍️ ShopBot — E-commerce RAG Chatbot

An AI-powered customer support chatbot that answers questions based on **your own store documents** (PDFs, Word docs, text files). Built with Python, Flask, LangChain-style RAG pipeline, ChromaDB, and the Claude API.

---

## 🏗️ Architecture

```
Customer Question
       │
       ▼
  Flask API (app.py)
       │
       ▼
  RAG Engine (rag_engine.py)
  ┌────────────────────────────────┐
  │  1. Embed question             │
  Here is the raw Markdown code for your updated README.md. You can copy and paste this directly into your file:

Markdown
# 🛍️ ShopBot — E-commerce RAG Chatbot

An AI-powered customer support chatbot that answers questions based on **your own store documents**. This project features a hybrid architecture using a local LLM for cost-efficiency and **MongoDB Atlas Vector Search** for cloud-based persistence.

---

## 🏗️ Architecture

Customer Question                 🔒 Private Admin Link
│                             │
▼                             ▼
Flask API (app.py) ◄────────────────────── Document Uploads
│
▼
RAG Engine (rag_engine.py)
┌────────────────────────────────┐
│  1. Embed question (Ollama)    │
│  2. Vector Search (Cloud)      │◄── ☁️ MongoDB Atlas (Cloud DB)
│  3. Contextual Reranking       │
│  4. Generate Answer (Llama 3)  │
└────────────────────────────────┘
│
▼
Answer + Source Citations


---

## ⚙️ Setup Instructions

### 1. MongoDB Atlas Setup (Cloud Database)
1. Create a free cluster at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas).
2. Create a **Vector Search Index** on your collection named `default`.
3. Use the following JSON configuration for the index:
```json
{
  "fields": [{
    "numDimensions": 4096,
    "path": "embedding",
    "similarity": "cosine",
    "type": "vector"
  }]
}
2. Local LLM (Ollama)
Download Ollama and pull the model:

Bash
ollama pull llama3
ollama serve
3. Project Configuration
Create a .env file in the root directory and add your connection string:

Bash
MONGO_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net/shopbot_db
4. Install & Run
Bash
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the application
python app.py
🚀 Role-Based Access (Stealth Mode)
This app separates the Customer and Admin interfaces without requiring a complex login database:

Customer View: http://localhost:5000

Standard chat interface.

Upload buttons and document lists are hidden via Jinja2 conditional rendering.

Admin View: http://localhost:5000/manage-shop-admin-99

Reveals the Knowledge Base management sidebar.

Allows the owner to upload PDFs/Docs and clear the cloud database.

API endpoints are protected via request.referrer validation.
       │
       ▼
  Answer + Source Citations
```

**Data Ingestion (one-time per document):**
```
PDF / DOCX / TXT
      │
  Text Extraction (PyPDF2 / python-docx)
      │
  Chunking (500 chars, 80 overlap)
      │
  Stored in ChromaDB
```

---

## ⚙️ Setup Instructions (100% Free)

### 1. Install Ollama (the free local LLM runner)
Download from https://ollama.com and install it.

Then pull the Llama 3 model (one-time download, ~4.7GB):
```bash
ollama pull llama3
```

Start Ollama (it runs in the background):
```bash
ollama serve
```

### 2. Clone & navigate to project
```bash
git clone <your-repo-url>
cd rag-chatbot
```

### 3. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the app
```bash
python app.py
```

Open your browser at **http://localhost:5000** — no API key needed! 🎉

### Optional: Use a different model
```bash
# Smaller/faster (good for low-RAM machines)
ollama pull llama3:8b
OLLAMA_MODEL=llama3:8b python app.py

# More powerful
ollama pull mistral
OLLAMA_MODEL=mistral python app.py
```

---

## 🚀 How to Use

1. **Load sample data** — click "Load Sample Store Data" to see it work instantly
2. **Upload your own documents** — drag & drop PDFs, Word docs, or text files
3. **Ask questions** — type natural language questions about your products, policies, etc.

---

## 📁 Project Structure

```
rag-chatbot/
├── app.py                      # Flask API routes
├── rag_engine.py               # Core RAG pipeline
├── requirements.txt
├── data_samples/
│   └── sample_store_data.txt   # Demo store FAQ data
├── uploads/                    # Uploaded files (auto-created)
├── vectorstore/                # ChromaDB persisted storage
├── templates/
│   └── index.html              # Chat UI
└── static/
    ├── css/style.css
    └── js/chat.js
```

---

## 🔧 Customization

### Change the chatbot persona
Edit the `system_prompt` in `rag_engine.py` → `_generate_answer()`:
```python
system_prompt = """You are a helpful assistant for [YOUR STORE NAME]..."""
```

### Adjust chunk size
In `rag_engine.py`:
```python
CHUNK_SIZE = 500    # increase for longer passages
CHUNK_OVERLAP = 80  # increase for more context continuity
TOP_K = 4           # number of passages to retrieve
```

### Use a different LLM
Replace the Anthropic client in `rag_engine.py` with OpenAI:
```python
from openai import OpenAI
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
response = client.chat.completions.create(model="gpt-4o", messages=messages)
answer = response.choices[0].message.content
```

---

## 🌐 Deployment (Free)

### Deploy to Render.com
1. Push code to GitHub
2. Create new **Web Service** on render.com
3. Set environment variable: `ANTHROPIC_API_KEY`
4. Build command: `pip install -r requirements.txt`
5. Start command: `gunicorn app:app`

### Deploy to Railway
```bash
railway login
railway new
railway up
railway variables set ANTHROPIC_API_KEY=your-key
```

---

## 📝 Resume Description

> **AI-Powered E-commerce Chatbot (RAG System)**
> Built a production-style retrieval-augmented generation (RAG) chatbot using Python, Flask, and the Anthropic Claude API. The system ingests PDF and Word documents, chunks and stores text as embeddings in ChromaDB, and retrieves semantically relevant passages to ground LLM responses. Implemented real-time chat UI with conversation memory, source citations, and document management. Deployed to cloud with persistent vector storage.
>
> **Tech:** Python · Flask · ChromaDB · Anthropic Claude API · RAG · NLP · REST API · HTML/CSS/JS

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.10+, Flask |
| LLM | Ollama + Llama 3 (free, runs locally) |
| Vector Store | ChromaDB (local persistent) |
| PDF Parsing | PyPDF2 |
| DOCX Parsing | python-docx |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Deployment | Render / Railway |

---

## 📄 License

MIT — free to use for personal and commercial projects.
