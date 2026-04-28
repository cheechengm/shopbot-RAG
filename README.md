# 🛍️ ShopBot — E-commerce RAG Chatbot

**ShopBot** is a Retrieval-Augmented Generation (RAG) platform that transforms static store documents into an interactive AI support agent. It enables store owners to upload policies and FAQs, providing customers with instant, accurate responses grounded strictly in the shop’s verified data.

---

## 📝 Resume Summary (TL;DR)
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
* **Admin Dashboard:** A dedicated interface for shop owners to manage their knowledge base and clear existing data.

<img width="2869" height="1474" alt="image" src="https://github.com/user-attachments/assets/35464491-c6f6-48c7-a02d-9d642bd9dc8c" />
