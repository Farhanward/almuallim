from __future__ import annotations

import json
import statistics
import time
import tracemalloc
from pathlib import Path


REQUIRED = ("id", "title", "level", "concept", "summary_ar", "exercise", "quiz")


def _p(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(round((pct / 100) * (len(ordered) - 1))))]


def evaluate_lessons(path: str | Path, *, repeat: int = 1) -> dict:
    rows = [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]
    errors = complete = missing = 0
    latencies = []
    started = time.perf_counter()
    tracemalloc.start()
    for _ in range(repeat):
        for row in rows:
            t0 = time.perf_counter()
            try:
                absent = [key for key in REQUIRED if not row.get(key)]
                quiz_ok = isinstance(row.get("quiz"), list) and len(row["quiz"]) >= 3
                if absent or not quiz_ok:
                    missing += 1
                else:
                    complete += 1
            except Exception:
                errors += 1
            latencies.append((time.perf_counter() - t0) * 1000)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    processed = len(rows) * repeat
    return {
        "input": str(Path(path).resolve()),
        "records": len(rows),
        "repeat": repeat,
        "processed": processed,
        "complete": complete,
        "missing": missing,
        "errors": errors,
        "quality": complete / processed if processed else 0.0,
        "latency_ms": {"mean": statistics.fmean(latencies) if latencies else 0.0, "p99": _p(latencies, 99), "max": max(latencies) if latencies else 0.0},
        "memory_mb": {"current": current / 1_000_000, "peak": peak / 1_000_000},
        "elapsed_seconds": time.perf_counter() - started,
        "collapse_check": {"passed": errors == 0, "criteria": "errors == 0"},
    }

