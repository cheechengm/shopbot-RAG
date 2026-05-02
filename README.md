# 🛍️ ShopBot — E-commerce RAG Chatbot

**ShopBot** is a Retrieval-Augmented Generation (RAG) platform that transforms static store documents into an interactive AI support agent. It enables store owners to upload policies and FAQs, providing customers with instant, accurate responses grounded strictly in the shop’s verified data.

---

## 📝 Resume Summary 
> **AI-Powered E-commerce Chatbot (RAG System)**
> Engineered a full-stack RAG platform that enables businesses to deploy domain-specific AI assistants. Built a document processing pipeline to vectorize unstructured data (PDF/DOCX) into MongoDB Atlas, ensuring grounded and accurate LLM responses. Implemented secure role-based interfaces using **Jinja2** to isolate administrative document management from public customer chat.
>
> **Core Tech:** Python, Flask, Llama 3, MongoDB Atlas, RAG, Semantic Search.

---

## 🏗️ Technical Highlights

* **RAG Architecture:** Developed a retrieval-augmented generation flow using **Llama 3** to ground AI responses in uploaded store documents, ensuring high factual accuracy and minimizing hallucinations.
* **Vector Search & Persistence:** Integrated **MongoDB Atlas Vector Search** to store and retrieve document embeddings, enabling millisecond-latency semantic search across private datasets.
* **Secure Role Separation:** Leveraged **Jinja2** conditional rendering to create a secure, "stealth-mode" admin dashboard for document management, allowing for administrative control without a complex authentication database.
* **Automated Ingestion:** Built a robust data pipeline that chunks and vectorizes PDFs, DOCX, and TXT files using a sliding-window strategy to preserve semantic context.

---

## 🛠️ Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Backend** | Python (Flask), REST APIs |
| **AI / ML** | Llama 3 (Ollama), Semantic Search, RAG |
| **Database** | MongoDB Atlas Vector Search, ChromaDB |
| **Frontend** | Jinja2, Vanilla JavaScript, CSS3 |

---

## 📁 Key Features

* **Verified Responses:** Every answer is derived from the uploaded shop documentation, ensuring customers receive accurate information.
* **Multi-Format Support:** Ingests unstructured data from PDF, Word, and Text files seamlessly.
* **Admin Dashboard:** A dedicated interface for shop owners to manage their knowledge base and clear existing data. (Normal customer will not be able to see)
* **Real-Time Processing Progress:** A dynamic loading bar that provides instant feedback during document ingestion, showing the exact percentage of chunks processed and embedded.
* **Smart Semantic Search:** Powered by MongoDB Atlas Vector Search and Ollama, the bot understands the meaning behind customer questions rather than just matching keywords.
* **Persistent Memory:** Documentation remains securely stored in the cloud (MongoDB Atlas), meaning the bot is ready to answer questions 24/7 without needing to re-upload files after a restart.
* **Clutter-Free Chat Management:** Users can reset their conversation at any time with a "Clear Chat" feature, instantly wiping the history to start a fresh session and maintain an organized interface.

## Image of the interface for admin dashboard
<img width="2859" height="1452" alt="image" src="https://github.com/user-attachments/assets/8e721ff5-ffcf-4c65-b8a0-68eef47add36" />

The image demonstrates the ingestion of a Shopee Refund and Return Policy PDF. Once vectorized and stored in MongoDB Atlas Vector Search, this persistent data(MongoDB) allows the AI to generate highly accurate responses with direct citations from the source documentation. When ingesting the document it also includes a progress bar so admin can keep track of the progress.


## Image of the customer interface 
<img width="2859" height="1424" alt="image" src="https://github.com/user-attachments/assets/275a5df6-c1b0-4e12-94fe-072bf9e9cc5b" />

## ⚙️ How the Ingestion Pipeline Works
The process converts static documents into "searchable brains" for the AI through several coordinated steps:

Document Parsing: The system extracts raw text from PDF, DOCX, or TXT files, handling complex layouts like the Shopee policy you ingested.

Recursive Chunking: To stay within the AI's "context window," the text is broken into smaller, overlapping passages (chunks).

Vector Embedding: Each chunk is sent to Ollama (Llama 3), which converts human language into a high-dimensional mathematical vector representing its meaning.

Persistent Storage: These vectors are saved in MongoDB Atlas. Unlike a standard database, this allows for "nearest neighbor" searches, finding content based on intent rather than just keywords.

Live Feedback: During this loop, the system sends real-time updates to the Admin Progress Bar, ensuring the user knows exactly how much data has been successfully vectorized.

