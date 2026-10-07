import tree_sitter_c as tsc
from tree_sitter import Language, Parser

C_LANGUAGE = Language(tsc.language())
parser = Parser(C_LANGUAGE)

with open("data/sample1.c", "rb") as f:
  code = f.read()

tree = parser.parse(code)


def print_tree(node, indent=0):
  print("  " * indent + node.type)
  for child in node.children:
    print_tree(child, indent + 1)


print_tree(tree.root_node)