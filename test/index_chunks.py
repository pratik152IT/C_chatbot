import ollama
import chromadb
from chunker import chunk_c_file

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("c_codebase")

def index_file(filepath):
    chunks = chunk_c_file(filepath)
    for i, chunk in enumerate(chunks):
        embedding = ollama.embeddings(model="nomic-embed-text", prompt=chunk["text"])["embedding"]
        collection.add(
            ids=[f"{filepath}::{i}"],
            embeddings=[embedding],
            documents=[chunk["text"]],
            metadatas=[{"file": chunk["file"], "type": chunk["type"],
                        "start_line": chunk["start_line"], "end_line": chunk["end_line"]}],
        )
    print(f"Indexed {len(chunks)} chunks from {filepath}")

if __name__ == "__main__":
    index_file("sample1.c")
    index_file("sample2.c")
    print("Total chunks in DB:", collection.count())