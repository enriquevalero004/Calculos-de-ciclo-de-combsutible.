"""The physics package must not depend on the UI."""

import ast
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src" / "fcsim"


def test_core_does_not_import_streamlit():
    offenders = []
    for path in SRC.rglob("*.py"):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            if any(n.split(".")[0] == "streamlit" for n in names):
                offenders.append(str(path.relative_to(SRC)))
    assert offenders == []
