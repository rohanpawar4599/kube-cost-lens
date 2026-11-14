import argparse
import os

from collector import collect
from analyzer import analyze
from pricing import load_pricing
from patcher import generate_patch
from reporter import print_table, print_json


def main():
    ap = argparse.ArgumentParser(
        description="Find wasted spend in a Kubernetes cluster"
    )
    ap.add_argument("--namespace", "-n")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--patches", help="directory to write YAML patches")
    args = ap.parse_args()

    pricing = load_pricing()
    findings = analyze(collect(args.namespace))

    print_table(findings, pricing)

    if args.json:
        print_json(findings)

    if args.patches:
        os.makedirs(args.patches, exist_ok=True)
        for f in findings:
            path = os.path.join(
                args.patches,
                f'{f["namespace"]}-{f["workload"]}-{f["container"]}.yaml'
            )
            with open(path, "w") as fh:
                fh.write(generate_patch(f))


if __name__ == "__main__":
    main()