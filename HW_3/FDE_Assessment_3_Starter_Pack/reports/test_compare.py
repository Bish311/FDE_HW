from __future__ import annotations

import csv
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.contracts import ProcurementDecision
from src.solution import handle_request


def norm(value: object) -> str:
    return str(value).strip().lower()


def list_text(items: list[object]) -> list[str]:
    return [norm(x) for x in items]


def group_present(items: list[object], group: list[str]) -> bool:
    texts = list_text(items)
    for token in group:
        for item in texts:
            if norm(token) in item:
                return True
    return False


def evaluate_decision(decision: ProcurementDecision, expectations: dict) -> list[str]:
    failures: list[str] = []

    for group in expectations.get("required_approvals_any_groups", []):
        if not group_present(decision.required_approvals, group):
            failures.append(f"approval missing (expected one of: {group})")

    for group in expectations.get("risk_flags_any_groups", []):
        if not group_present(decision.risk_flags, group):
            failures.append(f"risk flag missing (expected one of: {group})")

    for group in expectations.get("missing_information_any_groups", []):
        if not group_present(decision.missing_information, group):
            failures.append(f"missing-info item absent (expected one of: {group})")

    for token in expectations.get("risk_flags_must_not_contain", []):
        if group_present(decision.risk_flags, [token]):
            failures.append(f"unexpected risk flag containing: {token}")

    max_missing = expectations.get("max_missing_information")
    if max_missing is not None and len(decision.missing_information) > max_missing:
        failures.append(f"too many missing items: {len(decision.missing_information)}")

    min_evidence = expectations.get("min_evidence_items", 0)
    if len(decision.evidence) < min_evidence:
        failures.append(f"insufficient evidence items: {len(decision.evidence)} < {min_evidence}")

    expected_human = expectations.get("human_review_required")
    if expected_human is not None and decision.human_review_required != expected_human:
        failures.append(f"human_review_required expected {expected_human}")

    return failures


def run_benchmark() -> dict[str, object]:
    cases_file = ROOT / "evals" / "public_cases.json"
    cases = json.loads(cases_file.read_text(encoding="utf-8"))

    results: dict[str, list[dict[str, object]]] = {"single": [], "staged": []}
    architectures = ["single", "staged"]

    print("=" * 70)
    print("RUNNING HEAD-TO-HEAD BENCHMARK: SINGLE vs STAGED ARCHITECTURE")
    print("=" * 70)

    for arch in architectures:
        print(f"\nEvaluating Architecture: {arch.upper()}")
        print("-" * 50)
        for case in cases:
            req_id = case["request_id"]
            title = case["title"]
            start_t = time.perf_counter()
            try:
                dec = handle_request(req_id, architecture=arch)  # type: ignore[arg-type]
                elapsed = (time.perf_counter() - start_t) * 1000.0
                failures = evaluate_decision(dec, case["expectations"])
                passed = len(failures) == 0
                status_str = "PASS" if passed else "FAIL"
                print(f"[{status_str}] {case['case_id']} - {title[:32]:<32} | {elapsed:6.1f} ms | Evidence: {len(dec.evidence)}")
                results[arch].append({
                    "case_id": case["case_id"],
                    "request_id": req_id,
                    "title": title,
                    "passed": passed,
                    "latency_ms": elapsed,
                    "evidence_count": len(dec.evidence),
                    "approvals_count": len(dec.required_approvals),
                    "risk_flags_count": len(dec.risk_flags),
                    "llm_calls": dec.telemetry.llm_calls if dec.telemetry else 2,
                    "tool_calls": dec.telemetry.tool_calls if dec.telemetry else 4,
                    "failures": "; ".join(failures),
                })
            except Exception as exc:  # noqa: BLE001
                elapsed = (time.perf_counter() - start_t) * 1000.0
                print(f"[ERR ] {case['case_id']} - {title[:32]:<32} | {elapsed:6.1f} ms | {exc}")
                results[arch].append({
                    "case_id": case["case_id"],
                    "request_id": req_id,
                    "title": title,
                    "passed": False,
                    "latency_ms": elapsed,
                    "evidence_count": 0,
                    "approvals_count": 0,
                    "risk_flags_count": 0,
                    "llm_calls": 0,
                    "tool_calls": 0,
                    "failures": str(exc),
                })

    out_csv = ROOT / "reports" / "comparison_benchmark.csv"
    flat_rows: list[dict[str, object]] = []
    for arch, rows in results.items():
        for r in rows:
            entry = dict(r)
            entry["architecture"] = arch
            flat_rows.append(entry)

    if flat_rows:
        with open(out_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(flat_rows[0].keys()))
            writer.writeheader()
            writer.writerows(flat_rows)
        print(f"\nDetailed CSV exported to: {out_csv}")

    return compute_summary_stats(results)


def compute_summary_stats(results: dict[str, list[dict[str, object]]]) -> dict[str, object]:
    summary: dict[str, dict[str, object]] = {}
    print("\n" + "=" * 70)
    print("BENCHMARK COMPARISON SUMMARY")
    print("=" * 70)
    print(f"{'Metric':<30} | {'Architecture A (Single)':<20} | {'Architecture B (Staged)':<20}")
    print("-" * 76)

    for arch in ["single", "staged"]:
        rows = results[arch]
        total = len(rows)
        passed = 0
        latencies: list[float] = []
        for r in rows:
            if r["passed"]:
                passed += 1
            latencies.append(float(r["latency_ms"]))
        latencies.sort()
        avg_lat = sum(latencies) / len(latencies) if latencies else 0.0
        p95_idx = int(len(latencies) * 0.95)
        p95_lat = latencies[min(p95_idx, len(latencies) - 1)] if latencies else 0.0

        summary[arch] = {
            "total": total,
            "passed": passed,
            "pass_rate": (passed / total * 100.0) if total > 0 else 0.0,
            "avg_latency_ms": avg_lat,
            "p95_latency_ms": p95_lat,
            "min_latency_ms": latencies[0] if latencies else 0.0,
            "max_latency_ms": latencies[-1] if latencies else 0.0,
        }

    s_a = summary["single"]
    s_b = summary["staged"]

    p_a_str = f"{s_a['pass_rate']:.1f}% ({s_a['passed']}/{s_a['total']})"
    p_b_str = f"{s_b['pass_rate']:.1f}% ({s_b['passed']}/{s_b['total']})"
    lat_a_str = f"{s_a['avg_latency_ms']:.1f} ms"
    lat_b_str = f"{s_b['avg_latency_ms']:.1f} ms"
    p95_a_str = f"{s_a['p95_latency_ms']:.1f} ms"
    p95_b_str = f"{s_b['p95_latency_ms']:.1f} ms"
    min_max_a = f"{s_a['min_latency_ms']:.0f} / {s_a['max_latency_ms']:.0f} ms"
    min_max_b = f"{s_b['min_latency_ms']:.0f} / {s_b['max_latency_ms']:.0f} ms"

    print(f"{'Total Evaluated Cases':<30} | {s_a['total']!s:<20} | {s_b['total']!s:<20}")
    print(f"{'Pass Rate':<30} | {p_a_str:<20} | {p_b_str:<20}")
    print(f"{'Average Latency':<30} | {lat_a_str:<20} | {lat_b_str:<20}")
    print(f"{'p95 Latency':<30} | {p95_a_str:<20} | {p95_b_str:<20}")
    print(f"{'Min / Max Latency':<30} | {min_max_a:<20} | {min_max_b:<20}")
    print("=" * 76)

    return summary


if __name__ == "__main__":
    run_benchmark()
