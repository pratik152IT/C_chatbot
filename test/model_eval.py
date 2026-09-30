import ollama
import time
from deepeval.models import OllamaModel
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

MODELS = ["llama3.2", "qwen2.5-coder:1.5b", "qwen2.5-coder:7b"]

TEST_PROMPTS = {
    "generation": "Write a C function that checks if a number is prime.",
    "debugging": """Find and explain the bugs in this C code:

#include <stdlib.h>
void process(int n) {
    int *arr = malloc(n * sizeof(int));
    for (int i = 0; i <= n; i++) {
        arr[i] = i * 2;
    }
}""",
    "readability": """Explain what this C function does, step by step:

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
}"""
}

# Judge model — uses the same Ollama server
judge_model = OllamaModel(model="qwen2.5-coder:7b", base_url="http://localhost:11434", temperature=0)

accuracy_metric = GEval(
    name="Accuracy",
    criteria="Determine if the response is technically correct C code or a correct explanation of the given C code.",
    evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
    model=judge_model,
)

readability_metric = GEval(
    name="Readability",
    criteria="Determine if the response is clear, well-structured, and easy for a developer to understand.",
    evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
    model=judge_model,
)

results = []

for model in MODELS:
    for task_name, prompt in TEST_PROMPTS.items():
        print(f"Running {model} / {task_name}...")

        start = time.time()
        response = ollama.chat(model=model, messages=[{'role': 'user', 'content': prompt}])
        latency = time.time() - start
        output_text = response['message']['content']

        test_case = LLMTestCase(input=prompt, actual_output=output_text)

        accuracy_metric.measure(test_case)
        readability_metric.measure(test_case)

        results.append({
            "model": model,
            "task": task_name,
            "latency": round(latency, 2),
            "accuracy": round(accuracy_metric.score, 2),
            "readability": round(readability_metric.score, 2),
        })
        print(f"  -> latency={latency:.2f}s  accuracy={accuracy_metric.score:.2f}  readability={readability_metric.score:.2f}")

# Summary table
print("\n" + "="*70)
print(f"{'Model':<20}{'Avg Latency (s)':<18}{'Avg Accuracy':<15}{'Avg Readability':<15}")
print("="*70)

for model in MODELS:
    model_results = [r for r in results if r["model"] == model]
    avg_lat = sum(r["latency"] for r in model_results) / len(model_results)
    avg_acc = sum(r["accuracy"] for r in model_results) / len(model_results)
    avg_read = sum(r["readability"] for r in model_results) / len(model_results)
    print(f"{model:<20}{avg_lat:<18.2f}{avg_acc:<15.2f}{avg_read:<15.2f}")