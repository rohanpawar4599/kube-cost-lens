import json

from rich.console import Console
from rich.table import Table


def print_table(findings: list[dict], pricing: dict) -> float:
    """Print a Rich table of findings. Returns total monthly waste in USD."""
    from pricing import monthly_cost

    console = Console()
    table = Table(title="kube-cost-lens — Waste Report")

    for col in [
        "Namespace",
        "Workload",
        "Container",
        "CPU req→rec",
        "Mem req→rec",
        "Issues",
        "Waste/mo",
    ]:
        table.add_column(col)

    total_waste = 0.0

    for f in findings:
        waste = monthly_cost(f["cpu_waste"], f["mem_waste"], pricing)
        total_waste += waste
        table.add_row(
            f["namespace"],
            f["workload"],
            f["container"],
            f'{f["cpu_request"]}→{f["recommended_cpu"]}',
            f'{f["mem_request"]}→{f["recommended_mem"]}Mi',
            ", ".join(f["issues"]),
            f"${waste:.2f}",
        )

    console.print(table)

    inr = total_waste * pricing["currency_rate"]
    console.print(
        f"\n[bold red]Estimated recoverable spend: "
        f"${total_waste:,.2f}/month (~₹{inr:,.0f})[/]"
    )

    return total_waste


def print_json(findings: list[dict]) -> None:
    """Print findings as formatted JSON to stdout."""
    print(json.dumps(findings, indent=2, default=str))