import csv
import json
import statistics
import time
import requests
from typing import List

def calculate_percentile(data: List[float], percentile: int) -> float:
    if not data:
        return 0.0
    try:
        return round(statistics.quantiles(data, n=100)[percentile - 1], 4)
    except Exception:
        return round(sorted(data)[int(len(data) * percentile / 100)], 4)

def measure_latency(url: str, attempts: int = 10, timeout: int = 5) -> List[float]:
    latencies = []
    for _ in range(attempts):
        try:
            start = time.time()
            resp = requests.get(url, timeout=timeout)
            end = time.time()
            if resp.status_code == 200:
                latencies.append(end - start)
        except Exception:
            continue  # если ошибка, просто пропускаем
    return latencies

def generate_metrics_from_urls(csv_path: str = "ddos/endpoint_metrics_url.csv", output_path: str = "ddos/metrics.json"):
    urls = []
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if 'url' in row:
                urls.append(row['url'])

    metrics_nodes = []
    total_successes = 0
    total_latency = 0.0

    for url in urls:
        print(f"🌐 Пингую {url}...")
        latencies = measure_latency(url)

        if not latencies:
            print(f"⚠️  Нет успешных ответов от {url}")
            continue

        avg_latency = round(sum(latencies) / len(latencies), 4)
        p95_latency = calculate_percentile(latencies, 95)
        p99_latency = calculate_percentile(latencies, 99)

        metrics_nodes.append({
            "name": url,
            "visit_ratio": len(latencies),  # будет нормализован
            "avg_latency": avg_latency,
            "p95_latency": p95_latency,
            "p99_latency": p99_latency
        })

        total_successes += len(latencies)
        total_latency += sum(latencies)

    # Нормализуем visit_ratio
    if total_successes > 0:
        for node in metrics_nodes:
            node["visit_ratio"] = round(node["visit_ratio"] / total_successes, 4)

        lambda_rps = round(total_successes / 60, 4)  # 60 секунд
        system_avg_latency = round(total_latency / total_successes, 4)
    else:
        lambda_rps = 0.0
        system_avg_latency = 0.0

    result = {
        "lambda_rps": lambda_rps,
        "system_avg_latency": system_avg_latency,
        "nodes": metrics_nodes
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"✅ Метрики сохранены в {output_path}")
