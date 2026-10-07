import ollama

code_to_explain = """
struct Node {
    int data;
    struct Node *next;
};

struct Node* reverse(struct Node *head) {
    struct Node *prev = NULL;
    struct Node *curr = head;
    while (curr != NULL) {
        struct Node *next = curr->next;
        curr->next = prev;
        prev = curr;
        curr = next;
    }
    return prev;
}
"""

response = ollama.chat(
    model='qwen2.5-coder:7b',
    messages=[
        {'role': 'user', 'content': f"Explain what this C function does, step by step:\n\n{code_to_explain}"}
    ]
)

print(response['message']['content'])