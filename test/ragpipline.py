import ollama
import chromadb

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("c_codebase")

def retrieve_context(query, n_results=3):
    query_embedding = ollama.embeddings(model="nomic-embed-text", prompt=query)["embedding"]
    results = collection.query(query_embeddings=[query_embedding], n_results=n_results)
    chunks = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        chunks.append({"text": doc, "meta": meta})
    return chunks

def build_prompt(user_question, chunks):
    context_blocks = []
    for c in chunks:
        m = c["meta"]
        context_blocks.append(f"# {m['type']} from {m['file']} (lines {m['start_line']}-{m['end_line']})\n{c['text']}")
    context = "\n\n".join(context_blocks)

    prompt = f"""You are a C programming assistant. Use the following code context from the project to answer the question when relevant.

RULES:
1. If the context below contains code relevant to the question, base your answer primarily on that code and reference it directly.
2. If the context does NOT contain anything relevant to the question, explicitly say so first (e.g. "This isn't in the current codebase, but here's a general answer:") before providing a general C programming answer.
3. Never present general-knowledge code as if it came from the project's codebase.

CONTEXT:
{context}

QUESTION:
{user_question}
"""
    return prompt

def generate_answer(user_question):
    chunks = retrieve_context(user_question)
    prompt = build_prompt(user_question, chunks)
    response = ollama.chat(model='qwen2.5-coder:7b', messages=[{'role': 'user', 'content': prompt}])
    return response['message']['content']

if __name__ == "__main__":
    print("C-Copilot (type 'exit' to quit)")
    while True:
        q = input("\nAsk a question about the codebase: ")
        if q.lower() == "exit":
            break
        if not q.strip():
            continue
        print("\n" + generate_answer(q))