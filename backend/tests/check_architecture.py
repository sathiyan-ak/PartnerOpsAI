"""Architecture guardrails: Enforce layering rules."""

import ast
import sys
from pathlib import Path


class ImportChecker(ast.NodeVisitor):
    """Check imports to enforce architecture rules."""

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.errors: list[str] = []

    def visit_ImportFrom(self, node):
        if node.module:
            self._check_import(node.module)
        self.generic_visit(node)

    def visit_Import(self, node):
        for alias in node.names:
            self._check_import(alias.name)
        self.generic_visit(node)

    def _check_import(self, module: str):
        """Enforce architecture rules."""
        filepath = self.filepath

        # Rule 1: Domain cannot import Infrastructure
        if "domain" in filepath and "infrastructure" in module:
            self.errors.append(f"{filepath}: Domain layer imports Infrastructure ({module})")

        # Rule 2: Domain cannot import Application
        if "domain" in filepath and "application" in module:
            self.errors.append(f"{filepath}: Domain layer imports Application ({module})")

        # Rule 3: Application cannot import Infrastructure directly
        # (only through interfaces)
        if "application" in filepath and "infrastructure.repositories" in module:
            self.errors.append(
                f"{filepath}: Application imports concrete Infrastructure ({module})"
            )

        # Rule 4: Infrastructure repositories stay in infrastructure
        if "infrastructure" not in filepath and "infrastructure.repositories" in module:
            self.errors.append(
                f"{filepath}: Non-infrastructure code imports repository implementation ({module})"
            )


def check_architecture():
    """Check all Python files for architecture violations."""
    backend_path = Path("backend")
    all_errors = []

    for py_file in backend_path.rglob("*.py"):
        # Skip test files
        if "test" in str(py_file):
            continue

        try:
            with open(py_file, "r") as f:
                tree = ast.parse(f.read(), str(py_file))
                checker = ImportChecker(str(py_file))
                checker.visit(tree)
                all_errors.extend(checker.errors)
        except SyntaxError as e:
            print(f"✗ Syntax error in {py_file}: {e}")
            sys.exit(1)

    if all_errors:
        print("✗ Architecture violations found:")
        for error in all_errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print("✓ Architecture rules enforced:")
        print("  - Domain does not import Application or Infrastructure")
        print("  - Application does not import concrete Infrastructure")
        print("  - Repository implementations stay in Infrastructure")
        sys.exit(0)


if __name__ == "__main__":
    check_architecture()
