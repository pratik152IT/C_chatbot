#include <stdlib.h>

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

void process(int n) {
    int *arr = malloc(n * sizeof(int));
    for (int i = 0; i <= n; i++) {
        arr[i] = i * 2;
    }
}