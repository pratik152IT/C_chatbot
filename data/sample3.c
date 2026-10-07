#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <limits.h>

/* ============================================================================
 * PROGRAM 1: DYNAMIC VECTOR IMPLEMENTATION (DATA STRUCTURES)
 * ============================================================================ */

typedef struct {
    int *data;
    size_t capacity;
    size_t size;
} Vector;

Vector* vector_create(size_t initial_capacity) {
    Vector *vec = (Vector *)malloc(sizeof(Vector));
    if (!vec) return NULL;
    vec->data = (int *)malloc(initial_capacity * sizeof(int));
    if (!vec->data) {
        free(vec);
        return NULL;
    }
    vec->capacity = initial_capacity;
    vec->size = 0;
    return vec;
}

bool vector_push_back(Vector *vec, int value) {
    if (!vec) return false;
    if (vec->size >= vec->capacity) {
        size_t new_capacity = vec->capacity * 2;
        int *new_data = (int *)realloc(vec->data, new_capacity * sizeof(int));
        if (!new_data) return false;
        vec->data = new_data;
        vec->capacity = new_capacity;
    }
    vec->data[vec->size++] = value;
    return true;
}

int vector_get(const Vector *vec, size_t index, bool *out_error) {
    if (!vec || index >= vec->size) {
        if (out_error) *out_error = true;
        return -1;
    }
    if (out_error) *out_error = false;
    return vec->data[index];
}

void vector_free(Vector *vec) {
    if (vec) {
        free(vec->data);
        free(vec);
    }
}

void run_vector_demo(void) {
    printf("=== Program 1: Vector Demo ===\n");
    Vector *vec = vector_create(4);
    for (int i = 1; i <= 10; ++i) {
        vector_push_back(vec, i * 10);
    }
    
    printf("Vector elements: ");
    for (size_t i = 0; i < vec->size; ++i) {
        bool err = false;
        int val = vector_get(vec, i, &err);
        if (!err) printf("%d ", val);
    }
    printf("\nCapacity: %zu, Size: %zu\n\n", vec->capacity, vec->size);
    vector_free(vec);
}

/* ============================================================================
 * PROGRAM 2: DIJKSTRA'S SHORTEST PATH ALGORITHM (GRAPH THEORY)
 * ============================================================================ */

#define MAX_NODES 6

typedef struct {
    int num_nodes;
    int adj_matrix[MAX_NODES][MAX_NODES];
} Graph;

Graph* graph_create(int nodes) {
    Graph *g = (Graph *)malloc(sizeof(Graph));
    g->num_nodes = nodes;
    for (int i = 0; i < nodes; i++) {
        for (int j = 0; j < nodes; j++) {
            g->adj_matrix[i][j] = (i == j) ? 0 : INT_MAX;
        }
    }
    return g;
}

void graph_add_edge(Graph *g, int src, int dest, int weight) {
    if (src >= 0 && src < g->num_nodes && dest >= 0 && dest < g->num_nodes) {
        g->adj_matrix[src][dest] = weight;
        g->adj_matrix[dest][src] = weight;
    }
}

int min_distance_node(const int dist[], const bool visited[], int num_nodes) {
    int min = INT_MAX, min_index = -1;
    for (int v = 0; v < num_nodes; v++) {
        if (!visited[v] && dist[v] <= min) {
            min = dist[v];
            min_index = v;
        }
    }
    return min_index;
}

void dijkstra_shortest_path(Graph *g, int src_node) {
    int dist[MAX_NODES];
    bool visited[MAX_NODES];

    for (int i = 0; i < g->num_nodes; i++) {
        dist[i] = INT_MAX;
        visited[i] = false;
    }

    dist[src_node] = 0;

    for (int count = 0; count < g->num_nodes - 1; count++) {
        int u = min_distance_node(dist, visited, g->num_nodes);
        if (u == -1) break;
        
        visited[u] = true;

        for (int v = 0; v < g->num_nodes; v++) {
            if (!visited[v] && g->adj_matrix[u][v] != INT_MAX && 
                dist[u] != INT_MAX && (dist[u] + g->adj_matrix[u][v] < dist[v])) {
                dist[v] = dist[u] + g->adj_matrix[u][v];
            }
        }
    }

    printf("=== Program 2: Dijkstra Shortest Path from Node %d ===\n", src_node);
    for (int i = 0; i < g->num_nodes; i++) {
        printf("Node %d -> Shortest Distance: %d\n", i, dist[i]);
    }
    printf("\n");
}

void run_dijkstra_demo(void) {
    Graph *g = graph_create(6);
    graph_add_edge(g, 0, 1, 7);
    graph_add_edge(g, 0, 2, 9);
    graph_add_edge(g, 0, 5, 14);
    graph_add_edge(g, 1, 2, 10);
    graph_add_edge(g, 1, 3, 15);
    graph_add_edge(g, 2, 3, 11);
    graph_add_edge(g, 2, 5, 2);
    graph_add_edge(g, 3, 4, 6);
    graph_add_edge(g, 4, 5, 9);

    dijkstra_shortest_path(g, 0);
    free(g);
}

/* ============================================================================
 * PROGRAM 3: SIMPLE CSV PARSER & QUERY ENGINE (STRING PROCESSING)
 * ============================================================================ */

#define MAX_ROWS 10
#define MAX_COLS 3
#define FIELD_LEN 32

typedef struct {
    char header[MAX_COLS][FIELD_LEN];
    char rows[MAX_ROWS][MAX_COLS][FIELD_LEN];
    size_t col_count;
    size_t row_count;
} CSVTable;

void csv_parse(CSVTable *table, const char *csv_data) {
    char buffer[1024];
    strncpy(buffer, csv_data, sizeof(buffer) - 1);
    buffer[sizeof(buffer) - 1] = '\0';

    char *line = strtok(buffer, "\n");
    bool is_header = true;
    table->row_count = 0;
    table->col_count = 0;

    while (line != NULL) {
        char *token = strtok(line, ",");
        size_t col_idx = 0;

        while (token != NULL && col_idx < MAX_COLS) {
            if (is_header) {
                strncpy(table->header[col_idx], token, FIELD_LEN - 1);
            } else {
                strncpy(table->rows[table->row_count][col_idx], token, FIELD_LEN - 1);
            }
            token = strtok(NULL, ",");
            col_idx++;
        }

        if (is_header) {
            table->col_count = col_idx;
            is_header = false;
        } else {
            table->row_count++;
        }

        line = strtok(NULL, "\n");
    }
}

void csv_print_column(const CSVTable *table, const char *column_name) {
    int col_index = -1;
    for (size_t j = 0; j < table->col_count; j++) {
        if (strcmp(table->header[j], column_name) == 0) {
            col_index = (int)j;
            break;
        }
    }

    if (col_index == -1) {
        printf("Column '%s' not found.\n", column_name);
        return;
    }

    printf("Values for Column '%s':\n", column_name);
    for (size_t i = 0; i < table->row_count; i++) {
        printf("  Row %zu: %s\n", i + 1, table->rows[i][col_index]);
    }
}

void run_csv_demo(void) {
    printf("=== Program 3: CSV Parser Demo ===\n");
    const char *raw_csv = 
        "ID,Name,Role\n"
        "101,Alice,Engineer\n"
        "102,Bob,Designer\n"
        "103,Charlie,Manager\n";

    CSVTable table;
    csv_parse(&table, raw_csv);
    csv_print_column(&table, "Name");
    csv_print_column(&table, "Role");
    printf("\n");
}

/* ============================================================================
 * MAIN EXECUTION ENTRY POINT
 * ============================================================================ */

int main(void) {
    printf("Starting multi-program execution pipeline...\n\n");
    
    run_vector_demo();
    run_dijkstra_demo();
    run_csv_demo();

    printf("Execution finished successfully.\n");
    return 0;
}