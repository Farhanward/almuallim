from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from almuallim.analyzer import teach_python
from almuallim.batch import evaluate_lessons
from almuallim.datasets import convert_nvd


class AlMuallimTests(unittest.TestCase):
    def test_teach_python_file(self):
        with tempfile.TemporaryDirectory(dir="C:/Projects") as tmp:
            path = Path(tmp) / "sample.py"
            path.write_text("import json\n\ndef add(a, b):\n    if a:\n        return a + b\n    return b\n", encoding="utf-8")
            lesson = teach_python(path)
            self.assertIn("درس تفكيك", lesson["title"])
            self.assertEqual(lesson["symbols"][0]["name"], "add")
            self.assertGreaterEqual(len(lesson["quiz"]), 3)

    def test_convert_nvd_fixture(self):
        with tempfile.TemporaryDirectory(dir="C:/Projects") as tmp:
            source = Path(tmp) / "nvd.jsonl"
            out = Path(tmp) / "lessons.jsonl"
            source.write_text('{"id":"CVE-1","severity":"HIGH","description":"SQL injection in product"}\n{"id":"CVE-2","severity":"LOW","description":"Memory bug"}\n', encoding="utf-8")
            summary = convert_nvd(source, out)
            self.assertEqual(summary["rows"], 2)
            rows = [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(rows[0]["concept"], "حقن المدخلات")
            self.assertGreaterEqual(len(rows[0]["quiz"]), 3)

    def test_batch_quality(self):
        with tempfile.TemporaryDirectory(dir="C:/Projects") as tmp:
            lessons = Path(tmp) / "lessons.jsonl"
            lessons.write_text(json.dumps({"id": "1", "title": "t", "level": "beginner", "concept": "c", "summary_ar": "s", "exercise": "e", "quiz": [1, 2, 3]}) + "\n", encoding="utf-8")
            summary = evaluate_lessons(lessons)
            self.assertEqual(summary["errors"], 0)
            self.assertEqual(summary["quality"], 1.0)


if __name__ == "__main__":
    unittest.main()

