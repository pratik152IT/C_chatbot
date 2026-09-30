import tree_sitter_c as tsc
from tree_sitter import Language, Parser

C_LANGUAGE = Language(tsc.language())
parser = Parser(C_LANGUAGE)

def chunk_c_file(filepath):
    with open(filepath, "rb") as f:
        code = f.read()

    tree = parser.parse(code)
    chunks = []

    def walk(node):
        if node.type in ("function_definition", "struct_specifier"):
            text = code[node.start_byte:node.end_byte].decode("utf-8")
            chunks.append({
                "file": filepath,
                "type": node.type,
                "start_line": node.start_point[0] + 1,
                "end_line": node.end_point[0] + 1,
                "text": text,
            })
        else:
            for child in node.children:
                walk(child)

    walk(tree.root_node)
    return chunks

if __name__ == "__main__":
    chunks = chunk_c_file("sample1.c")
    for c in chunks:
        print(f"--- {c['type']} (lines {c['start_line']}-{c['end_line']}) ---")
        print(c['text'])
        print()
