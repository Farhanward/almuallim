from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _severity(record: dict[str, Any]) -> str:
    metrics = record.get("metrics") or {}
    for key in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
        values = metrics.get(key) if isinstance(metrics, dict) else None
        if values:
            item = values[0]
            if isinstance(item, dict):
                data = item.get("cvssData") or {}
                return str(data.get("baseSeverity") or item.get("baseSeverity") or "UNKNOWN").upper()
    vuln = record.get("vuln") if isinstance(record.get("vuln"), dict) else record
    return str(vuln.get("severity") or record.get("severity") or "UNKNOWN").upper()


def _description(record: dict[str, Any]) -> str:
    vuln = record.get("vuln") if isinstance(record.get("vuln"), dict) else record
    descriptions = vuln.get("descriptions") if isinstance(vuln, dict) else None
    if isinstance(descriptions, list):
        for item in descriptions:
            if item.get("lang") == "en":
                return str(item.get("value") or "")
    return str(record.get("description") or record.get("summary") or "")


def _cve_id(record: dict[str, Any], index: int) -> str:
    vuln = record.get("vuln") if isinstance(record.get("vuln"), dict) else record
    return str(vuln.get("id") or record.get("id") or f"CVE-LESSON-{index}")


def lesson_from_cve(record: dict[str, Any], index: int) -> dict[str, Any]:
    cve = _cve_id(record, index)
    severity = _severity(record)
    description = _description(record)
    concept = "تحليل ثغرة وقراءة أثرها"
    if any(word in description.lower() for word in ("buffer", "overflow", "memory")):
        concept = "سلامة الذاكرة"
    elif any(word in description.lower() for word in ("sql", "injection", "xss", "script")):
        concept = "حقن المدخلات"
    elif any(word in description.lower() for word in ("auth", "credential", "password", "privilege")):
        concept = "التحكم بالوصول"
    return {
        "id": cve,
        "title": f"درس أمني: {cve}",
        "level": "advanced" if severity in {"CRITICAL", "HIGH"} else "intermediate",
        "concept": concept,
        "severity": severity,
        "summary_ar": f"اقرأ وصف {cve} وحدد الأصل المتأثر، شرط الاستغلال، والأثر المتوقع. الشدة: {severity}.",
        "source_text": description[:1200],
        "exercise": "اكتب قاعدة كشف أو اختباراً صغيراً يثبت أن المدخل الضار لا يمر دون تحقق.",
        "quiz": [
            {"question": "ما الأصل المتأثر؟", "expected": "اسم المنتج أو المكتبة أو الخدمة."},
            {"question": "ما نوع الخطر؟", "expected": concept},
            {"question": "ما أول إجراء تخفيف؟", "expected": "تحديث، تحقق مدخلات، تقليل صلاحيات، أو مراقبة حسب الحالة."},
        ],
    }


def convert_nvd(input_path: str | Path, out_path: str | Path, *, limit: int = 0) -> dict[str, Any]:
    source = Path(input_path)
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    rows = 0
    severity_counts: dict[str, int] = {}
    with source.open("r", encoding="utf-8") as handle, out.open("w", encoding="utf-8") as output:
        for index, line in enumerate(handle, start=1):
            if limit and rows >= limit:
                break
            if not line.strip():
                continue
            record = json.loads(line)
            lesson = lesson_from_cve(record, index)
            output.write(json.dumps(lesson, ensure_ascii=False) + "\n")
            severity_counts[lesson["severity"]] = severity_counts.get(lesson["severity"], 0) + 1
            rows += 1
    return {"source": str(source.resolve()), "out": str(out.resolve()), "rows": rows, "severity_counts": severity_counts}

