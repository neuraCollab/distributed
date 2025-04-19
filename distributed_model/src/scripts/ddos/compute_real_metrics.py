#!/usr/bin/env python3
"""
compute_real_metrics.py

Скрипт формирует metrics.json для MVA + tail‑Latency анализа на основе CSV-логов:
- lambda_rps         : средняя пропускная способность (запросов в секунду)
- system_avg_latency : средняя сквозная задержка (сек)
- nodes              : список словарей с метриками по каждому endpoint:
    - name        : имя endpoint
    - visit_ratio : доля запросов к этому endpoint
    - avg_latency : средняя задержка (сек)
    - p95_latency : 95-й перцентиль задержки (сек)
    - p99_latency : 99-й перцентиль задержки (сек)

Использование:
    python3 compute_real_metrics.py logs.csv metrics.json
"""

import argparse
import pandas as pd
import json
import sys

def compute_real_metrics(log_csv: str, out_json: str):
    # Чтение исходного CSV
    df = pd.read_csv(log_csv, parse_dates=['timestamp'])
    total_requests = len(df)
    if total_requests == 0:
        print("No data in log file.")
        sys.exit(1)

    # 1) Системная пропускная способность (λ_measured)
    df.set_index('timestamp', inplace=True)
    rps_series = df.groupby(pd.Grouper(freq='1S')).size()
    lambda_rps = float(rps_series.mean())

    # 2) Средняя системная задержка
    system_avg_latency = float(df['latency'].mean())

    # 3) Метрики по endpoint
    df.reset_index(inplace=True)
    nodes = []
    for endpoint, grp in df.groupby('endpoint'):
        cnt = len(grp)
        nodes.append({
            "name": endpoint,
            "visit_ratio": cnt / total_requests,
            "avg_latency": float(grp['latency'].mean()),
            "p95_latency": float(grp['latency'].quantile(0.95)),
            "p99_latency": float(grp['latency'].quantile(0.99))
        })

    # 4) Сборка и сохранение JSON
    metrics = {
        "lambda_rps": lambda_rps,
        "system_avg_latency": system_avg_latency,
        "nodes": nodes
    }
    with open(out_json, 'w') as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)
    print(f"Metrics written to {out_json}")

def main():
    parser = argparse.ArgumentParser(
        description="Generate metrics.json from logs.csv for MVA + tail-Latency analysis"
    )
    parser.add_argument("logs_csv", help="Path to CSV with columns: timestamp, endpoint, latency")
    parser.add_argument("output_json", help="Path to output metrics.json")
    args = parser.parse_args()

    compute_real_metrics(args.logs_csv, args.output_json)

if __name__ == "__main__":
    main()
