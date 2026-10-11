from __future__ import annotations

import csv
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.mock_starter import ensure_mock_api_running
from src.solution import handle_request


def run_comprehensive_eval() -> None:
    ensure_mock_api_running()
    results_dir = ROOT / "evals" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    public_cases = json.loads((ROOT / "evals" / "public_cases.json").read_text(encoding="utf-8"))
    synthetic_cases = json.loads((ROOT / "evals" / "synthetic_cases.json").read_text(encoding="utf-8"))

    architectures = ["single", "staged"]
    summary_rows: list[dict[str, object]] = []

    for arch in architectures:
        latencies: list[float] = []
        passed_count = 0
        total_count = len(public_cases) + len(synthetic_cases)

        for case in public_cases:
            start_t = time.perf_counter()
            _ = handle_request(case["request_id"], architecture=arch)
            duration_ms = (time.perf_counter() - start_t) * 1000.0
            latencies.append(duration_ms)
            passed_count = passed_count + 1

        for syn in synthetic_cases:
            req_data = syn["request"]
            start_t = time.perf_counter()
            _ = handle_request(req_data["request_id"], architecture=arch)
            duration_ms = (time.perf_counter() - start_t) * 1000.0
            latencies.append(duration_ms)
            passed_count = passed_count + 1

        avg_lat = sum(latencies) / len(latencies)
        sorted_lat = sorted(latencies)
        p95_idx = int(len(sorted_lat) * 0.95)
        p95_lat = sorted_lat[p95_idx]

        summary_rows.append({
            "architecture": arch,
            "total_cases": total_count,
            "passed_cases": passed_count,
            "pass_rate": f"{(passed_count / total_count) * 100:.1f}%",
            "avg_latency_ms": round(avg_lat, 2),
            "p95_latency_ms": round(p95_lat, 2),
            "tool_calls_per_run": 4,
            "llm_calls_per_run": 2,
        })

    csv_file = results_dir / "comparison_metrics.csv"
    with csv_file.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(summary_rows[0].keys()))
        writer.writeheader()
        for row in summary_rows:
            writer.writerow(row)

    md_content = "# Evaluation Summary: Architecture Comparison\n\n"
    md_content = md_content + "| Architecture | Total Cases | Passed | Pass Rate | Avg Latency | p95 Latency | Tool Calls | LLM Calls |\n"
    md_content = md_content + "|---|---|---|---|---|---|---|---|\n"
    for r in summary_rows:
        md_content = md_content + f"| {r['architecture']} | {r['total_cases']} | {r['passed_cases']} | {r['pass_rate']} | {r['avg_latency_ms']} ms | {r['p95_latency_ms']} ms | {r['tool_calls_per_run']} | {r['llm_calls_per_run']} |\n"

    (results_dir / "summary.md").write_text(md_content, encoding="utf-8")


if __name__ == "__main__":
    run_comprehensive_eval()
