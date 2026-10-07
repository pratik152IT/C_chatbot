import tree_sitter_c as tsc
from tree_sitter import Language, Parser

C_LANGUAGE = Language(tsc.language())
parser = Parser(C_LANGUAGE)

def get_structure_summary(code_text, chunk_type):
    """Extract a condensed structural summary from a chunk:
    - function: just the signature (return type, name, params)
    - struct: the struct name and its field declarations
    """
    if chunk_type == "function_definition":
        brace_index = code_text.find('{')
        if brace_index != -1:
            return code_text[:brace_index].strip() + ";"
        return code_text.strip()

    elif chunk_type == "struct_specifier":
        lines = [l.strip() for l in code_text.strip().split('\n') if l.strip()]
        return '\n'.join(lines)

    return code_text.strip()