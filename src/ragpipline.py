import chromadb
import ollama
from src.structure_extractor import get_structure_summary

# Target vector store inside data/
client = chromadb.PersistentClient(path="data/chroma_db")
collection = client.get_or_create_collection("c_codebase")

DISTANCE_THRESHOLD = 1.0


def retrieve_context(query, n_results=3):
  query_embedding = ollama.embeddings(
      model="nomic-embed-text", prompt=query
  )["embedding"]
  results = collection.query(
      query_embeddings=[query_embedding], n_results=n_results
  )

  chunks = []
  documents = results["documents"][0]
  metadatas = results["metadatas"][0]
  distances = results["distances"][0]

  for doc, meta, dist in zip(documents, metadatas, distances):
    if dist <= DISTANCE_THRESHOLD:
      chunks.append({"text": doc, "meta": meta})

  return chunks


def build_prompt(user_question, chunks):
  if not chunks:
    context = "(No relevant code was found in the codebase for this question.)"
    structure_info = "(None)"
  else:
    context_blocks = []
    structure_blocks = []
    for c in chunks:
      m = c["meta"]
      context_blocks.append(
          f"# {m['type']} from {m['file']} (lines"
          f" {m['start_line']}-{m['end_line']})\n{c['text']}"
      )
      structure_blocks.append(get_structure_summary(c["text"], m["type"]))
    context = "\n\n".join(context_blocks)
    structure_info = "\n".join(structure_blocks)

  prompt = f"""You are a C programming assistant. Use the following code context and structure info from the project to answer the question when relevant.

RULES:
1. If the context below contains code relevant to the question, base your answer primarily on that code and reference it directly.
2. If the context does NOT contain anything relevant to the question, explicitly say so first before providing a general C programming answer.
3. Never present general-knowledge code as if it came from the project's codebase.

STRUCTURE INFO (signatures only, for quick reference):
{structure_info}

FULL CODE CONTEXT:
{context}

QUESTION:
{user_question}
"""
  return prompt


def generate_answer(user_question):
  try:
    chunks = retrieve_context(user_question)
    prompt = build_prompt(user_question, chunks)
    response = ollama.chat(
        model="qwen2.5-coder:7b", messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"]
  except Exception as e:
    return f"Something went wrong while generating a response: {e}"


if __name__ == "__main__":
  print("C-Copilot (type 'exit' to quit)")
  while True:
    q = input("\nAsk a question about the codebase: ")
    if q.lower() == "exit":
      break
    if not q.strip():
      continue
    print("\n" + generate_answer(q))