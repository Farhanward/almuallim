from __future__ import annotations


def markdown(summary: dict, title: str = "تقرير المعلّم") -> str:
    return "\n".join(
        [
            f"# {title}",
            "",
            f"- المدخل: `{summary.get('input')}`",
            f"- السجلات: `{summary.get('records', 0)}`",
            f"- المعالجة: `{summary.get('processed', 0)}`",
            f"- الجودة: `{summary.get('quality', 0):.2%}`",
            f"- ناقص: `{summary.get('missing', 0)}`",
            f"- أخطاء: `{summary.get('errors', 0)}`",
            f"- p99: `{summary.get('latency_ms', {}).get('p99', 0):.4f}ms`",
            f"- peak memory: `{summary.get('memory_mb', {}).get('peak', 0):.2f}MB`",
            "",
        ]
    )

