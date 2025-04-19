#!/usr/bin/env python3
"""
compute_mva_tail.py

Скрипт выполняет MVA + tail‑Latency анализ на основе metrics.json:
- читает metrics.json, содержащий:
    - lambda_rps          : средняя RPS системы
    - system_avg_latency  : средняя системная задержка (с)
    - nodes               : список узлов с полями:
        - name           : имя endpoint
        - visit_ratio    : доля запросов к endpoint
        - avg_latency    : средняя задержка (с)
        - p95_latency    : 95-й перцентиль задержки (с)
        - p99_latency    : 99-й перцентиль задержки (с)
- вычисляет число клиентов M = λ * avg_latency
- выполняет Exact MVA для замкнутой сети
- оценивает минимальные service_rate для гарантии tail‑SLA

Использование:
    python3 compute_mva_tail.py metrics.json
"""

import argparse
import json
import math
from typing import List, Tuple

def mva(visit_ratios: List[float], service_rates: List[float], M: int) -> Tuple[float, List[float], List[float]]:
    """
    Exact Mean Value Analysis for a closed network.
    Возвращает (throughput λ_M, queue_lengths L_k, response_times W_k).
    """
    K = len(service_rates)
    L = [0.0] * K
    W = [0.0] * K
    throughput = 0.0
    for m in range(1, M + 1):
        # 1) среднее время обработки на каждом узле
        for k in range(K):
            W[k] = (1 + L[k]) / service_rates[k]
        # 2) системная пропускная способность
        throughput = m / sum(v * Wk for v, Wk in zip(visit_ratios, W))
        # 3) обновляем длины очередей
        for k in range(K):
            L[k] = visit_ratios[k] * throughput * W[k]
    return throughput, L, W

def compute_tail_mu_min(lambda_k: float, t_p: float, alpha: float) -> float:
    """
    Минимальный service rate μ_k для обеспечения P(W_k > t_p) <= alpha.
    Для экспоненциального узла: μ_k >= λ_k + (-ln(alpha)) / t_p
    """
    return lambda_k + (-math.log(alpha)) / t_p

def main():
    parser = argparse.ArgumentParser(description="Compute MVA + tail‑Latency based on metrics.json")
    parser.add_argument("metrics_json", help="Path to metrics.json")
    args = parser.parse_args()

    # Загрузка метрик
    with open(args.metrics_json, 'r', encoding='utf-8') as f:
        metrics = json.load(f)

    lambda_rps = float(metrics["lambda_rps"])
    sys_avg = float(metrics["system_avg_latency"])
    nodes = metrics["nodes"]

    # Оценка числа клиентов M
    M = max(1, int(round(lambda_rps * sys_avg)))

    # Подготовка векторов для MVA и tail
    visit_ratios: List[float] = []
    service_rates: List[float] = []
    tail_requirements: List[Tuple[float, float]] = []

    for node in nodes:
        v = float(node["visit_ratio"])
        avg_lat = float(node["avg_latency"])
        mu_k = 1.0 / avg_lat if avg_lat > 0 else float('inf')

        # выбираем tail‑SLA: p99 если есть, иначе p95
        if node.get("p99_latency") is not None:
            t_p = float(node["p99_latency"])
            alpha = 0.01
        else:
            t_p = float(node.get("p95_latency", avg_lat))
            alpha = 0.05

        visit_ratios.append(v)
        service_rates.append(mu_k)
        tail_requirements.append((t_p, alpha))

    # Запуск MVA
    throughput, L_vals, W_vals = mva(visit_ratios, service_rates, M)

    # Вычисление нагрузок λ_k и μ_min для tail‑SLA
    lambda_ks = [v * throughput for v in visit_ratios]
    mu_mins = [
        compute_tail_mu_min(lambda_ks[k], tail_requirements[k][0], tail_requirements[k][1])
        for k in range(len(nodes))
    ]

    # Вывод результатов
    print("\n=== MVA + Tail Latency ===")
    print(f"Clients (M)              : {M}")
    print(f"System throughput (λ_M)  : {throughput:.2f} req/s\n")

    for k, node in enumerate(nodes):
        print(f"Node '{node['name']}':")
        print(f"  visit_ratio            : {visit_ratios[k]:.2f}")
        print(f"  service_rate (μ_k)     : {service_rates[k]:.2f} req/s")
        print(f"  avg queue length (L_k) : {L_vals[k]:.2f}")
        print(f"  avg wait time (W_k)    : {W_vals[k]:.4f} s")
        print(f"  λ_k = v_k·λ_M          : {lambda_ks[k]:.2f} req/s")
        print(f"  min μ_k for tail SLA   : {mu_mins[k]:.2f} req/s\n")

if __name__ == "__main__":
    main()
