import ollama

response = ollama.chat(
    model='qwen2.5-coder:7b',
    messages=[
        {'role': 'user', 'content': 'Write a C function that reverses a singly linked list.'}
    ]
)

print(response['message']['content'])