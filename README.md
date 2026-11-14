<p align="center">

&#x20; <h1 align="center">🔍 kube-cost-lens</h1>

&#x20; <p align="center">

&#x20;   <strong>Find wasted spend in your Kubernetes cluster in under 30 seconds.</strong>

&#x20; </p>

&#x20; <p align="center">

&#x20;   <img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python">

&#x20;   <img src="https://img.shields.io/badge/kubernetes-1.26+-326ce5.svg" alt="Kubernetes">

&#x20;   <img src="https://img.shields.io/badge/docker-ready-2496ed.svg" alt="Docker">

&#x20;   <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License">

&#x20; </p>

</p>



\---



\## The Problem



Most Kubernetes clusters run at \*\*20–40% CPU utilization\*\*

(\[Datadog Container Report 2024](https://www.datadoghq.com/container-report/),

\[CNCF FinOps Survey](https://www.cncf.io/reports/finops/)).



Why?



1\. Developers copy-paste resource requests from Stack Overflow

2\. Nobody revisits them after the initial deploy

3\. There's no easy way to see the gap between \*\*requested\*\* and \*\*actually used\*\*



The result: \*\*thousands of dollars per month\*\* in idle compute that nobody notices.



\---



\## What kube-cost-lens Does



```

┌─────────────────────────────────────────────────────────────────────┐

│                        kube-cost-lens                               │

│                                                                     │

│  ┌──────────┐    ┌──────────────┐    ┌───────────┐    ┌──────────┐  │

│  │Collector │───▶│  Analyzer    │───▶│  Pricer   │───▶│ Reporter │  │

│  │          │    │              │    │           │    │          │  │

│  │ K8s API  │    │ 5 rule types │    │ Cloud     │    │ Terminal │  │

│  │ + metrics│    │ per container│    │ node rates│    │ table +  │  │

│  │ -server  │    │              │    │           │    │ JSON     │  │

│  └──────────┘    └──────────────┘    └───────────┘    └──────────┘  │

│                        │                                  │         │

│                        ▼                                  ▼         │

│                 ┌──────────────┐                   ┌────────────┐   │

│                 │   Patcher    │                   │  $ Waste   │   │

│                 │              │                   │  Summary   │   │

│                 │ Ready-to-use │                   │            │   │

│                 │ YAML patches │                   │ ₹ / $ per  │   │

│                 │              │                   │ month      │   │

│                 └──────────────┘                   └────────────┘   │

└─────────────────────────────────────────────────────────────────────┘

```



In one command, it:



1\. \*\*Connects\*\* to your Kubernetes cluster (kubeconfig or in-cluster)

2\. \*\*Pulls\*\* every pod's resource requests from the K8s API

3\. \*\*Fetches\*\* actual CPU/memory usage from metrics-server

4\. \*\*Compares\*\* the two and flags 5 types of waste

5\. \*\*Calculates\*\* the dollar cost using real cloud node pricing

6\. \*\*Generates\*\* right-sized YAML patches you can review and apply



\---



\## Real Output



Scanned a test cluster with 4 deliberately over-provisioned deployments:



```

&#x20;             kube-cost-lens — Waste Report

┏━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓

┃ Namespace ┃ Workload     ┃ Container ┃ CPU req→rec ┃ Mem req→rec ┃ Issues                 ┃ Waste/mo ┃

┡━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩

│ demo      │ web-frontend │ nginx     │ 1.0→0.01    │ 512.0→32Mi  │ CPU\_OVERPROVISIONED,   │ $21.62   │

│           │              │           │             │             │ MEM\_OVERPROVISIONED    │          │

│ demo      │ api-server   │ api       │ 0.5→0.01    │ 256.0→32Mi  │ CPU\_OVERPROVISIONED,   │ $10.64   │

│           │              │           │             │             │ MEM\_OVERPROVISIONED    │          │

│ demo      │ cache        │ redis     │ 0.25→0.01   │ 128.0→32Mi  │ MISSING\_LIMITS,        │ $5.14    │

│           │              │           │             │             │ CPU\_OVERPROVISIONED    │          │

│ demo      │ bg-worker    │ worker    │ None→0.01   │ None→32Mi   │ MISSING\_REQUESTS,      │ $0.00    │

│           │              │           │             │             │ MISSING\_LIMITS         │          │

└───────────┴──────────────┴───────────┴─────────────┴─────────────┴────────────────────────┴──────────┘



Estimated recoverable spend: $69.66/month (\~₹5,851)

```



> \*\*Note:\*\* This is from a 4-app test cluster. Real production clusters with

> hundreds of workloads typically show \*\*$500–$5,000+/month\*\* in recoverable waste.



\---



\## Findings Detected



| Finding | Trigger | Why It Matters |

|---------|---------|----------------|

| `CPU\_OVERPROVISIONED` | Actual usage < 50% of request | Wasted compute, blocks bin-packing |

| `MEM\_OVERPROVISIONED` | Actual usage < 50% of request | Wasted memory, inflates node count |

| `MISSING\_REQUESTS` | No CPU/memory requests set | Scheduler can't place pods intelligently |

| `MISSING\_LIMITS` | No CPU/memory limits set | Noisy-neighbour risk, potential OOM |

| `IDLE\_WORKLOAD` | CPU usage < 5 millicores | Deployment may be dead/unused |



\---



\## Prerequisites



| Tool | Version | Why |

|------|---------|-----|

| Python | 3.10+ | Runtime |

| kubectl | 1.26+ | Cluster access |

| Kubernetes cluster | Any | Minikube, kind, EKS, GKE, AKS |

| metrics-server | Installed | Provides actual usage data |



\### Installing metrics-server (if not present)



\*\*Minikube:\*\*

```bash

minikube addons enable metrics-server

kubectl -n kube-system patch deployment metrics-server \\

&#x20; --type='json' \\

&#x20; -p='\[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]'

```



\*\*EKS / GKE / AKS:\*\*

```bash

kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

```



Verify it's working:

```bash

kubectl top nodes

```



\---



\## Installation



\### Option A: pip (local)



```bash

git clone https://github.com/rohanpawar4599/kube-cost-lens.git

cd kube-cost-lens

pip install -r requirements.txt

```



\### Option B: Docker



```bash

docker build -t kube-cost-lens:latest .

```



\---



\## Usage



\### Basic scan — all namespaces



```bash

python cli.py

```



\### Scan a specific namespace



```bash

python cli.py -n production

```



\### Generate right-sizing patches



```bash

python cli.py -n production --patches ./patches

```



This creates one YAML file per container in the `./patches/` directory. Each file

contains a `kubectl patch` command you can review and apply:



```bash

\# Review the patch

cat patches/production-api-server-api.yaml



\# Apply when ready (NOT automated — you decide)

kubectl patch deployment api-server -n production --patch-file patches/production-api-server-api.yaml

```



\### JSON output (for CI/CD pipelines)



```bash

python cli.py -n production --json > report.json

```



\### Docker usage



```bash

docker run --rm \\

&#x20; -v \~/.kube/config:/home/appuser/.kube/config:ro \\

&#x20; -e KUBECONFIG=/home/appuser/.kube/config \\

&#x20; kube-cost-lens:latest -n production --json

```



\---



\## How It Works — Step by Step



\### Step 1: Collection (`collector.py`)



```

K8s API ──▶ list all Running pods ──▶ extract requests/limits from pod spec

metrics-server ──▶ list pod metrics ──▶ extract actual CPU/memory usage

```



The collector joins these two data sources by `(namespace, pod, container)` tuple.



\### Step 2: Analysis (`analyzer.py`)



Each container is checked against 5 rules:



```python

if cpu\_usage < cpu\_request \* 0.5:    → CPU\_OVERPROVISIONED

if mem\_usage < mem\_request \* 0.5:    → MEM\_OVERPROVISIONED

if cpu\_request is None:              → MISSING\_REQUESTS

if cpu\_limit is None:                → MISSING\_LIMITS

if cpu\_usage < 0.005:                → IDLE\_WORKLOAD

```



Recommendations use a \*\*30% headroom\*\* buffer:

```python

recommended\_cpu = cpu\_usage \* 1.3   # never below 10m

recommended\_mem = mem\_usage \* 1.3   # never below 32Mi

```



\### Step 3: Pricing (`pricing.py`)



Waste is priced using a \*\*split-cost model\*\* from real cloud node rates:



```

Node: m5.large (ap-south-1) = $0.107/hr

&#x20; ├── 50% allocated to CPU  → $0.0268/core/hr

&#x20; └── 50% allocated to RAM  → $0.0067/GiB/hr



Monthly waste = (wasted\_cores × cpu\_rate + wasted\_gib × mem\_rate) × 730 hours

```



\### Step 4: Reporting (`reporter.py`)



Outputs a Rich terminal table + optional JSON for pipeline integration.



\### Step 5: Patching (`patcher.py`)



Generates strategic merge patches with right-sized values. \*\*Patches are never

auto-applied\*\* — point-in-time metrics can mislead, so human review is required.



\---



\## Configuration



\### Cloud Pricing



Edit `pricing/aws-ap-south-1.yaml` to match your region and node type:



```yaml

node\_type: m5.large          # change to your actual node type

node\_hourly\_usd: 0.107       # on-demand hourly rate

node\_vcpu: 2                 # vCPUs per node

node\_mem\_gib: 8              # RAM per node in GiB

usd\_to\_inr: 84               # currency conversion (optional)

```



Find your node pricing at:

\- \[AWS EC2 Pricing](https://aws.amazon.com/ec2/pricing/on-demand/)

\- \[GKE Pricing](https://cloud.google.com/kubernetes-engine/pricing)

\- \[AKS Pricing](https://azure.microsoft.com/en-us/pricing/details/kubernetes-service/)



\### Analysis Thresholds



In `analyzer.py`:



```python

HEADROOM = 1.3          # 30% safety buffer on recommendations

WASTE\_THRESHOLD = 0.5   # flag if using < 50% of request

IDLE\_CPU = 0.005        # < 5 millicores = effectively idle

```



\---



\## Project Structure



```

kube-cost-lens/

├── kube\_cost\_lens/

│   ├── \_\_init\_\_.py          # Package metadata

│   ├── collector.py         # K8s API + metrics-server data collection

│   ├── analyzer.py          # Waste detection rules (5 finding types)

│   ├── pricing.py           # Cloud node pricing → per-core/per-GB cost

│   ├── patcher.py           # Generates right-sized YAML patches

│   └── reporter.py          # Rich terminal table + JSON output

├── tests/

│   ├── conftest.py          # Shared test fixtures

│   ├── test\_collector.py    # CPU/memory parsing tests

│   ├── test\_analyzer.py     # Waste detection logic tests

│   ├── test\_pricing.py      # Cost calculation tests

│   └── test\_patcher.py      # YAML patch generation tests

├── demo/

│   └── overprovisioned-apps.yaml   # 4 sample workloads for testing

├── pricing/

│   └── aws-ap-south-1.yaml  # Cloud pricing configuration

├── cli.py                   # Entry point (argparse CLI)

├── Dockerfile               # Multi-stage Docker build

├── requirements.txt         # Python dependencies

├── LICENSE                  # MIT License

└── README.md                # This file

```



\---



\## Running Tests



```bash

pip install pytest

pytest tests/ -v

```



Expected: \*\*22 tests passing\*\* covering parsing, analysis, pricing, and patching.



\---



\## Roadmap



\- \[ ] \*\*Prometheus integration\*\* — 7-day P95 percentiles instead of point-in-time snapshots

\- \[ ] \*\*VPA comparison\*\* — show kube-cost-lens recommendations vs Vertical Pod Autoscaler

\- \[ ] \*\*Slack/Teams alerts\*\* — scheduled reports to your team channel

\- \[ ] \*\*Multi-cluster\*\* — scan all clusters in a kubeconfig context

\- \[ ] \*\*GKE/AKS pricing\*\* — built-in pricing tables for all major clouds

\- \[ ] \*\*Helm chart\*\* — deploy as a CronJob inside the cluster

\- \[ ] \*\*Web dashboard\*\* — Flask/Streamlit UI for non-CLI users



\---



\## Why Not Just Use VPA / Kubecost?



| Tool | Strength | Gap |

|------|----------|-----|

| \*\*VPA\*\* | Auto-right-sizes in real time | Can't show $ cost, needs days of data, risky in prod |

| \*\*Kubecost\*\* | Enterprise-grade dashboards | Paid for multi-cluster, heavy to install |

| \*\*kube-cost-lens\*\* | Instant, zero-install, shows $ | Point-in-time (Prometheus coming in v2) |



kube-cost-lens is the \*\*quick first scan\*\* — run it before investing in heavier tooling.



\---



\## Contributing



1\. Fork the repo

2\. Create a branch: `git checkout -b feature/my-improvement`

3\. Make changes + add tests

4\. Run `pytest tests/ -v`

5\. Submit a PR



\---



\## License



MIT — see \[LICENSE](LICENSE)



\---



\## Built By



\*\*Rohan Pawar\*\*

\- 🌐 \[LinkedIn](https://linkedin.com/in/rohan-pawar-0a1bb1314)

\- 💻 \[GitHub](https://github.com/rohanpawar4599)



Built to learn Kubernetes internals and solve a real infrastructure problem.

If this tool saved you money, a ⭐ on GitHub would mean a lot!

