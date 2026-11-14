import yaml

# Derived from an on-demand node type. Example: m5.large ap-south-1
# ~$0.107/hr, 2 vCPU, 8 GiB -> split cost 50/50 between CPU and memory.
def load_pricing(path="pricing/aws-ap-south-1.yaml") -> dict:
    with open(path) as f:
        p = yaml.safe_load(f)
    hourly = p["node_hourly_usd"]
    return {
        "cpu_core_hour": (hourly * 0.5) / p["node_vcpu"],
        "mem_gib_hour": (hourly * 0.5) / p["node_mem_gib"],
        "currency_rate": p.get("usd_to_inr", 84),
    }


def monthly_cost(cpu_cores: float, mem_mib: float, pricing: dict) -> float:
    hours = 730
    return (cpu_cores * pricing["cpu_core_hour"] +
            (mem_mib / 1024) * pricing["mem_gib_hour"]) * hours