import os
import chromadb
import ollama
from src.chunker import chunk_c_file

# Save ChromaDB persistent storage inside data/
client = chromadb.PersistentClient(path="data/chroma_db")
collection = client.get_or_create_collection("c_codebase")

# Subfolders inside CJSON to skip while walking the directory tree
SKIP_FOLDERS = {"tests", "unity", "fuzzing"}


def index_file(filepath):
  chunks = chunk_c_file(filepath)
  for i, chunk in enumerate(chunks):
    embedding = ollama.embeddings(
        model="nomic-embed-text", prompt=chunk["text"]
    )["embedding"]
    collection.upsert(
        ids=[f"{filepath}::{i}"],
        embeddings=[embedding],
        documents=[chunk["text"]],
        metadatas=[{
            "file": chunk["file"],
            "type": chunk["type"],
            "start_line": chunk["start_line"],
            "end_line": chunk["end_line"],
        }],
    )
  print(f"Indexed {len(chunks)} chunks from {filepath}")


def index_folder(folder_path):
  """Recursively find .c files in folder_path, skipping SKIP_FOLDERS, and index them."""
  c_files = []
  for root, dirs, files in os.walk(folder_path):
    dirs[:] = [d for d in dirs if d.lower() not in SKIP_FOLDERS]
    for f in files:
      if f.endswith(".c"):
        c_files.append(os.path.join(root, f))

  if not c_files:
    print(f"No .c files found in {folder_path}")
    return

  print(
      f"Found {len(c_files)} .c file(s) in {folder_path} (excluding"
      f" {SKIP_FOLDERS})"
  )
  for filepath in c_files:
    index_file(filepath)


if __name__ == "__main__":
  
  index_file("data/sample1.c")
  index_file("data/sample2.c")
  index_file("data/sample3.c")
  index_folder("data/CJSON")

  print("\nTotal chunks in DB:", collection.count())
