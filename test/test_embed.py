import ollama

response = ollama.embeddings(
    model='nomic-embed-text',
    prompt='int add(int a, int b) { return a + b; }'
)

embedding = response['embedding']
print(f"Embedding length: {len(embedding)}")
print(f"First 5 values: {embedding[:5]}")