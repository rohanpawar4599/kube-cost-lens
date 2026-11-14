HEADROOM = 1.3          # recommend usage * 1.3 (30% safety buffer)
WASTE_THRESHOLD = 0.5   # flag if using < 50% of request
IDLE_CPU = 0.005        # < 5 millicores = effectively idle


def analyze(rows: list[dict]) -> list[dict]:
    findings = []
    for r in rows:
        issues = []

        if r["cpu_request"] is None or r["mem_request"] is None:
            issues.append("MISSING_REQUESTS")      # scheduler can't bin-pack properly
        if r["cpu_limit"] is None or r["mem_limit"] is None:
            issues.append("MISSING_LIMITS")        # noisy-neighbour risk

        if r["cpu_request"] and r["cpu_usage"] < r["cpu_request"] * WASTE_THRESHOLD:
            issues.append("CPU_OVERPROVISIONED")
        if r["mem_request"] and r["mem_usage"] < r["mem_request"] * WASTE_THRESHOLD:
            issues.append("MEM_OVERPROVISIONED")
        if r["cpu_usage"] < IDLE_CPU:
            issues.append("IDLE_WORKLOAD")

        if not issues:
            continue

        rec_cpu = max(round(r["cpu_usage"] * HEADROOM, 3), 0.01)
        rec_mem = max(round(r["mem_usage"] * HEADROOM), 32)

        findings.append({
            **r,
            "issues": issues,
            "recommended_cpu": rec_cpu,
            "recommended_mem": rec_mem,
            "cpu_waste": max((r["cpu_request"] or 0) - rec_cpu, 0),
            "mem_waste": max((r["mem_request"] or 0) - rec_mem, 0),
        })
    return findings