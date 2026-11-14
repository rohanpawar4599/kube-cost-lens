import yaml


def generate_patch(finding: dict) -> str:
    patch = {
        "spec": {"template": {"spec": {"containers": [{
            "name": finding["container"],
            "resources": {
                "requests": {
                    "cpu": f'{int(finding["recommended_cpu"] * 1000)}m',
                    "memory": f'{int(finding["recommended_mem"])}Mi',
                },
                "limits": {
                    "cpu": f'{int(finding["recommended_cpu"] * 2000)}m',
                    "memory": f'{int(finding["recommended_mem"] * 1.5)}Mi',
                },
            },
        }]}}}
    }
    return (f"# kubectl patch deployment {finding['workload']} -n {finding['namespace']} "
            f"--patch-file this.yaml\n" + yaml.safe_dump(patch))