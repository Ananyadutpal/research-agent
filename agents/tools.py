"""Tools the researcher agent can call."""
import ast
import json
import operator

OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
       ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod,
       ast.USub: operator.neg}


def calculator(expression: str) -> str:
    """Safely evaluate arithmetic (no eval(): walks the AST and allows only numbers/operators)."""
    def ev(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in OPS:
            return OPS[type(node.op)](ev(node.left), ev(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in OPS:
            return OPS[type(node.op)](ev(node.operand))
        raise ValueError("Unsupported expression")
    return str(ev(ast.parse(expression, mode="eval").body))


def search_web(query: str) -> str:
    from ddgs import DDGS
    results = DDGS().text(query, max_results=5)
    return json.dumps([{"title": r["title"], "url": r["href"], "snippet": r["body"]}
                       for r in results])


def fetch_url(url: str) -> str:
    import requests
    from bs4 import BeautifulSoup
    resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    return soup.get_text(" ", strip=True)[:6000]


def build_tools(memory):
    """Return (schemas, functions) for the researcher, with memory bound in."""
    def recall_memory(query: str) -> str:
        return json.dumps(memory.search(query)) or "[]"

    functions = {"search_web": search_web, "fetch_url": fetch_url,
                 "calculator": calculator, "recall_memory": recall_memory}

    def schema(name, desc, prop):
        return {"name": name, "description": desc,
                "input_schema": {"type": "object", "properties": {prop: {"type": "string"}},
                                 "required": [prop]}}
    schemas = [
        schema("search_web", "Search the web. Returns titles, URLs, snippets.", "query"),
        schema("fetch_url", "Fetch readable text of a web page.", "url"),
        schema("calculator", "Evaluate an arithmetic expression, e.g. '(120*0.15)+40'.", "expression"),
        schema("recall_memory", "Search previously saved research reports.", "query"),
    ]
    return schemas, functions
