# generate_metrics_json.py
import pandas as pd, json, sys

if len(sys.argv)!=4:
    print("Usage: generate_metrics_json.py logs.csv endpoint_metrics.csv metrics.json"); sys.exit(1)

logs_csv, ep_csv, out_json = sys.argv[1:]
df = pd.read_csv(logs_csv, parse_dates=['timestamp'])
λ = float(df.set_index('timestamp').resample('1S').size().mean())
avg_sys = float(df['latency'].mean())

ep = pd.read_csv(ep_csv)
nodes = [{
    "name": r.endpoint,
    "visit_ratio": float(r.visit_ratio),
    "avg_latency": float(r.avg_latency_s),
    "p95_latency": float(r.p95_latency_s),
    "p99_latency": float(r.p99_latency_s)
} for _, r in ep.iterrows()]

with open(out_json,'w') as f:
    json.dump({
      "lambda_rps": λ,
      "system_avg_latency": avg_sys,
      "nodes": nodes
    }, f, indent=2)
print("Wrote", out_json)
