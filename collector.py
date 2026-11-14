from kubernetes import client, config


def parse_cpu(value: str) -> float:
    """'250m' -> 0.25 cores, '2' -> 2.0 cores, '100n' -> nanocores"""
    if value.endswith("n"):
        return int(value[:-1]) / 1_000_000_000
    if value.endswith("u"):
        return int(value[:-1]) / 1_000_000
    if value.endswith("m"):
        return int(value[:-1]) / 1000
    return float(value)


def parse_memory(value: str) -> float:
    """Returns MiB. Handles Ki, Mi, Gi, and plain bytes."""
    units = {"Ki": 1 / 1024, "Mi": 1, "Gi": 1024, "Ti": 1024 * 1024}
    for suffix, factor in units.items():
        if value.endswith(suffix):
            return float(value[: -len(suffix)]) * factor
    return float(value) / (1024 * 1024)


def load_cluster():
    try:
        config.load_incluster_config()   # running inside the cluster
    except config.ConfigException:
        config.load_kube_config()        # running from your laptop


def collect(namespace: str | None = None) -> list[dict]:
    load_cluster()
    core = client.CoreV1Api()
    custom = client.CustomObjectsApi()

    pods = (core.list_namespaced_pod(namespace) if namespace
            else core.list_pod_for_all_namespaces()).items

    # metrics-server data
    if namespace:
        metrics = custom.list_namespaced_custom_object(
            "metrics.k8s.io", "v1beta1", namespace, "pods")
    else:
        metrics = custom.list_cluster_custom_object(
            "metrics.k8s.io", "v1beta1", "pods")

    usage = {}
    for item in metrics.get("items", []):
        key = (item["metadata"]["namespace"], item["metadata"]["name"])
        for c in item["containers"]:
            usage[(*key, c["name"])] = {
                "cpu": parse_cpu(c["usage"]["cpu"]),
                "mem": parse_memory(c["usage"]["memory"]),
            }

    rows = []
    for pod in pods:
        if pod.status.phase != "Running":
            continue
        owner = pod.metadata.owner_references[0].name if pod.metadata.owner_references else pod.metadata.name
        for c in pod.spec.containers:
            req = (c.resources.requests or {})
            lim = (c.resources.limits or {})
            u = usage.get((pod.metadata.namespace, pod.metadata.name, c.name), {"cpu": 0, "mem": 0})
            rows.append({
                "namespace": pod.metadata.namespace,
                "workload": owner,
                "pod": pod.metadata.name,
                "container": c.name,
                "cpu_request": parse_cpu(req["cpu"]) if "cpu" in req else None,
                "mem_request": parse_memory(req["memory"]) if "memory" in req else None,
                "cpu_limit": parse_cpu(lim["cpu"]) if "cpu" in lim else None,
                "mem_limit": parse_memory(lim["memory"]) if "memory" in lim else None,
                "cpu_usage": u["cpu"],
                "mem_usage": u["mem"],
            })
    return rows