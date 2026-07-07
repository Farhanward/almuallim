from __future__ import annotations

import ast
from pathlib import Path
from typing import Any


def _signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    args = [arg.arg for arg in node.args.args]
    if node.args.vararg:
        args.append("*" + node.args.vararg.arg)
    args.extend(arg.arg for arg in node.args.kwonlyargs)
    if node.args.kwarg:
        args.append("**" + node.args.kwarg.arg)
    return f"{node.name}({', '.join(args)})"


def _complexity(node: ast.AST) -> int:
    score = 1
    branches = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try, ast.ExceptHandler, ast.BoolOp, ast.Match)
    return score + sum(1 for item in ast.walk(node) if isinstance(item, branches))


def analyze_python(path: str | Path) -> dict[str, Any]:
    source_path = Path(path)
    text = source_path.read_text(encoding="utf-8", errors="ignore")
    return analyze_python_source(text, display_path=str(source_path.resolve()))


def analyze_python_source(text: str, display_path: str = "uploaded.py") -> dict[str, Any]:
    tree = ast.parse(text)
    imports = []
    symbols = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
        elif isinstance(node, ast.ClassDef):
            methods = [item.name for item in node.body if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))]
            symbols.append({"kind": "class", "name": node.name, "line": node.lineno, "methods": methods, "complexity": _complexity(node)})
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            symbols.append({"kind": "function", "name": node.name, "signature": _signature(node), "line": node.lineno, "complexity": _complexity(node)})
    return {"path": display_path, "imports": sorted(set(imports)), "symbols": symbols, "lines": len(text.splitlines())}


def lesson_from_analysis(analysis: dict[str, Any]) -> dict[str, Any]:
    symbols = analysis.get("symbols") or []
    main_focus = symbols[0]["name"] if symbols else "الملف"
    explanations = [
        f"هذا الملف يحتوي {len(symbols)} رمزاً رئيسياً و{analysis.get('lines', 0)} سطراً.",
        "ابدأ بقراءة الواردات لأنها تكشف الاعتماديات والحدود الخارجية.",
    ]
    for symbol in symbols[:8]:
        if symbol["kind"] == "class":
            explanations.append(f"الصنف `{symbol['name']}` يجمع سلوكاً مترابطاً ويحتوي methods: {', '.join(symbol.get('methods') or []) or 'لا يوجد'}.")
        else:
            explanations.append(f"الدالة `{symbol.get('signature', symbol['name'])}` تبدأ في السطر {symbol['line']} وتعقيدها التقريبي {symbol['complexity']}.")
    quiz = [
        {"question": f"ما مسؤولية `{main_focus}` في هذا الملف؟", "expected": "اذكر المدخلات والمخرجات والأثر الجانبي إن وجد."},
        {"question": "أي دالة أو صنف يحتاج اختباراً أولاً؟", "expected": "اختر أعلى جزء مخاطرة أو تعقيداً."},
        {"question": "ما الاعتماديات الخارجية التي يجب فهمها؟", "expected": ", ".join(analysis.get("imports") or ["لا توجد"])},
    ]
    return {
        "title": f"درس تفكيك: {Path(analysis['path']).name}",
        "level": "intermediate",
        "summary_ar": "\n".join(explanations),
        "symbols": symbols,
        "quiz": quiz,
        "source": analysis["path"],
    }


def teach_python(path: str | Path) -> dict[str, Any]:
    return lesson_from_analysis(analyze_python(path))


def teach_python_source(text: str, display_path: str = "uploaded.py") -> dict[str, Any]:
    return lesson_from_analysis(analyze_python_source(text, display_path=display_path))

