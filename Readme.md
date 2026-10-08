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
│   ├── sample1.c             # Sample C source test file
│   ├── sample2.c             # Sample C source test file
│   ├── sample3.c             # Sample C source test file
│   
├── src/
│   ├── __init__.py
│   ├── chunker.py            #code chunking using tree-sitter
│   ├── structure_extractor.py# C function & structure  extractor
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

## ⚡ Features

- **AST-Aware Code Chunking:** Uses `tree-sitter-c` to chunk code logically at function and struct boundaries instead of arbitrary character limits.
- **100% Local Processing:** Uses local embedding models (`nomic-embed-text`) and LLMs (`qwen2.5-coder:7b`) via Ollama with zero external API calls.
- **Signature Compression:** Extracts concise C function declarations and struct definitions to minimize context window usage.
- **Automated Compiler Feedback Loop:** Evaluates generated C code using `gcc -Wall -Wextra` to count warnings and execution correctness.
- **Interactive Dashboards:** Streamlit UI for both real-time code QA and comparative model evaluation analytics.

---

## 🚀 Getting Started

### Prerequisites

1. **Python 3.10+**
2. **GCC Compiler:** Ensure GCC is installed and added to system PATH (e.g., via MinGW/MSYS2 on Windows).
3. **Ollama:** Installed and running locally (`http://localhost:11434`).

Pull required local models:
```bash
ollama pull nomic-embed-text
ollama pull qwen2.5-coder:7b
```

### Installation

1. Clone the repository:
```bash
git clone [https://github.com/pratik152IT/C_chatbot.git](https://github.com/pratik152IT/C_chatbot.git)
cd C_chatbot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

---

## 💻 Usage

### 1. Index Codebase
Extract chunks from C source files in `data/` and build the persistent vector database:
```bash
python -m src.index_chunks
```

### 2. Run Interactive Chatbot
Launch the Streamlit web interface:
```bash
python -m streamlit run app/chat_app.py
```

### 3. Run Performance Analytics Dashboard
View comparative benchmarks across tested local models:
```bash
python -m streamlit run app/dashboard.py
```

### 4. Run Benchmark Test Suite
Evaluate local models against code generation, debugging, explanation, and QA tasks:
```bash
python -m test_new.eval_models
```
