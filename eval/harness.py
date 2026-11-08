"""Repeatable evaluation harness.

    python -m eval.harness                         # all cases, lean context, 1 run each
    python -m eval.harness --repeats 3             # reliability: outcome consistency per case
    python -m eval.harness --context rich --workflow dynamic
    python -m eval.harness --ids st-unauth-credit,dy-oos-reg-dd
    python -m eval.harness --fail-under 0.7        # non-zero exit for CI

Writes eval/results/<YYYY-MM-DD_HH-MM>_<context>/results.json and report.md, and copies the
report to eval/results/latest.md. Models run at default sampling, so use --repeats to
measure run-to-run variation.
"""

from __future__ import annotations

import argparse
import json
import math
import shutil
import statistics
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import yaml

import config

CASES_PATH = Path(__file__).parent / "cases.yaml"
RESULTS_DIR = Path(__file__).parent / "results"


def load_cases(path: Path = CASES_PATH, ids=None, workflow=None, category=None) -> list[dict]:
    cases = yaml.safe_load(path.read_text())
    if ids:
        cases = [c for c in cases if c["id"] in ids]
    if workflow and workflow != "all":
        cases = [c for c in cases if c["workflow"] == workflow]
    if category:
        cases = [c for c in cases if c["category"] == category]
    return cases


def _section_of(evidence_id: str) -> str | None:
    if not evidence_id.startswith("R-"):
        return None
    return evidence_id[2:].split("#")[0]


# ---------------------------------------------------------------- scoring
def score(case: dict, r: dict) -> dict:
    exp = case.get("expect", {})
    checks: dict[str, bool] = {}
    reasons: list[str] = []

    checks["outcome"] = r["outcome"] in exp.get("outcome", ["answer"])
    if not checks["outcome"]:
        reasons.append(f"outcome {r['outcome']} not in {exp.get('outcome')}")

    if exp.get("product") and r.get("classification"):
        checks["product"] = r["classification"]["product"] == exp["product"]
        if not checks["product"]:
            reasons.append(f"product {r['classification']['product']} != {exp['product']}")

    retrieved = set(r.get("retrieved_sections", []))
    if exp.get("sections_any"):
        checks["retrieval_hit"] = bool(retrieved & set(exp["sections_any"]))
        if not checks["retrieval_hit"]:
            reasons.append(f"none of {exp['sections_any']} retrieved (got {sorted(retrieved)[:6]})")
        if r["outcome"] == "answer":
            cited = {_section_of(c["id"]) for c in r.get("citations", [])}
            checks["citation_hit"] = bool(cited & set(exp["sections_any"]))
            if not checks["citation_hit"]:
                reasons.append(
                    f"answer cites {sorted(s for s in cited if s)}, expected one of "
                    f"{exp['sections_any']}"
                )
    if exp.get("sections_all"):
        missing = set(exp["sections_all"]) - retrieved
        checks["retrieval_all"] = not missing
        if missing:
            reasons.append(f"missing sections {sorted(missing)}")

    if exp.get("actions_any"):
        ran = {a["action"] for a in r.get("actions", [])}
        checks["actions"] = bool(ran & set(exp["actions_any"]))
        if not checks["actions"]:
            reasons.append(f"actions {sorted(ran)} lack {exp['actions_any']}")

    if exp.get("must_not_contain"):
        low = (r.get("response") or "").lower()
        hit = [p for p in exp["must_not_contain"] if p.lower() in low]
        checks["forbidden"] = not hit
        if hit:
            reasons.append(f"response contains forbidden {hit}")

    if r.get("errors"):
        reasons.append(f"errors: {r['errors'][-1][:120]}")

    v = r.get("verification") or {}
    path = r.get("path", [])
    return {
        "id": case["id"],
        "workflow": case["workflow"],
        "category": case["category"],
        "expected": exp.get("outcome"),
        "actual": r["outcome"],
        "passed": all(checks.values()),
        "checks": checks,
        "reasons": reasons,
        "supported_ratio": v.get("supported_ratio"),
        "verifier_caught": path.count("draft") > 1 or "replan" in path,
        "path": path,
        "overrides": r.get("overrides", []),
        "best_reg_score": max(r.get("retrieved_scores") or [0.0]),
        "latency_s": r["latency_s"],
        "cost_usd": r["usage"]["cost_usd"],
        "input_tokens": r["usage"]["input_tokens"],
        "output_tokens": r["usage"]["output_tokens"],
        "llm_calls": r["usage"]["llm_calls"],
        "response": r.get("response", ""),
    }


# ---------------------------------------------------------------- running
def run_case(rt, case: dict) -> dict:
    from graphs.runner import run_dynamic, run_static

    try:
        if case["workflow"] == "static":
            r = run_static(rt, case["input"])
        else:
            r = run_dynamic(rt, case["input"], history=case.get("history"))
    except Exception as e:  # a crash is a failed case, not a crashed harness
        r = {
            "outcome": "crash",
            "errors": [f"{type(e).__name__}: {e}"],
            "latency_s": 0,
            "usage": {"cost_usd": 0, "input_tokens": 0, "output_tokens": 0, "llm_calls": 0},
        }
    return score(case, r)


def run_cases(rt, cases: list[dict], repeats: int = 1, progress=print) -> list[dict]:
    rows = []
    for case in cases:
        for i in range(repeats):
            row = run_case(rt, case)
            row["repeat"] = i
            rows.append(row)
            progress(
                f"  {'PASS' if row['passed'] else 'FAIL'}  {case['id']:<26} "
                f"{row['actual']:<10} {row['latency_s']:>6.1f}s  ${row['cost_usd']:.4f}"
            )
    return rows


# ---------------------------------------------------------------- summarising
def _pct(n, d):
    return f"{100 * n / d:.0f}%" if d else "n/a"


def _clip(text, n):
    text = (text or "").strip()
    return text if len(text) <= n else text[:n].rstrip() + "…"


def summarize(rows: list[dict]) -> dict:
    lat = [r["latency_s"] for r in rows if r["actual"] != "crash"]
    by_case = defaultdict(list)
    for r in rows:
        by_case[r["id"]].append(r["actual"])
    consistency = {
        cid: Counter(outs).most_common(1)[0][1] / len(outs) for cid, outs in by_case.items()
    }
    answered = [r for r in rows if r["actual"] == "answer"]
    ratios = [r["supported_ratio"] for r in answered if r["supported_ratio"] is not None]

    def rate(key):
        vals = [r["checks"][key] for r in rows if key in r["checks"]]
        return (sum(vals), len(vals))

    return {
        "runs": len(rows),
        "cases": len(by_case),
        "pass": sum(r["passed"] for r in rows),
        "metrics": {
            k: rate(k)
            for k in [
                "outcome",
                "product",
                "retrieval_hit",
                "citation_hit",
                "retrieval_all",
                "actions",
                "forbidden",
            ]
        },
        "mean_supported_ratio": round(statistics.mean(ratios), 3) if ratios else None,
        "verifier_caught": sum(r["verifier_caught"] for r in rows),
        "latency_mean": round(statistics.mean(lat), 2) if lat else 0,
        "latency_p95": round(sorted(lat)[math.ceil(len(lat) * 0.95) - 1], 2) if lat else 0,
        "cost_total": round(sum(r["cost_usd"] for r in rows), 4),
        "cost_per_run": round(sum(r["cost_usd"] for r in rows) / len(rows), 5) if rows else 0,
        "tokens_in": sum(r["input_tokens"] for r in rows),
        "tokens_out": sum(r["output_tokens"] for r in rows),
        "consistency": round(statistics.mean(consistency.values()), 3) if consistency else None,
        "inconsistent_cases": [c for c, v in consistency.items() if v < 1],
    }


def render_report(rows: list[dict], summary: dict, meta: dict) -> str:
    L = [
        f"# Evaluation report: {meta['timestamp']}",
        "",
        (
            f"Context config **{meta['context']}**, repeats {meta['repeats']}, models "
            f"`{config.FAST_MODEL}` (classify/route) and `{config.STRONG_MODEL}` (draft/verify). "
            f"Cost uses the prices in .env."
        ),
        "",
        "## Summary",
        "",
        "| Metric | Result |",
        "|---|---|",
        f"| Cases passed | {summary['pass']}/{summary['runs']} ({_pct(summary['pass'], summary['runs'])}) |",
    ]
    names = {
        "outcome": "Correct outcome (answer/clarify/abstain/escalate)",
        "product": "Classification accuracy",
        "retrieval_hit": "Retrieval hit (expected section retrieved)",
        "citation_hit": "Citation hit (answer cites expected section)",
        "retrieval_all": "Multi-section retrieval",
        "actions": "Dynamic routing used expected tool",
        "forbidden": "No forbidden content (injection / false premise)",
    }
    for k, (n, d) in summary["metrics"].items():
        if d:
            L.append(f"| {names[k]} | {n}/{d} ({_pct(n, d)}) |")
    L += [
        f"| Mean supported-claim ratio (answered) | {summary['mean_supported_ratio']} |",
        f"| Runs where the verifier forced a redraft/replan | {summary['verifier_caught']} |",
        f"| Outcome consistency across repeats | {summary['consistency']} |",
        f"| Latency mean / p95 | {summary['latency_mean']}s / {summary['latency_p95']}s |",
        f"| Cost total / per run | ${summary['cost_total']} / ${summary['cost_per_run']} |",
        f"| Tokens in / out | {summary['tokens_in']:,} / {summary['tokens_out']:,} |",
        "",
    ]

    L += ["## By category", "", "| Category | Passed |", "|---|---|"]
    cats = defaultdict(list)
    for r in rows:
        cats[r["category"]].append(r["passed"])
    for c, v in sorted(cats.items()):
        L.append(f"| {c} | {sum(v)}/{len(v)} |")

    L += [
        "",
        "## Cases",
        "",
        "| Case | Workflow | Category | Expected | Actual | Pass | Supported | Latency | Cost |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        L.append(
            f"| {r['id']} | {r['workflow']} | {r['category']} | {'/'.join(r['expected'] or [])} "
            f"| {r['actual']} | {'yes' if r['passed'] else '**no**'} "
            f"| {r['supported_ratio'] if r['supported_ratio'] is not None else 'n/a'} "
            f"| {r['latency_s']}s | ${r['cost_usd']:.4f} |"
        )

    fails = [r for r in rows if not r["passed"]]
    L += ["", f"## Failures ({len(fails)})", ""]
    for r in fails:
        L += [
            f"### {r['id']} ({r['category']})",
            "",
            f"- Path: {' → '.join(r['path'])}",
            *[f"- {x}" for x in r["reasons"]],
            *[f"- Policy override: {o}" for o in r["overrides"]],
            "- Response:",
            "",
            *[f"  > {line}".rstrip() for line in _clip(r["response"], 400).splitlines()],
            "",
        ]

    scores = sorted(r["best_reg_score"] for r in rows if r["best_reg_score"])
    oos = sorted(
        r["best_reg_score"] for r in rows if r["category"] == "out_of_scope" and r["best_reg_score"]
    )
    L += [
        "## Retrieval score calibration",
        "",
        f"Current floor REG_MIN_SCORE = {config.REG_MIN_SCORE}.",
        "",
    ]
    if scores:
        L.append(
            f"- Best regulation score per run: min {scores[0]:.3f}, median "
            f"{statistics.median(scores):.3f}, max {scores[-1]:.3f}"
        )
    if oos:
        L.append(
            f"- Out-of-scope runs that reached retrieval: {', '.join(f'{s:.3f}' for s in oos)}"
        )
    inscope = sorted(r["best_reg_score"] for r in rows
                    if r["category"] != "out_of_scope" and r["best_reg_score"])
    if inscope:
        L.append(f"- Lowest best score among in-scope runs: {inscope[0]:.3f} "
            f"(floor {config.REG_MIN_SCORE} should stay below this)")
    return "\n".join(L) + "\n"


def write_results(rows, summary, meta) -> Path:
    # "2026-11-07, 16:00" -> "2026-11-07_16-00" (no commas, spaces or colons in paths)
    stamp = meta["timestamp"].replace(", ", "_").replace(":", "-")
    suite = Path(meta.get("cases_file", "cases.yaml")).stem
    suffix = "" if suite == "cases" else f"_{suite}"
    out = RESULTS_DIR / f"{stamp}_{meta['context']}{suffix}"
    out.mkdir(parents=True, exist_ok=True)
    (out / "results.json").write_text(
        json.dumps({"meta": meta, "summary": summary, "rows": rows}, indent=2, default=str)
    )
    report = render_report(rows, summary, meta)
    (out / "report.md").write_text(report)
    if not suffix:  # latest.md always shows the development suite
        shutil.copy(out / "report.md", RESULTS_DIR / "latest.md")
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--context", default="lean", choices=["lean", "rich"])
    ap.add_argument("--repeats", type=int, default=1)
    ap.add_argument("--workflow", default="all", choices=["all", "static", "dynamic"])
    ap.add_argument("--category")
    ap.add_argument("--ids", help="comma-separated case ids")
    ap.add_argument("--fail-under", type=float, help="exit 1 if pass rate is below this")
    ap.add_argument("--cases", default=str(CASES_PATH), help="case file (default: eval/cases.yaml)")
    args = ap.parse_args(argv)

    from runtime import build_runtime

    cases = load_cases(
        Path(args.cases),
        ids=set(args.ids.split(",")) if args.ids else None,
        workflow=args.workflow,
        category=args.category,
    )
    rt = build_runtime(context=args.context)
    print(f"Running {len(cases)} cases x {args.repeats} ({args.context} context)")
    rows = run_cases(rt, cases, repeats=args.repeats)
    summary = summarize(rows)
    meta = {
        "timestamp": datetime.now().strftime("%Y-%m-%d, %H:%M"),
        "context": args.context,
        "repeats": args.repeats,
        "fast_model": config.FAST_MODEL,
        "strong_model": config.STRONG_MODEL,
        "reg_min_score": config.REG_MIN_SCORE,
        "cases_file": Path(args.cases).name,
    }
    out = write_results(rows, summary, meta)
    rate = summary["pass"] / summary["runs"] if summary["runs"] else 0
    print(
        f"\nPassed {summary['pass']}/{summary['runs']} ({rate:.0%}). "
        f"Cost ${summary['cost_total']}. Report: {out / 'report.md'}"
    )
    if args.fail_under is not None and rate < args.fail_under:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
