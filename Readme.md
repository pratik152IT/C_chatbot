# 🤖 C-Copilot: Local RAG Assistant for C Codebases

C-Copilot is a privacy-first, locally-hosted Retrieval-Augmented Generation (RAG) assistant designed to analyze, explain, debug, and write C code based on custom project source files. It leverages Tree-Sitter AST parsing, ChromaDB vector search, and local LLMs via Ollama.

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
│   ├── sample1-3.c           # Sample C source test files
│   └── eval_c_results.csv    # Benchmark performance metrics
├── src/
│   ├── __init__.py
│   ├── chunker.py            # AST-based code chunking using tree-sitter-c
│   ├── structure_extractor.py# C function & struct signature extractor
│   ├── index_chunks.py       # Embedding generation & ChromaDB indexing
│   └── ragpipline.py         # Context retrieval & prompt augmentation
├── test_new/
│   ├── eval_models.py        # Automated GCC compilation & evaluation suite
│   ├── model_eval.py         # DeepEval accuracy & readability suite
│   └── test_retrieval.py     # Vector similarity retrieval tests
├── .gitignore
├── requirements.txt          # Project dependencies
└── README.md
