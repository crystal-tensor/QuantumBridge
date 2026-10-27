# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Enumerate AST candidates with bounded hints, not a Python type proof."""

import argparse
import ast
from collections import Counter
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
METHODS = {"compose", "dot", "tensor", "expand"}
FACTORIES = {"from_circuit", "from_label", "as_native_operator", "as_qiskit_operator"}
RETURNS_OPERATOR = METHODS | {"copy", "adjoint", "conjugate", "transpose", "reverse_qargs", "power", "reshape"}


def migration_review(record):
    """Keep unresolved aliases visible; only bounded claims are classified."""
    path, scope, hint = (record[key] for key in ("path", "scope", "receiver_hint"))
    if not path.startswith("quantumbridge/"):
        return dict(status="UNRESOLVED", reason="Test/example constructor and default expectations need separate migration review.")
    if record["method"] in METHODS:
        if path == "quantumbridge/information/channels.py" and scope == "_embed_operator" and hint == "native_explicit":
            return dict(status="PROVEN", reason="Explicit dense native receiver; runtime guard plus independent embedding/Channel/Choi tests.")
        if path == "quantumbridge/information/operator.py":
            return dict(status="PROVEN", reason="Same-class convention-aware dispatch covered by explicit native/public shadow tests; not future constructor approval.")
        if hint.startswith(("other:", "other_class:", "import:numpy", "import:torch")):
            return dict(status="NOT_APPLICABLE", reason="Canonical lexical receiver is another API; dynamic replacement/subclass behavior is not certified.")
        return dict(status="UNRESOLVED", reason="Alias/factory/attribute or mutable receiver needs context review; no automatic type or absence proof.")
    if record["method"] in FACTORIES | {"Operator"}:
        return dict(status="UNRESOLVED", reason="Constructor/data-source policy is not migrated by arithmetic receiver cleanup.")
    return dict(status="UNRESOLVED", reason="Numeric/@ operand type and data basis require caller evidence.")


class Candidates(ast.NodeVisitor):
    def __init__(self, path, source):
        self.path, self.source = path, source
        self.env, self.scope, self.class_name = {}, [], None
        self.records = []

    def hint(self, node):
        if isinstance(node, ast.Name):return self.env.get(node.id, "unresolved")
        if isinstance(node, ast.Call):
            target = self.hint(node.func)
            if target.startswith("constructor:"):return target.removeprefix("constructor:")
            if isinstance(node.func, ast.Attribute):
                receiver = self.hint(node.func.value)
                if receiver.startswith("constructor:"):receiver = receiver.removeprefix("constructor:")
                if receiver.startswith("native_"):
                    if node.func.attr == "as_native_operator":return "native_explicit"
                    if node.func.attr == "as_qiskit_operator":return "native_public_explicit"
                    if node.func.attr in RETURNS_OPERATOR | FACTORIES:return receiver
            return "unresolved"
        if isinstance(node, ast.Attribute):
            receiver = self.hint(node.value)
            if node.attr == "data" and receiver.startswith("native_"):return "numeric_array"
            if receiver.startswith("import:"):return receiver + "." + node.attr
        if isinstance(node, ast.IfExp):
            first, second = self.hint(node.body), self.hint(node.orelse)
            return first if first == second else "unresolved_union"
        return "unresolved"

    def visit_ImportFrom(self, node):
        for item in node.names:
            name = item.asname or item.name
            if item.name == "Operator" and node.module in ("quantumbridge.information", "quantumbridge.information.operator"):
                self.env[name] = "constructor:native_implicit"
            elif item.name == "Operator" and node.module == "qiskit.quantum_info":
                self.env[name] = "constructor:upstream_public"
            else:self.env[name] = "constructor:other:" + (node.module or "") + "." + item.name

    def visit_Import(self, node):
        for item in node.names:self.env[item.asname or item.name.split(".")[0]] = "import:" + item.name

    def visit_Assign(self, node):
        self.visit(node.value)
        for target in node.targets:
            if isinstance(target, ast.Name):self.env[target.id] = self.hint(node.value)

    def visit_AnnAssign(self, node):
        if node.value is not None:
            self.visit(node.value)
            if isinstance(node.target, ast.Name):self.env[node.target.id] = self.hint(node.value)

    def visit_ClassDef(self, node):
        previous = self.class_name
        self.class_name = node.name
        self.scope.append(node.name)
        for item in node.body:self.visit(item)
        self.scope.pop()
        self.class_name = previous

    def visit_FunctionDef(self, node):
        previous = self.env
        self.env = dict(previous)
        self.scope.append(node.name)
        if self.class_name:
            self.env["self"] = "native_internal_dispatch" if self.path == "quantumbridge/information/operator.py" and self.class_name == "Operator" else "other_class:" + self.class_name
        for item in node.body:self.visit(item)
        self.scope.pop()
        self.env = previous

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Call(self, node):
        method = node.func.attr if isinstance(node.func, ast.Attribute) else None
        constructor = isinstance(node.func, ast.Name) and self.hint(node.func).startswith("constructor:native_")
        if method in METHODS | FACTORIES or constructor:
            receiver = self.hint(node.func.value) if isinstance(node.func, ast.Attribute) else self.hint(node.func)
            self.records.append(dict(path=self.path, line=node.lineno, scope=".".join(self.scope),
                method=method or "Operator", receiver_hint=receiver,
                expression=ast.get_source_segment(self.source, node)))
        self.generic_visit(node)

    def visit_BinOp(self, node):
        if isinstance(node.op, ast.MatMult):
            self.records.append(dict(path=self.path, line=node.lineno, scope=".".join(self.scope),
                method="@", receiver_hint=self.hint(node.left), expression=ast.get_source_segment(self.source, node)))
        self.generic_visit(node)


def inventory(root=ROOT):
    records, files = [], {}
    for directory in ("quantumbridge", "tests", "examples"):
        for path in sorted((root / directory).rglob("*.py")):
            if "__pycache__" in path.parts:continue
            source = path.read_text(encoding="utf-8")
            name = str(path.relative_to(root))
            files[name] = hashlib.sha256(source.encode()).hexdigest()
            visitor = Candidates(name, source)
            visitor.visit(ast.parse(source, filename=name))
            records.extend(visitor.records)
    for record in records:record["migration_review"] = migration_review(record)
    return dict(protocol_version=1, roots=["quantumbridge", "tests", "examples"],
        qualification="AST candidates and local lexical hints only; unresolved/dynamic receivers require manual review, not absence proof.",
        files=files, counts=dict(sorted(Counter(item["receiver_hint"] for item in records).items())),
        review_counts=dict(sorted(Counter(item["migration_review"]["status"] for item in records).items())),
        records=sorted(records, key=lambda item:(item["path"], item["line"], item["method"])))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    options = parser.parse_args()
    result = inventory()
    options.output.parent.mkdir(parents=True, exist_ok=True)
    options.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(dict(output=str(options.output), files=len(result["files"]), candidates=len(result["records"]))))


if __name__ == "__main__":main()
