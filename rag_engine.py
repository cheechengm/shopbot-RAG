import os
import re
import requests
from typing import List, Dict, Any
import os
from dotenv import load_dotenv
from pymongo import MongoClient

# This looks for a file named .env in the same folder and 
# loads the variables into your system's environment.
load_dotenv() 

# Now this will actually work!
mongo_uri = os.getenv("MONGO_URI")

# ── Ollama config ──────────────────────────────────
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3")

# Optional: for PDF and DOCX parsing
try:
    import PyPDF2
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

try:
    from docx import Document as DocxDocument
    DOCX_SUPPORT = True
except ImportError:
    DOCX_SUPPORT = False

try:
    import chromadb
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False


# ─────────────────────────────────────────────
# Simple in-memory vector store fallback
# ─────────────────────────────────────────────
class SimpleVectorStore:
    """
    A basic TF-IDF-style vector store that works without any external DB.
    Used as fallback if ChromaDB is not installed.
    """

    def __init__(self):
        self.chunks: List[Dict] = []

    def add(self, text: str, metadata: Dict):
        self.chunks.append({"text": text, "metadata": metadata})

    def search(self, query: str, top_k: int = 4) -> List[Dict]:
        if not self.chunks:
            return []
        query_words = set(re.findall(r"\w+", query.lower()))
        scored = []
        for chunk in self.chunks:
            chunk_words = set(re.findall(r"\w+", chunk["text"].lower()))
            overlap = len(query_words & chunk_words)
            score = overlap / (len(query_words) + 1)
            scored.append((score, chunk))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [c for _, c in scored[:top_k] if _ > 0]

    def list_sources(self) -> List[str]:
        seen = set()
        return [
            c["metadata"]["source"]
            for c in self.chunks
            if c["metadata"]["source"] not in seen and not seen.add(c["metadata"]["source"])
        ]

    def clear(self):
        self.chunks = []

    def count(self) -> int:
        return len(self.chunks)


# ─────────────────────────────────────────────
# ChromaDB-backed vector store (preferred)
# ─────────────────────────────────────────────
class MongoVectorStore:
    def __init__(self):
        uri = os.getenv("MONGO_URI")
        # DEBUG PRINT: This will show up in your terminal
        if not uri:
            print("❌ ERROR: MONGO_URI not found in environment variables!")
        else:
            print(f"✅ MONGO_URI found! Connecting to Atlas...")
        self.client = MongoClient(uri)
        # Match the Database and Collection names you just created in Atlas
        self.db = self.client["shopbot_db"]
        self.collection = self.db["rag_collection"]
        self.ollama_emb_url = "http://localhost:11434/api/embeddings"

    def _get_embedding(self, text):
        response = requests.post(
            self.ollama_emb_url, 
            json={"model": "llama3", "prompt": text}
        )
        return response.json()["embedding"]

    def add(self, text, metadata):
        embedding = self._get_embedding(text)
        self.collection.insert_one({
            "text": text,
            "metadata": metadata,
            "embedding": embedding
        })

    def search(self, query: str, top_k: int = 4) -> List[Dict]:
        query_vector = self._get_embedding(query)
        print(f"DEBUG: Generated embedding of length {len(query_vector)}") 
        
        pipeline = [
            {
                "$vectorSearch": {
                    "index": "vector_index", 
                    "path": "embedding",
                    "queryVector": query_vector,
                    "numCandidates": 100,
                    "limit": top_k
                }
            },
            {
                "$project": {
                    "text": 1,
                    "metadata": 1, # Ensure metadata is included!
                    "score": {"$meta": "vectorSearchScore"}
                }
            }
        ]
        
        results = list(self.collection.aggregate(pipeline))
        # Return the full document (as a dict) so the engine can read metadata
        print(f"DEBUG: Raw search results from Mongo: {results}") # IS THIS EMPTY?
        return results

    def list_sources(self) -> List[str]:
        """Fetches unique filenames from the cloud so the sidebar stays populated."""
        try:
            # We use distinct on the metadata.source field
            return self.collection.distinct("metadata.source")
        except Exception as e:
            print(f"❌ MongoDB error in list_sources: {e}")
            return []

    def count(self) -> int:
        """Required for the RAG Engine to know if data exists."""
        return self.collection.count_documents({})

    def clear(self):
        self.collection.delete_many({})
# ─────────────────────────────────────────────
# RAG Engine
# ─────────────────────────────────────────────
class RAGEngine:
    CHUNK_SIZE = 500       # characters per chunk
    CHUNK_OVERLAP = 80     # overlap between chunks
    TOP_K = 4              # passages to retrieve

    def __init__(self):
        # Use ChromaDB if available, else fall back to simple store
        self.store = MongoVectorStore()     # <-- Use this
        print("✅ Connected to MongoDB Atlas Vector Store")
        self.ingested_files: List[str] = []
        self._check_ollama()

    # ── Document ingestion ──────────────────────────────────────

    def ingest_document(self, filepath: str, display_name: str, progress_tracker: dict = None) -> int:
        print(f"\n--- STARTING INGESTION for: {display_name} ---")

        # Check if this file is already in MongoDB
        existing_count = self.store.collection.count_documents({"metadata.source": display_name})
        if existing_count > 0:
            print(f"✅ {display_name} already exists in Atlas ({existing_count} chunks). Skipping re-upload.")
            if progress_tracker is not None:
                progress_tracker["progress"] = 100
                progress_tracker["status"] = "File already exists. Ready!"
            return existing_count

        # STEP 1: Extraction
        text = self._extract_text(filepath)
        if len(text) == 0:
            print("❌ ERROR: No text was extracted!")
            if progress_tracker: progress_tracker["status"] = "Error: No text found"
            return 0

        # STEP 2: Chunking
        chunks = self._chunk_text(text)
        total_chunks = len(chunks)
        if total_chunks == 0:
            print("❌ ERROR: 0 chunks created.")
            return 0

        # STEP 3: Adding to Store
        print(f"DEBUG 3: Processing {total_chunks} chunks...")
        try:
            for i, chunk in enumerate(chunks):
                # Calculate percentage
                percent = int(((i + 1) / total_chunks) * 100)
                
                # Update progress tracker for the frontend
                if progress_tracker is not None:
                    progress_tracker["progress"] = percent
                    progress_tracker["status"] = f"Embedding chunk {i+1} of {total_chunks}..."

                # Console log every 10 chunks
                if i % 10 == 0:
                    print(f"Progress: {i}/{total_chunks} chunks processed...")

                # The actual heavy lifting (Ollama embedding + Mongo upload)
                self.store.add(chunk, {"source": display_name, "chunk_index": i})
                
            print("DEBUG 4: Loop finished successfully.")
        except Exception as e:
            print(f"❌ ERROR during store.add: {str(e)}")
            if progress_tracker: progress_tracker["status"] = "Error during embedding"
            raise e

        # STEP 4: Final Verification
        final_count = self.store.count()
        print(f"DEBUG 5: Final Verification - Store now says it has {final_count} chunks.")
        
        return total_chunks
    def _extract_text(self, filepath: str) -> str:
        ext = filepath.rsplit(".", 1)[-1].lower()

        if ext == "txt":
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()

        if ext == "pdf":
            if not PDF_SUPPORT:
                raise ImportError("PyPDF2 not installed. Run: pip install PyPDF2")
            text = []
            with open(filepath, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text.append(page.extract_text() or "")
            return "\n".join(text)

        if ext == "docx":
            if not DOCX_SUPPORT:
                raise ImportError("python-docx not installed. Run: pip install python-docx")
            doc = DocxDocument(filepath)
            return "\n".join(p.text for p in doc.paragraphs)

        raise ValueError(f"Unsupported file type: {ext}")

    def _chunk_text(self, text: str) -> List[str]:
        text = re.sub(r"\n{3,}", "\n\n", text).strip()
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.CHUNK_SIZE
            chunk = text[start:end]
            
            if end < len(text):
                # Find the last sentence or line break
                last_period = chunk.rfind(". ")
                last_newline = chunk.rfind("\n")
                break_point = max(last_period, last_newline)
                
                # Only break if we found a separator in the second half of the chunk
                if break_point > self.CHUNK_SIZE // 2:
                    chunk = chunk[:break_point + 1]
            
            chunks.append(chunk.strip())
            # Move the pointer, ensuring we actually move forward to avoid infinite loops
            move_forward = len(chunk) - self.CHUNK_OVERLAP
            start += max(move_forward, 1)
        
        return [c for c in chunks if len(c) > 20] # Lowered from 40 for testing
    # ── Query + Generation ──────────────────────────────────────

    def query(self, user_message: str, history: List[Dict] = None) -> Dict[str, Any]:
        print(f"DEBUG: Checking store... total chunks available: {self.store.count()}")
        retrieved = self.store.search(user_message, top_k=self.TOP_K)

        if not retrieved:
            return {
                "answer": "I don't have any documents loaded yet. Please upload your store's FAQ or policy documents first, or click **'Load Sample Data'** to try a demo.",
                "sources": [],
                "has_context": False,
            }

        context_text = self._build_context(retrieved)
        answer = self._generate_answer(user_message, context_text, history or [])
        sources = list({c["metadata"]["source"] for c in retrieved})

        return {
            "answer": answer,
            "sources": sources,
            "has_context": True,
            "passages_used": len(retrieved),
        }

    def _build_context(self, chunks: List[Dict]) -> str:
        parts = []
        for i, chunk in enumerate(chunks, 1):
            source = chunk["metadata"].get("source", "document")
            parts.append(f"[Passage {i} — from '{source}']\n{chunk['text']}")
        return "\n\n---\n\n".join(parts)

    def _check_ollama(self):
        try:
            r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
            models = [m["name"] for m in r.json().get("models", [])]
            matched = next((m for m in models if OLLAMA_MODEL in m), None)
            if matched:
                print(f"✅ Ollama running — using model: {matched}")
            else:
                print(f"⚠️  Ollama is running but model '{OLLAMA_MODEL}' not found.")
                print(f"   Run: ollama pull {OLLAMA_MODEL}")
        except Exception:
            print("⚠️  Ollama not reachable. Make sure it's running: https://ollama.com")

    def _generate_answer(self, question: str, context: str, history: List[Dict]) -> str:
        system_prompt = (
            "You are a friendly and helpful customer support assistant for an e-commerce store.\n"
            "Answer questions using ONLY the context passages provided. "
            "If the answer is not in the context, say you don't have that information. "
            "Never make up prices, policies, or product details. Be concise and warm."
        )

        # Build conversation history string (Ollama /api/chat supports messages array)
        messages = [{"role": "system", "content": system_prompt}]
        for turn in history[-6:]:
            messages.append({"role": turn["role"], "content": turn["content"]})

        user_content = (
            f"Context from our store documents:\n\n{context}\n\n---\n\nCustomer question: {question}"
        )
        messages.append({"role": "user", "content": user_content})

        try:
            response = requests.post(
                f"{OLLAMA_URL}/api/chat",
                json={"model": OLLAMA_MODEL, "messages": messages, "stream": False},
                timeout=120,
            )
            response.raise_for_status()
            return response.json()["message"]["content"]
        except requests.exceptions.ConnectionError:
            return (
                "⚠️ Could not connect to Ollama. "
                "Make sure it's running (`ollama serve`) and the model is pulled (`ollama pull llama3`)."
            )
        except Exception as e:
            return f"⚠️ Error generating answer: {str(e)}"

    # ── Utility ────────────────────────────────────────────────

    def list_documents(self) -> List[str]:
        return self.store.list_sources()

    def clear_all(self):
        self.store.clear()
        self.ingested_files = []
        # Clean up uploads folder
        for f in os.listdir("uploads"):
            try:
                os.remove(os.path.join("uploads", f))
            except Exception:
                pass
