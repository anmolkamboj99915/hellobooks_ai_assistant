# Hellobooks AI Assistant

## Overview

Hellobooks AI Assistant is a **Retrieval-Augmented Generation (RAG) based AI system** that answers bookkeeping and accounting-related questions.

The assistant retrieves relevant documents from a small accounting knowledge base and uses a Large Language Model (LLM) to generate accurate responses.

This project was built as part of a **Python + Generative AI internship assignment**.

---

# Features

- Retrieval-Augmented Generation (RAG) architecture
- Semantic document search using **FAISS**
- Embeddings generated using **SentenceTransformers**
- LLM integration with **OpenAI / Mistral / Local TinyLlama fallback**
- Modular Python architecture
- CLI-based AI assistant
- Docker support for deployment
- Small accounting knowledge base

---

# Project Architecture

```
hellobooks-ai-assistant
│
├── app
│   ├── config.py
│   ├── embedder.py
│   ├── retriever.py
│   ├── rag_pipeline.py
│   ├── llm.py
│   └── main.py
│
├── scripts
│   └── build_index.py
│
├── knowledge_base
│   ├── bookkeeping.md
│   ├── invoices.md
│   ├── profit_loss.md
│   ├── balance_sheet.md
│   └── cash_flow.md
│
├── vector_store
│   ├── faiss_index.bin
│   └── documents.pkl
│
├── Dockerfile
├── requirements.txt
└── README.md
```

---

# How the System Works

The system follows a **Retrieval-Augmented Generation pipeline**.

```
User Question
      ↓
Generate Question Embedding
      ↓
FAISS Vector Search
      ↓
Retrieve Relevant Documents
      ↓
Send Context to LLM
      ↓
Generate Answer
```

This approach improves accuracy by grounding responses in the knowledge base.

---

# Knowledge Base

The assistant uses a small accounting dataset containing documents about:

- Bookkeeping
- Invoices
- Profit & Loss
- Balance Sheet
- Cash Flow

Documents are stored in the **knowledge_base/** directory as markdown files.

---

# Installation

## 1. Clone the Repository

```
git clone https://github.com/YOUR_USERNAME/hellobooks-ai-assistant.git
cd hellobooks-ai-assistant
```

---

## 2. Create Virtual Environment

Windows:

```
python -m venv .venv
.venv\Scripts\activate
```

Linux / Mac:

```
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3. Install Dependencies

```
pip install -r requirements.txt
```

---

# Environment Variables

Create a `.env` file in the project root.

Example:

```
OPENAI_API_KEY=your_openai_api_key_here
MISTRAL_API_KEY=your_mistral_api_key_here
```

If no API key is provided, the system automatically falls back to a **local TinyLlama model**.

---

# Build the Vector Database

Before running the assistant, generate the FAISS index.

```
python scripts/build_index.py
```

This will:

- load documents
- generate embeddings
- create FAISS vector index
- store metadata

Output will be saved in:

```
vector_store/
```

---

# Run the AI Assistant

Start the command-line assistant:

```
python -m app.main
```

Example session:

```
Hellobooks AI Assistant
Type your accounting question or type 'exit' to quit.

Question: What is bookkeeping?

Answer:
Bookkeeping is the process of recording financial transactions of a business...
```

---

# Docker Usage

You can also run the project using Docker.

## Build Docker Image

```
docker build -t hellobooks-ai-assistant .
```

## Run Container

```
docker run -it hellobooks-ai-assistant
```

---

# Technologies Used

- Python
- SentenceTransformers
- FAISS (Vector Database)
- OpenAI API
- Mistral API
- HuggingFace Transformers
- Docker

---

# Example Questions

You can ask questions such as:

- What is bookkeeping?
- What is a balance sheet?
- What is an invoice?
- What does a profit and loss statement show?
- What is cash flow?

---

# Future Improvements

Possible enhancements include:

- Web interface using FastAPI or Streamlit
- Larger knowledge base
- Improved chunking and document indexing
- Advanced retrieval strategies
- Conversation memory support

---

# Author

Anmol Jaiya

---

# License

This project is for educational and internship evaluation purposes.
