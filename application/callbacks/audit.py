"""Static callback audit for the legacy Telegram core."""
from __future__ import annotations
import ast
from dataclasses import dataclass
from pathlib import Path
from .catalog import resolve_callback

@dataclass(frozen=True)
class CallbackOccurrence:
    value: str
    line: int
    resolved: bool

def _constant_prefix(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        parts = []
        for value in node.values:
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                parts.append(value.value)
            else:
                break
        return ''.join(parts) or None
    return None

def extract_callback_literals(source_path: str | Path) -> list[CallbackOccurrence]:
    text = Path(source_path).read_text(encoding="utf-8")
    tree = ast.parse(text, filename=str(source_path))
    out: list[CallbackOccurrence] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        for kw in node.keywords:
            if kw.arg != "callback_data":
                continue
            value = _constant_prefix(kw.value)
            if value is not None:
                out.append(CallbackOccurrence(value, node.lineno, resolve_callback(value) is not None))
    return out

def audit_callbacks(source_path: str | Path) -> list[CallbackOccurrence]:
    return [item for item in extract_callback_literals(source_path) if not item.resolved]
