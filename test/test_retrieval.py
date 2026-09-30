import ollama
import chromadb

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("c_codebase")

query = "code that create a binary tree"
query_embedding = ollama.embeddings(model="nomic-embed-text", prompt=query)["embedding"]

results = collection.query(query_embeddings=[query_embedding], n_results=2)

for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
    print(f"--- {meta['type']} from {meta['file']} (lines {meta['start_line']}-{meta['end_line']}) ---")
    print(doc)
    print()