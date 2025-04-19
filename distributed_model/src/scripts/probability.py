#!/usr/bin/env python3
"""
full_analysis.py

Полный скрипт, который:
1) Рассчитывает DDoS‑метрики на основе FLOPS атакующего и RPS сервера.
2) Проводит MVA + Tail Latency анализ на реальных данных из metrics.json.
3) Оценивает среднее время успешной DDoS‑атаки по методу Богер & Соколов.

Конфиг config.json должен содержать:
  - dp_flops_per_cycle, num_cores, frequency_ghz
  - earth_radius_km, server_country, country_counts, country_coords
  - f_req, sigma_R, sigma_C, sigma_P
  - model_params (включая tA…tK, P), norm_params
  - metrics_json_path (путь к metrics.json)

Использование:
    python3 full_analysis.py
"""

import math
import json
import numpy as np
import sympy as sp
from scipy.special import gammainc, gamma
from typing import Dict, List, Tuple

from parquet_stats import get_peak_hour
from spark.find_by_nick import get_num_vertices
from fingerprint import get_average_cores

# ─── 0. ЗАГРУЗКА КОНФИГА ─────────────────────────────────────────────────────────

def load_config(path: str) -> dict:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

cfg = load_config('/home/jovyan/src/scripts/config.json')

# ─── 1. БАЗОВЫЕ ВЫЧИСЛЕНИЯ ─────────────────────────────────────────────────────────

def compute_dp_flops(params: dict) -> float:
    return (params['dp_flops_per_cycle']
            * params['num_cores']
            * params['frequency_ghz']
            * 1e9)

def compute_delta_b(time_hour: float, params: dict) -> float:
    optimal = params.get('optimal_hour', 14.0)
    max_dev = params.get('max_deviation', 24.0)
    return max(0.0, 1.0 - abs(time_hour - optimal) / max_dev)

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = cfg['earth_radius_km']
    φ1, φ2 = math.radians(lat1), math.radians(lat2)
    Δφ = math.radians(lat2 - lat1)
    Δλ = math.radians(lon2 - lon1)
    a = math.sin(Δφ/2)**2 + math.cos(φ1)*math.cos(φ2)*math.sin(Δλ/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def average_peak(peaks: dict) -> float:
    vals = list(peaks.values())
    return min(vals)/max(vals) if vals else 0.0

# Геоданные для d_norm
country_counts = cfg['country_counts']
country_coords = cfg['country_coords']
server_lat, server_lon = country_coords[cfg['server_country']]
distances = {
    c: haversine_distance(server_lat, server_lon, lat, lon)
    for c,(lat,lon) in country_coords.items()
}

def calculate_dnorm(counts: Dict[str,int], dists: Dict[str,float], params: dict) -> Tuple[float,List[str],List[float]]:
    sorted_c = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    top5 = [c for c,_ in sorted_c[:params.get('top_k',5)]]
    d5 = [dists.get(c,float('inf')) for c in top5]
    inv = [1.0/d for d in d5 if d and math.isfinite(d)]
    avg_inv = sum(inv)/len(inv) if inv else 0.0
    return max(0.0, 1.0-avg_inv), top5, d5

# ─── 2. КЛАССИЧЕСКАЯ ЛОГИСТИЧЕСКАЯ МОДЕЛЬ ───────────────────────────────────────────

def compute_probability(N: int, alpha: float, P: float, d_norm: float,
                        time_hour: float, L: float, P_req: float,
                        params: dict, avg_peak: float) -> Tuple[float,float]:
    delta_b = compute_delta_b(time_hour, params)
    eps = 1e-12
    logs = np.log([
        N*P*alpha + eps,
        L*d_norm + eps,
        math.sin(delta_b*math.pi/2) + avg_peak + eps
    ])
    log_X = float(np.sum(logs)) - math.log(P_req + eps)
    X = math.exp(log_X)
    beta, gamma_ = params.get('beta',5.0), params.get('gamma',1.0)
    z = beta*(X-gamma_)
    p = 1.0/(1.0+math.exp(-z))
    return X, p

def required_N_for_probability(p_target: float, alpha: float, P: float,
                               d_norm: float, delta_b: float, L: float,
                               P_req: float, params: dict) -> float:
    beta, gamma_ = params.get('beta',5.0), params.get('gamma',1.0)
    X_t = gamma_ - math.log((1.0/p_target)-1.0)/beta
    eps = 1e-12
    ln_rest = sum(math.log(v+eps) for v in (alpha,P,d_norm,delta_b,L))
    return math.exp(math.log(X_t+eps) + math.log(P_req+eps) - ln_rest)

# ─── 3. DDoS RPS‑модель ─────────────────────────────────────────────────────────────

def compute_ddos_success_probability(
    dp_params: dict,
    P: float,
    f_req: float,
    C_eff: float,
    sigma_P: float,
    sigma_C: float,
    t_params: Dict[str,float],
    P_proc: float
) -> Tuple[float,float,float,float]:
    """
    dp_params: те же, что в compute_dp_flops, нужно для «взлома» P_req из флопс
    P: фактическое количество FLOPS атакующего
    f_req: нагрузка на запрос
    C_eff: остаточная ёмкость RPS
    sigma_P, sigma_C: дисперсии
    t_params: { 'A':tA, ..., 'K':tK }
    P_proc: P из стох. модели (вероятность каждого этапа)
    """
    # 1) Взлом P_req: пусть порог = та же compute_dp_flops(dp_params)
    P_req = compute_dp_flops(dp_params)

    # нормальная CDF
    def norm_cdf(x): return 0.5 * (1 + math.erf(x / math.sqrt(2)))

    # 2) p_power: мощность флопс
    p_power = 1.0 - norm_cdf((P_req - P) / sigma_P)

    # 3) p_rate: RPS
    R_att = P / f_req
    sigma_R = sigma_P / f_req
    sigma_diff = math.sqrt(sigma_R**2 + sigma_C**2)
    p_rate = 1.0 - norm_cdf((C_eff - R_att) / sigma_diff)

    # 4) p_stoch: вероятность завершения по стохастической модели
    M1, D2, alpha, mu, F = compute_stochastic_ddos(t_params, P_proc)
    p_stoch = F(M1)

    # 5) общая вероятность
    p_total = p_power * p_rate * p_stoch

    return p_power, p_rate, p_stoch, p_total


# ─── 4. MVA + Tail Latency ──────────────────────────────────────────────────────────

def mva(visits: List[float], services: List[float], M: int) -> Tuple[float,List[float],List[float]]:
    K = len(services)
    L = [0.0]*K; W = [0.0]*K
    for m in range(1, M+1):
        for k in range(K): W[k] = (1+L[k])/services[k]
        thr = m/sum(v*Wk for v,Wk in zip(visits,W))
        for k in range(K): L[k] = visits[k]*thr*W[k]
    return thr, L, W

def compute_tail_mu_min(lambda_k: float, t_p: float, alpha: float) -> float:
    return lambda_k + (-math.log(alpha))/t_p

# ─── 5. Стохастическая модель Богер & Соколов ──────────────────────────────────────

def compute_stochastic_ddos(t_params: Dict[str,float], P_proc: float):
    # s — Лаплас‑переменная, P — вероятность процессов
    s, P = sp.symbols('s P', positive=True)
    # λ_i = 1/t_i (только для ненулевых t_i)
    lam = {k: 1.0/v for k, v in t_params.items() if v > 0}
    # L_i(s) = λ_i / (s + λ_i)
    Ls = {k: lam[k]/(s + lam[k]) for k in lam}

    # Прямой путь: Qx(s) = ∏ L_i(s) для процессов A,B,D,E,G,H,J,K
    Qx = 1
    for k in ['A','B','D','E','G','H','J','K']:
        if k in Ls:
            Qx *= Ls[k]
    # У нас четыре P-фактора: B,D,E,H
    Qx *= P**4

    # 1) Собираем петли первого порядка
    loops1 = []
    if 'B' in Ls and 'C' in Ls:
        loops1.append(Ls['B'] * (1-P) * Ls['C'])
    if all(x in Ls for x in ['B','D','C']):
        loops1.append(Ls['B']*Ls['D'] * P*(1-P) * Ls['C'])
    if all(x in Ls for x in ['B','D','E','C']):
        loops1.append(Ls['B']*Ls['D']*Ls['E'] * P**2*(1-P) * Ls['C'])
    if 'H' in Ls and 'I' in Ls:
        loops1.append(Ls['H'] * (1-P) * Ls['I'])

    # 2) Петли второго порядка: пары непересекающихся первых петель
    from itertools import combinations
    loops2 = []
    for l1, l2 in combinations(loops1, 2):
        loops2.append(l1 * l2)

    # 3) Определяем Δ(s) по Мейсону: Δ = 1 - Σloops1 + Σloops2
    Delta = 1 - sum(loops1) + sum(loops2)

    # 4) Характеристическая функция Q(s) = Qx(s) / Δ(s)
    Q = sp.simplify(Qx / Delta)

    # 5) Считаем моменты: Q0 = Q(0), Q'(0), Q''(0)
    Q0  = Q.subs({s: 0, P: P_proc})
    dQ1 = sp.diff(Q, s).subs({s: 0, P: P_proc})
    dQ2 = sp.diff(Q, s, 2).subs({s: 0, P: P_proc})

    M1 = float((-dQ1 / Q0).evalf())              # среднее время
    D2 = float((dQ2 / Q0 - M1**2).evalf())       # дисперсия

    # 6) Параметры гамма‑распределения
    alpha = M1**2 / D2
    mu    = D2 / M1

    # 7) Функция распределения F(t)
    def F(t: float) -> float:
        return gammainc(alpha, t/mu) / gamma(alpha)

    return M1, D2, alpha, mu, F

if __name__ == "__main__":
    # ─── ЗАГРУЗКА ПАРАМЕТРОВ ───────────────────────────────────────────────
    dp_params = {
        'dp_flops_per_cycle': cfg.get('dp_flops_per_cycle', 8.0),
        'num_cores':          cfg.get('num_cores') or get_average_cores(),
        'frequency_ghz':      cfg.get('frequency_ghz', 3.574)
    }
    model_p = cfg.get('model_params', {})
    norm_p  = cfg.get('norm_params', {})

    # классическая модель
    N        = model_p.get('N') or get_num_vertices()
    alpha_   = model_p.get('alpha', 0.3)
    L_scale  = model_p.get('L', 1.0)
    P_req    = model_p.get('P_req', 28e15)
    time_h, _, peaks = get_peak_hour()
    avg_pk   = average_peak(peaks)

    # MVA + Tail Latency
    with open(cfg.get('metrics_json_path',
                      '/home/jovyan/src/scripts/ddos/metrics.json'),
              'r', encoding='utf-8') as f:
        metrics = json.load(f)
    lambda_rps   = float(metrics['lambda_rps'])
    sys_avg_lat  = float(metrics['system_avg_latency'])
    nodes        = metrics['nodes']
    M_clients    = max(1, int(round(lambda_rps * sys_avg_lat)))

    # стохастическая модель параметры
    t_params = {
        'A': model_p.get('tA', 0.0),
        'B': model_p.get('tB', 0.0),
        'C': model_p.get('tC', 0.0),
        'D': model_p.get('tD', 0.0),
        'E': model_p.get('tE', 0.0),
        'G': model_p.get('tG', 0.0),
        'H': model_p.get('tH', 10.0),
        'I': model_p.get('tI', 6.0),
        'J': model_p.get('tJ',10.0),
        'K': model_p.get('tK',60.0)
    }
    P_proc = model_p.get('P', 0.9)

    # ─── ВЫЧИСЛЕНИЯ ───────────────────────────────────────────────────────────
    # 1) Classic logistic
    P = compute_dp_flops(dp_params)
    d_norm, top5, d5 = calculate_dnorm(country_counts, distances, norm_p)
    X, p_classic = compute_probability(
        N, alpha_, P, d_norm, time_h, L_scale, P_req, model_p, avg_pk
    )
    delta_b = compute_delta_b(time_h, norm_p)
    N_req   = required_N_for_probability(
        model_p.get('p_target', 0.999),
        alpha_, P, d_norm, delta_b, L_scale, P_req, model_p
    )

    # 2) MVA + Tail latency
    visits, services, tails = [], [], []
    for n in nodes:
        v     = float(n['visit_ratio'])
        mu_k  = 1.0/float(n['avg_latency']) if float(n['avg_latency'])>0 else float('inf')
        if n.get('p99_latency') is not None:
            tails.append((float(n['p99_latency']), 0.01))
        else:
            tails.append((float(n.get('p95_latency', n['avg_latency'])), 0.05))
        visits.append(v)
        services.append(mu_k)

    throughput, L_vals, W_vals = mva(visits, services, M_clients)
    lambda_ks = [v*throughput for v in visits]
    mu_mins   = [
        compute_tail_mu_min(lambda_ks[i], *tails[i])
        for i in range(len(nodes))
    ]
    avg_lambda_k = sum(lambda_ks)/len(lambda_ks)
    avg_mu_min   = sum(mu_mins)/len(mu_mins)
    C_eff        = max(0.0, avg_mu_min - avg_lambda_k)

    # 3) DDoS RPS + стохастическая
    f_req   = model_p.get('f_req', cfg.get('f_req', 1e9))
    sigma_P = cfg.get('sigma_P', model_p.get('sigma_P', 1e15))
    sigma_C = cfg.get('sigma_C', model_p.get('sigma_C', 0.1))

    p_power, p_rate, p_stoch, p_ddos = compute_ddos_success_probability(
        dp_params, P, f_req, C_eff, sigma_P, sigma_C, t_params, P_proc
    )

    # 4) Параметры стохастической сети
    M1, D2, alpha_s, mu_s, F = compute_stochastic_ddos(t_params, P_proc)

    # ─── ВЫВОД РЕЗУЛЬТАТОВ ─────────────────────────────────────────────────────────
    print("\n=== Classic logistic DDoS model ===")
    print(f"X (combined metric)                  : {X:.6f}")
    print(f"p_classic (logistic probability)     : {p_classic:.6f}")
    print(f"N_req (for p_target)                 : {N_req:.0f}")

    print("\n=== MVA + Tail Latency (Real Data) ===")
    print(f"Clients (M)                          : {M_clients}")
    print(f"System throughput (λ_M)              : {throughput:.2f} req/s")
    print(f"λ_k (avg)                            : {avg_lambda_k:.2f} req/s")
    print(f"μ_min for tail SLA (avg)             : {avg_mu_min:.2f} req/s")
    print(f"C_eff (residual capacity)            : {C_eff:.2f} req/s")

    print("\n=== Stochastic DDoS model (Boger & Sokolov) ===")
    print(f"Mean attack time M1                  : {M1:.2f} s")
    print(f"Variance D2                          : {D2:.2f} s^2")
    print(f"Gamma params: alpha = {alpha_s:.3f}, mu = {mu_s:.3f}")
    print(f"Probability F(M1)                   : {F(M1):.4f}")

    print("\n=== RPS & FLOPS combined model ===")
    print(f"P (FLOPS атакующего)                 : {P:.2e}")
    print(f"P_req (required flops)               : {P_req:.2e}")
    print(f"p_power (P > P_req)                  : {p_power:.6f}")
    print(f"R_att = P/f_req                      : {P/f_req:.2e} req/s")
    print(f"p_rate (R_att > C_eff)               : {p_rate:.6f}")
    print(f"p_stoch (F(M1))                      : {p_stoch:.6f}")
    print(f"p_ddos (total combined)              : {p_ddos:.6f}")
