# 🤖 C-Copilot: Local RAG Assistant for C Codebases

A lightweight, local Retrieval-Augmented Generation (RAG) assistant that indexes C source files into ChromaDB and uses local Ollama models to analyze, explain, and debug C code (memory leaks, buffer overflows, pointer issues, macro bugs).

---

## 🏗 Project Architecture

```text
C_chatbot/
├── app/
│   ├── chat_app.py           # Streamlit conversational interface
│   └── dashboard.py          # LLM evaluation and benchmarking dashboard
├── data/
│   ├── CJSON/                # Target C library codebase for indexing
│   ├── chroma_db/            # Persistent ChromaDB vector database 
│   ├── sample1.c             # Sample C source test file
│   ├── sample2.c             # Sample C source test file
│   ├── sample3.c             # Sample C source test file
│   
├── src/
│   ├── __init__.py
│   ├── chunker.py            # code chunking using tree-sitter
│   ├── structure_extractor.py# C function & structure extractor
│   ├── index_chunks.py       # Embedding generation & indexing in ChromaDB
│   └── ragpipline.py         # Context retrieval & prompt generation 
├── test_new/
│   ├── eval_models.py       
│   ├── explore_ast.py        
│   ├── model_eval.py         
│   ├── test_embed.py         
│   ├── test_explain.py       
│   ├── test_ollama.py        
│   └── test_retrieval.py     
├── .gitignore
├── requirements.txt          # Project dependencies
└── README.md
```

---

## 📌 What It Does

* **Codebase Indexing:** Extracts functions and structures from C files in `data/` and stores embeddings locally in ChromaDB using `nomic-embed-text`.
* **Context-Aware Assistance:** Retrieves relevant C code snippets to answer questions, find bugs, and explain memory/pointer behavior using `qwen2.5-coder`.

---

## 🚀 How to Run

### 1. Requirements & Ollama Setup

Ensure Ollama is installed and pull the required models:

```bash
ollama pull nomic-embed-text
ollama pull qwen2.5-coder:3b
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

### 2. Index the C Codebase

Build or update the ChromaDB vector database from files in `data/`:

```bash
python -m src.index_chunks
```

### 3. Run Streamlit UI

Launch the web app interface:

```bash
streamlit run app/chat_app.py
```
