"""Streamlit demo:  streamlit run app.py

Tab 1 runs the STATIC triage workflow (with optional human approval).
Tab 2 runs the DYNAMIC analyst workflow as a multi-turn chat.
Tab 3 shows the latest evaluation report.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st
import yaml

from graphs.runner import resume_static, run_dynamic, run_static
from runtime import build_runtime

st.set_page_config(page_title="Complaint triage agents", layout="wide")

OUTCOME_STYLE = {
    "answer": ("Answered", "green"),
    "clarify": ("Needs clarification", "blue"),
    "abstain": ("Abstained", "gray"),
    "escalate": ("Escalated to a human", "orange"),
    "pending_review": ("Waiting for human approval", "violet"),
    "rejected": ("Rejected by reviewer", "red"),
}
CASES = yaml.safe_load((Path(__file__).parent / "eval" / "cases.yaml").read_text())


# ---------------------------------------------------------------- runtime
with st.sidebar:
    st.header("Settings")
    context = st.radio(
        "Context configuration",
        ["lean", "rich"],
        help="lean: top-3 chunks, 2.5k-token evidence budget, summarised history. "
        "rich: top-10, 9k budget, full history.",
    )
    approval = st.toggle("Require human approval", value=True)
    st.caption("Models and thresholds are set in config.py.")

key = f"rt-{context}-{approval}"
if key not in st.session_state:
    try:
        st.session_state[key] = build_runtime(context=context, require_approval=approval)
    except Exception as e:  # noqa: BLE001
        st.error(f"Could not start the runtime: {e}")
        st.stop()
rt = st.session_state[key]


# ---------------------------------------------------------------- display
def show_result(r: dict, show_response: bool = True) -> None:
    label, color = OUTCOME_STYLE.get(r["outcome"], (r["outcome"], "gray"))
    st.markdown(f"**Outcome:** :{color}[{label}]")
    if show_response and r["response"] and not r["pending_review"]:
        st.markdown(r["response"])
    u = r["usage"]
    cols = st.columns(4)
    cols[0].metric("Latency", f"{r['latency_s']}s")
    cols[1].metric("Est. cost", f"${u['cost_usd']:.4f}")
    cols[2].metric("LLM calls", u["llm_calls"])
    cols[3].metric("Tokens in / out", f"{u['input_tokens']:,} / {u['output_tokens']:,}")
    if r.get("escalation_reason"):
        st.warning(r["escalation_reason"])

    with st.expander("Agent path", expanded=True):
        st.caption(" → ".join(r["path"]))
        st.dataframe(pd.DataFrame(r["trace"]), hide_index=True, use_container_width=True)
        for o in r.get("overrides", []):
            st.info(f"Policy override: {o}")
    if r["citations"]:
        with st.expander(f"Citations ({len(r['citations'])})"):
            for c in r["citations"]:
                st.markdown(f"- `{c['id']}` [{c['citation']}]({c['url']}) · score {c['score']}")
    if r.get("verification"):
        v = r["verification"]
        with st.expander(
            f"Verification: {'PASS' if v['passed'] else 'FAIL'} (supported {v['supported_ratio']})"
        ):
            for i in v["issues"] + v.get("advisories", []):
                st.markdown(f"- {i}")
            if v["verdicts"]:
                st.dataframe(pd.DataFrame(v["verdicts"]), hide_index=True)
    if r.get("classification"):
        with st.expander("Classification"):
            st.json(r["classification"])
    if r.get("errors"):
        with st.expander("Errors"):
            for e in r["errors"]:
                st.code(e)


tab1, tab2, tab3 = st.tabs(["Complaint triage (static)", "Analyst Q&A (dynamic)", "Evaluation"])

# ---------------------------------------------------------------- static
with tab1:
    st.subheader("Complaint triage: fixed pipeline")
    st.caption(
        "classify → retrieve regulations → similar cases → draft → verify (≤2 redrafts) → human approval"
    )
    samples = {
        f"{c['id']} ({c['category']})": c["input"] for c in CASES if c["workflow"] == "static"
    }
    choice = st.selectbox(
        "Example complaint",
        ["(write your own)", "(random complaint from the database)"] + list(samples),
    )
    default = samples.get(choice, "")
    exclude = None
    if choice == "(random complaint from the database)":
        if st.button("Draw a complaint"):
            row = rt.store.random_complaints(1)[0]
            st.session_state["random_complaint"] = row
        row = st.session_state.get("random_complaint")
        if row:
            default, exclude = row["narrative"], row["complaint_id"]
            st.caption(f"Complaint {row['complaint_id']}: {row['product']} / {row['issue']}")
    text = st.text_area("Complaint", value=default, height=160)

    if st.button("Run triage", type="primary", disabled=not text.strip()):
        with st.spinner("Agents working..."):
            st.session_state["static_result"] = run_static(rt, text, exclude_complaint_id=exclude)

    r = st.session_state.get("static_result")
    if r:
        show_result(r)
        if r["pending_review"]:
            st.markdown("#### Human review")
            edited = st.text_area(
                "Draft reply (edit before approving if needed)", value=r["response"], height=220
            )
            note = st.text_input("Reviewer note")
            c1, c2 = st.columns(2)
            if c1.button("Approve and send", type="primary"):
                st.session_state["static_result"] = resume_static(
                    rt,
                    r["thread_id"],
                    approved=True,
                    edited_response=edited if edited != r["response"] else None,
                    reviewer="demo reviewer",
                    note=note,
                )
                st.rerun()
            if c2.button("Reject"):
                st.session_state["static_result"] = resume_static(
                    rt, r["thread_id"], approved=False, reviewer="demo reviewer", note=note
                )
                st.rerun()

# ---------------------------------------------------------------- dynamic
with tab2:
    st.subheader("Analyst Q&A: supervisor-routed agents")
    st.caption(
        "The supervisor picks regulation search, similar-complaint search or statistics, "
        "re-plans if verification fails, and can clarify or abstain."
    )
    hist_key = f"chat-{context}"
    st.session_state.setdefault(hist_key, [])
    examples = [c["input"] for c in CASES if c["workflow"] == "dynamic"]
    pick = st.selectbox("Example question", ["(type below)"] + examples)
    if st.button("Clear conversation"):
        st.session_state[hist_key] = []

    for turn in st.session_state[hist_key]:
        with st.chat_message(turn["role"]):
            st.markdown(turn["content"])
            if turn.get("result"):
                show_result(turn["result"], show_response=False)

    q = st.chat_input("Ask about Regulation E, F, Z or the complaint data")
    if pick != "(type below)" and st.button("Ask the example question"):
        q = pick
    if q:
        history = [{"role": t["role"], "content": t["content"]} for t in st.session_state[hist_key]]
        with st.spinner("Supervisor planning..."):
            res = run_dynamic(rt, q, history=history)
        st.session_state[hist_key] += [
            {"role": "user", "content": q},
            {"role": "assistant", "content": res["response"], "result": res},
        ]
        st.rerun()

# ---------------------------------------------------------------- eval
with tab3:
    st.subheader("Evaluation")
    st.caption(
        "Run `python -m eval.harness` (add `--repeats 3` for reliability). "
        "The newest report appears here."
    )
    latest = Path(__file__).parent / "eval" / "results" / "latest.md"
    if latest.exists():
        st.markdown(latest.read_text())
    else:
        st.info("No evaluation results yet.")
