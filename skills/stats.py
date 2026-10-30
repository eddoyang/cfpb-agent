"""Stats skill: the model fills a StatsRequest; we build parameterised SQL from a
whitelist. The model never writes SQL, so there is no injection surface and the
same request always produces the same query."""
from __future__ import annotations

from skills.schemas import StatsRequest

GROUP_COLUMNS = {
    "product": "product",
    "issue": "issue",
    "company": "company",
    "state": "state",
    "company_response": "company_response",
    "month": "to_char(date_trunc('month', date_received), 'YYYY-MM')",
}
METRICS = {
    "count": "count(*)",
    "timely_rate": "round(avg(CASE WHEN timely THEN 1.0 ELSE 0.0 END) * 100, 1)",
    "relief_rate": ("round(avg(CASE WHEN company_response ILIKE '%%relief%%' "
                    "THEN 1.0 ELSE 0.0 END) * 100, 1)"),
}


def build_sql(req: StatsRequest) -> tuple[str, dict]:
    where, params = [], {}
    for field, col in [("product_keyword", "product"), ("issue_keyword", "issue"),
                       ("company_keyword", "company")]:
        val = getattr(req, field)
        if val:
            where.append(f"{col} ILIKE %({field})s")
            params[field] = f"%{val}%"
    if req.state:
        where.append("state = %(state)s")
        params["state"] = req.state.upper()[:2]
    if req.date_from:
        where.append("date_received >= %(date_from)s")
        params["date_from"] = req.date_from
    if req.date_to:
        where.append("date_received <= %(date_to)s")
        params["date_to"] = req.date_to
    where_sql = ("WHERE " + " AND ".join(where)) if where else ""
    metric = METRICS[req.metric]

    if req.group_by == "none":
        sql = f"SELECT {metric} AS value, count(*) AS n FROM complaints {where_sql}"
    else:
        col = GROUP_COLUMNS[req.group_by]
        order = "grp" if req.group_by == "month" else "value DESC"
        sql = (f"SELECT {col} AS grp, {metric} AS value, count(*) AS n FROM complaints "
               f"{where_sql} GROUP BY grp ORDER BY {order} LIMIT %(limit)s")
        params["limit"] = req.limit
    return sql, params


def _render_table(req: StatsRequest, rows: list[dict]) -> str:
    label = {"count": "complaints", "timely_rate": "% timely responses",
             "relief_rate": "% closed with relief"}[req.metric]
    filters = {k: v for k, v in req.model_dump().items()
               if k not in {"metric", "group_by", "limit"} and v}
    head = (f"Complaint statistics from our CFPB sample (not the full national database). "
            f"Metric: {label}. Grouped by: {req.group_by}. Filters: {filters or 'none'}.")
    if not rows:
        return head + "\nNo matching complaints."
    lines = [f"- {r.get('grp', 'all')}: {r['value']} (n={r['n']})" for r in rows]
    return head + "\n" + "\n".join(lines)


def run_stats(rt, req: StatsRequest, evidence_index: int = 1) -> dict:
    sql, params = build_sql(req)
    rows = rt.store.run_readonly(sql, params)
    return {
        "evidence": [{
            "id": f"S-{evidence_index}",
            "kind": "stats",
            "citation": "Aggregate over ingested CFPB complaints",
            "text": _render_table(req, rows),
            "score": 1.0,
            "section": None,
            "source_url": "https://www.consumerfinance.gov/data-research/consumer-complaints/",
            "meta": {"sql": sql, "params": {k: str(v) for k, v in params.items()},
                     "rows": len(rows)},
        }],
        "n_rows": len(rows),
        "sufficient": bool(rows) and any((r.get("n") or 0) > 0 for r in rows),
    }
