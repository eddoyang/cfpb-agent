"""Compare two context configurations on one representative query.

    python -m experiments.context_compare
    python -m experiments.context_compare --workflow static --query "..." --repeats 3

For each config it records: outcome, evidence items in context, supported-claim ratio,
whether the expected sections were cited, input/output tokens, cost and latency.
A short prior conversation is included so the history setting (summary vs full)
actually matters. Results go to experiments/results/context_compare_<ts>.md.
"""

from __future__ import annotations

import argparse
import json
import statistics
from datetime import datetime
from pathlib import Path

from context import get_context_config
from graphs.runner import run_dynamic, run_static
from runtime import build_runtime

DEFAULT_QUERY = (
    "A customer says a thief made $700 of card purchases and also pulled money "
    "from their checking account by debit card. What liability limits apply to "
    "each, what deadlines matter, and how common are complaints like this in our data?"
)
DEFAULT_SECTIONS = ["1026.12", "1005.6", "1005.11", "1026.13"]
HISTORY = [
    {"role": "user", "content": "What is Regulation E?"},
    {
        "role": "assistant",
        "content": "Regulation E (12 CFR 1005) implements the Electronic Fund "
        "Transfer Act: debit cards, ATM transfers, prepaid accounts and remittances.",
    },
    {"role": "user", "content": "And Regulation Z?"},
    {
        "role": "assistant",
        "content": "Regulation Z (12 CFR 1026) implements the Truth in Lending "
        "Act, including credit card rules on unauthorized use and billing errors.",
    },
    {"role": "user", "content": "Thanks. Keep answers short and cite sections."},
    {"role": "assistant", "content": "Will do."},
]
OUT_DIR = Path(__file__).parent / "results"


def run_once(config_name: str, workflow: str, query: str, sections: list[str]) -> dict:
    rt = build_runtime(context=config_name)
    if workflow == "dynamic":
        r = run_dynamic(rt, query, history=HISTORY)
    else:
        r = run_static(rt, query)
    cited = {c["id"][2:].split("#")[0] for c in r["citations"] if c["id"].startswith("R-")}
    return {
        "config": config_name,
        "outcome": r["outcome"],
        "evidence_retrieved": len(r["retrieved_ids"]),
        "evidence_in_context": len(r["context_ids"]),
        "supported_ratio": (r["verification"] or {}).get("supported_ratio"),
        "n_claims": (r["verification"] or {}).get("n_claims"),
        "expected_cited": sorted(cited & set(sections)),
        "input_tokens": r["usage"]["input_tokens"],
        "output_tokens": r["usage"]["output_tokens"],
        "cost_usd": r["usage"]["cost_usd"],
        "latency_s": r["latency_s"],
        "llm_calls": r["usage"]["llm_calls"],
        "path": " → ".join(r["path"]),
        "response": r["response"],
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--workflow", default="dynamic", choices=["dynamic", "static"])
    ap.add_argument("--query", default=DEFAULT_QUERY)
    ap.add_argument("--sections", default=",".join(DEFAULT_SECTIONS))
    ap.add_argument("--repeats", type=int, default=2)
    ap.add_argument("--configs", default="lean,rich")
    args = ap.parse_args(argv)
    sections = args.sections.split(",")

    runs = {}
    for name in args.configs.split(","):
        runs[name] = []
        for i in range(args.repeats):
            print(f"{name} run {i + 1}/{args.repeats} ...")
            runs[name].append(run_once(name, args.workflow, args.query, sections))

    def mean(name, key):
        vals = [r[key] for r in runs[name] if r[key] is not None]
        return round(statistics.mean(vals), 3) if vals else None

    L = [
        f"# Context comparison ({datetime.now():%Y-%m-%d %H:%M})",
        "",
        f"Workflow: {args.workflow}. Query: _{args.query}_",
        "",
        f"Expected sections: {sections}. Repeats per config: {args.repeats}.",
        "",
        "| Metric | " + " | ".join(runs) + " |",
        "|---|" + "---|" * len(runs),
    ]
    for name in runs:
        c = get_context_config(name)
        runs[name][0]["_desc"] = (
            f"top-k regs {c.reg_top_k}, cases {c.case_top_k}, evidence "
            f"budget {c.max_evidence_tokens} tok, history {c.history_mode}"
        )
    L.append("| Settings | " + " | ".join(runs[n][0]["_desc"] for n in runs) + " |")
    for label, key in [
        ("Evidence items in context (mean)", "evidence_in_context"),
        ("Input tokens (mean)", "input_tokens"),
        ("Output tokens (mean)", "output_tokens"),
        ("Cost USD (mean)", "cost_usd"),
        ("Latency s (mean)", "latency_s"),
        ("LLM calls (mean)", "llm_calls"),
        ("Supported-claim ratio (mean)", "supported_ratio"),
        ("Claims per answer (mean)", "n_claims"),
    ]:
        L.append(f"| {label} | " + " | ".join(str(mean(n, key)) for n in runs) + " |")
    L.append(
        "| Outcomes | " + " | ".join(", ".join(r["outcome"] for r in runs[n]) for n in runs) + " |"
    )
    L.append(
        "| Expected sections cited (run 1) | "
        + " | ".join(", ".join(runs[n][0]["expected_cited"]) or "none" for n in runs)
        + " |"
    )
    for n in runs:
        L += ["", f"## {n}: run 1", "", f"Path: {runs[n][0]['path']}", "", runs[n][0]["response"]]
    L += [
        "",
        "## Interpretation",
        "",
        "- Quality: did the rich config cite more of the expected sections, or just add noise?",
        "- Cost/latency: how much more did rich cost per answer, and was it worth it?",
        "- Recommendation: which config would you deploy, and for which request types?",
    ]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    (OUT_DIR / f"context_compare_{stamp}.md").write_text("\n".join(L) + "\n")
    (OUT_DIR / f"context_compare_{stamp}.json").write_text(json.dumps(runs, indent=2, default=str))
    print("\n".join(L[:22]))
    print(f"\nWrote {OUT_DIR / f'context_compare_{stamp}.md'}")


if __name__ == "__main__":
    main()
