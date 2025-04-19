import json
from typing import Optional, Dict
from fastapi import FastAPI, Request, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel


from probability import (
    load_config,
    compute_dp_flops,
    compute_delta_b,
    calculate_dnorm,
    compute_probability,
    required_N_for_probability,
    mva,
    compute_tail_mu_min,
    compute_ddos_success_probability,
    compute_stochastic_ddos
)
from spark.find_by_nick import (
    generate_graph,
    beam_search_max_path,
    find_top_neighbors,
    compute_centralities,
    combined_rating,
    get_num_vertices
)
import networkx as nx
from ddos.generate_metrics_from_csv import generate_metrics_from_urls

from parquet_stats import get_peak_hour
from fingerprint import get_average_cores

# ─── Load configuration for static data ─────────────────────────────────────────
cfg = load_config('/home/jovyan/src/scripts/config.json')

G: nx.DiGraph = generate_graph()
# G = nx.read_graphml('/home/jovyan/src/data/graph/graph_time.graphml') 
# ─── Define Pydantic response model ──────────────────────────────────────────────
class AllResults(BaseModel):
    # Classic logistic
    X: float
    p_logistic: float
    N_required: float

    # MVA + Tail latency
    M_clients: int
    throughput: float
    avg_lambda_k: float
    avg_mu_min: float
    C_eff: float

    # Stochastic model
    M1: float
    D2: float
    alpha_s: float
    mu_s: float
    p_stochastic: float

    # Combined RPS + FLOPS
    P_attacker: float
    P_req: float
    p_power: float
    R_att: float
    p_rate: float
    p_total: float

# ─── Initialize FastAPI application ─────────────────────────────────────────────
app = FastAPI(
    title="DDoS Metrics API",
    description="Возвращает метрики DDoS по классической, MVA, стохастической и комбинированной моделям",
    version="1.0"
)

templates = Jinja2Templates(directory="/home/jovyan/src/scripts/templates")

# ─── Routes ──────────────────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def render_form(request: Request):
    """
    Render the HTML form for user inputs.
    """
    return templates.TemplateResponse("form.html", {"request": request})

@app.get("/metrics", response_model=AllResults)
def get_metrics(
    # DP FLOPS parameters via query
    dp_flops_per_cycle: float = Query(8.0, description="FP64 operations per cycle"),
    num_cores: Optional[int] = Query(None, description="Number of CPU cores"),
    frequency_ghz: float = Query(3.574, description="CPU frequency in GHz"),

    # Classic logistic parameters via query
    N: Optional[int] = Query(None, description="Number of users or nodes"),
    alpha: float = Query(0.3, description="Alpha parameter"),
    L: float = Query(1.0, description="Latency scaling factor"),
    P_req: float = Query(28e15, description="Required FLOPS")
):
    # 1) Prepare DP FLOPS parameters
    dp_params = {
        'dp_flops_per_cycle': dp_flops_per_cycle,
        'num_cores':          num_cores or get_average_cores(),
        'frequency_ghz':      frequency_ghz
    }

    # 2) Determine N
    N_val = N or get_num_vertices()

    # 3) Time-based inputs
    time_h, _, peaks = get_peak_hour()
    avg_peak_ratio = min(peaks.values()) / max(peaks.values()) if peaks else 0.0

    # 4) Classic logistic calculations
    P_attacker = compute_dp_flops(dp_params)
    distances = {
        country: calculate_dnorm.__globals__['haversine_distance'](
            *cfg['country_coords'][cfg['server_country']], *coord
        )
        for country, coord in cfg['country_coords'].items()
    }
    d_norm, _, _ = calculate_dnorm(cfg['country_counts'], distances, cfg.get('norm_params', {}))

    X, p_logistic = compute_probability(
        N_val, alpha, P_attacker, d_norm, time_h, L, P_req,
        cfg.get('model_params', {}), avg_peak_ratio
    )
    delta_b = compute_delta_b(time_h, cfg.get('norm_params', {}))
    N_required = required_N_for_probability(
        cfg.get('model_params', {}).get('p_target', 0.999),
        alpha, P_attacker, d_norm, delta_b, L, P_req,
        cfg.get('model_params', {})
    )

    # 5) MVA + Tail latency (static cfg metrics)
    with open(cfg.get('metrics_json_path'), 'r') as f:
        metrics = json.load(f)
    visits = [float(n['visit_ratio']) for n in metrics['nodes']]
    services = [1.0/float(n['avg_latency']) if float(n['avg_latency'])>0 else float('inf') for n in metrics['nodes']]
    tails = [(
        float(n.get('p99_latency', n.get('p95_latency', n['avg_latency']))),
        0.01 if n.get('p99_latency') else 0.05
    ) for n in metrics['nodes']]

    M_clients = max(1, round(float(metrics['lambda_rps']) * float(metrics['system_avg_latency'])))
    throughput, _, _ = mva(visits, services, M_clients)
    lambda_ks = [v * throughput for v in visits]
    mu_mins = [compute_tail_mu_min(lambda_ks[i], *tails[i]) for i in range(len(tails))]
    avg_lambda_k = sum(lambda_ks) / len(lambda_ks)
    avg_mu_min = sum(mu_mins) / len(mu_mins)
    C_eff = max(0.0, avg_mu_min - avg_lambda_k)

    # 6) Combined RPS + FLOPS + stochastic (static cfg)
    f_req = cfg.get('model_params', {}).get('f_req', cfg.get('f_req', 1e9))
    sigma_P = cfg.get('sigma_P', cfg.get('model_params', {}).get('sigma_P', 1e15))
    sigma_C = cfg.get('sigma_C', cfg.get('model_params', {}).get('sigma_C', 0.1))
    t_params = {k: cfg.get('model_params', {}).get(f't{k}', 0.0) for k in ['A','B','C','D','E','G','H','I','J','K']}
    P_proc = cfg.get('model_params', {}).get('P', 0.9)

    p_power, p_rate, p_stochastic, p_total = compute_ddos_success_probability(
        dp_params, P_attacker, f_req, C_eff,
        sigma_P, sigma_C, t_params, P_proc
    )
    M1, D2, alpha_s, mu_s, _ = compute_stochastic_ddos(t_params, P_proc)

    # 7) Return results
    return AllResults(
        X=X,
        p_logistic=p_logistic,
        N_required=N_required,
        M_clients=M_clients,
        throughput=throughput,
        avg_lambda_k=avg_lambda_k,
        avg_mu_min=avg_mu_min,
        C_eff=C_eff,
        M1=M1,
        D2=D2,
        alpha_s=alpha_s,
        mu_s=mu_s,
        p_stochastic=p_stochastic,
        P_attacker=P_attacker,
        P_req=P_req,
        p_power=p_power,
        R_att=P_attacker / f_req,
        p_rate=p_rate,
        p_total=p_total
    )

@app.get("/beam-search")
def beam_search(
    source: str,
    target: str,
    beam_width: int = 1000,
    max_depth: int = 100
):
    path, total_weight = beam_search_max_path(G, source, target, beam_width, max_depth)

    if path is None or not path:
        return {
            "source": source,
            "target": target,
            "path": [],
            "total_weight": None,
            "message": "Путь не найден"
        }

    return {
        "source": source,
        "target": target,
        "path": path,
        "total_weight": total_weight
    }


@app.get("/top-neighbors")
def top_neighbors(player: str, top_k: int = 5):
    top = find_top_neighbors(G, player, top_k)
    return {
        "player": player,
        "top_neighbors": top
    }

@app.get("/centralities")
def centrality_metrics(top_n: int = 10):
    wd, ec, bc = compute_centralities(G)
    top_wd = sorted(wd.items(), key=lambda x: x[1], reverse=True)[:top_n]
    top_ec = sorted(ec.items(), key=lambda x: x[1], reverse=True)[:top_n]
    top_bc = sorted(bc.items(), key=lambda x: x[1], reverse=True)[:top_n]
    return {
        "top_weighted_degree": top_wd,
        "top_eigenvector": top_ec,
        "top_betweenness": top_bc
    }

@app.get("/combined-rating")
def combined_rating_metrics(top_n: int = 10):
    cr = combined_rating(G)
    top_combined = sorted(cr.items(), key=lambda x: x[1], reverse=True)[:top_n]
    return {
        "top_combined_rating": [
            {"player": player, "score": round(score, 4)} for player, score in top_combined
        ]
    }

@app.get("/graph/stats")
def graph_info():
    return {
        "nodes": G.number_of_nodes(),
        "edges": G.number_of_edges()
    }

@app.get("/graph/num-vertices")
def num_vertices():
    return {"vertex_count": get_num_vertices(G)}



@app.post("/generate-metrics")
def generate_metrics(
    csv_path: str = "ddos/endpoint_metrics.csv",
    output_path: str = "ddos/metrics.json"
):
    generate_metrics_from_urls(csv_path, output_path)
    return {
        "status": "ok",
        "output_file": output_path
    }
