"""Command-line demo (backup for the Streamlit app).

python cli.py triage "Someone charged $500 to my credit card..."     # static workflow
python cli.py triage --complaint-id 8123456 --approve                 # real complaint + human approval
python cli.py triage --sample                                         # random complaint from the DB
python cli.py ask "How often can a debt collector call?"              # dynamic workflow
python cli.py chat                                                    # dynamic, multi-turn
python cli.py graph                                                   # Mermaid diagrams of both graphs
"""

from __future__ import annotations

import argparse
import textwrap

from graphs.runner import resume_static, run_dynamic, run_static
from runtime import build_runtime

W = 96


def show(r: dict) -> None:
    print("\n" + "=" * W)
    print(
        f"OUTCOME: {r['outcome'].upper()}   workflow={r['workflow']}  context={r['context_config']}"
    )
    print("-" * W)
    print("PATH:")
    for t in r["trace"]:
        print(f"  {t['node']:<24} {t['ms']:>6} ms  {t['detail'][: W - 40]}")
    for o in r.get("overrides", []):
        print(f"  policy override: {o}")
    if r.get("classification"):
        c = r["classification"]
        print(
            f"\nCLASSIFIED: {c['product']} | {c['issue']} | priority {c['priority']} | parts {c['regulation_parts']}"
        )
    print("\nRESPONSE:")
    print(textwrap.fill(r["response"] or "(none)", W, initial_indent="  ", subsequent_indent="  "))
    if r["citations"]:
        print("\nCITATIONS:")
        for c in r["citations"]:
            print(f"  [{c['id']}] {c['citation'][:70]}  (score {c['score']})")
            if c.get("text"):
                passage = " ".join(c["text"].split())
                print(textwrap.fill(passage[:400] + ("..." if len(passage) > 400 else ""),
                                    W, initial_indent="      ", subsequent_indent="      "))
    v = r.get("verification")
    if v:
        print(
            f"\nVERIFICATION: {'PASS' if v['passed'] else 'FAIL'}  supported={v['supported_ratio']}"
        )
        for i in (v["issues"] + v.get("advisories", []))[:5]:
            print(f"  - {i[: W - 4]}")
    if r.get("escalation_reason"):
        print(f"\nESCALATION REASON: {r['escalation_reason'][:300]}")
    u = r["usage"]
    print(
        f"\nUSAGE: {u['llm_calls']} LLM calls, {u['input_tokens']:,} in / {u['output_tokens']:,} out tokens, "
        f"${u['cost_usd']:.4f}, {r['latency_s']}s wall clock"
    )
    print("=" * W)


def main():
    ap = argparse.ArgumentParser(description="CFPB complaint agent demo")
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("triage", help="static workflow")
    t.add_argument("text", nargs="?")
    t.add_argument("--complaint-id", type=int)
    t.add_argument("--sample", action="store_true")
    t.add_argument("--approve", action="store_true", help="pause for human approval")
    for p in (t, sub.add_parser("ask", help="dynamic workflow"), sub.add_parser("chat")):
        p.add_argument("--context", default="lean", choices=["lean", "rich"])
    sub.choices["ask"].add_argument("question")
    sub.add_parser("graph", help="print Mermaid diagrams")
    args = ap.parse_args()

    if args.cmd == "graph":
        from graphs.dynamic import build_dynamic_graph
        from graphs.static import build_static_graph
        from tests.fakes import make_rt

        rt = make_rt(script=None)
        print("%% static\n" + build_static_graph(rt).get_graph().draw_mermaid())
        print("%% dynamic\n" + build_dynamic_graph(rt).get_graph().draw_mermaid())
        return

    rt = build_runtime(context=args.context, require_approval=getattr(args, "approve", False))

    if args.cmd == "triage":
        exclude = None
        text = args.text
        if args.complaint_id or args.sample:
            row = (
                rt.store.get_complaint(args.complaint_id)
                if args.complaint_id
                else rt.store.random_complaints(1)[0]
            )
            if not row:
                raise SystemExit(f"Complaint {args.complaint_id} not found")
            text, exclude = row["narrative"], row["complaint_id"]
            print(f"Complaint {row['complaint_id']} ({row['product']} / {row['issue']}):")
            print(textwrap.fill(text[:1200], W, initial_indent="  ", subsequent_indent="  "))
        if not text:
            raise SystemExit("Give complaint text, --complaint-id or --sample")
        r = run_static(rt, text, exclude_complaint_id=exclude)
        if r["pending_review"]:
            show(r)
            ans = input("\nApprove this reply? [y]es / [n]o / [e]dit: ").strip().lower()
            edited = input("Paste the edited reply:\n") if ans.startswith("e") else None
            r = resume_static(
                rt,
                r["thread_id"],
                approved=ans[:1] in {"y", "e"},
                edited_response=edited,
                reviewer="cli user",
            )
        show(r)
    elif args.cmd == "ask":
        show(run_dynamic(rt, args.question))
    else:
        history: list[dict] = []
        print("Ask about Reg E/F/Z or the complaint data. Empty line to quit.")
        while q := input("\nyou> ").strip():
            r = run_dynamic(rt, q, history=history)
            show(r)
            history += [
                {"role": "user", "content": q},
                {"role": "assistant", "content": r["response"]},
            ]


if __name__ == "__main__":
    main()
