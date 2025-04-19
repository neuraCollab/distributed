# graph_analysis.py

import os
from pathlib import Path
from pyspark.sql import SparkSession
import networkx as nx
from tqdm import tqdm


def init_spark(app_name: str = "Lichess Data Processing") -> SparkSession:
    return SparkSession.builder.appName(app_name).getOrCreate()


def list_parquet_files(data_dir: str, prefix: str = "lichess_part") -> list:
    return sorted(
        os.path.join(data_dir, f)
        for f in os.listdir(data_dir)
        if f.startswith(prefix) and f.endswith(".parquet")
    )


def read_data(spark: SparkSession, parquet_files: list):
    print(f"🔍 Найдено файлов: {len(parquet_files)}")
    df = spark.read.parquet(*parquet_files)
    print(f"🎮 Всего партий: {df.count()}")
    df.show(5)
    return df


def build_edges_rdd(df):
    edges_df = df.select(
        "white", "black", "white_elo", "black_elo", "result", "time_control", "moves_count"
    )
    return edges_df.rdd.flatMap(lambda row: [
        ((row.white, row.black), (row.white_elo, row.black_elo, row.result, row.time_control, row.moves_count)),
        ((row.black, row.white), (row.black_elo, row.white_elo, row.result, row.time_control, row.moves_count))
    ])


def aggregate_edges(edges_rdd):
    return edges_rdd.map(lambda x: (x[0], x[1])).reduceByKey(lambda a, b: a)


def parse_time_control(tc: str) -> tuple:
    try:
        if '+' in tc:
            m, inc = tc.split('+')
            return int(m), int(inc)
        return int(tc), 0
    except:
        return 1, 0


def build_graph(edges_aggregated, rdd_count: int) -> nx.DiGraph:
    G = nx.DiGraph()
    for (u, v), (we, be, res, tc, mc) in tqdm(
        edges_aggregated.collect(),
        total=rdd_count,
        desc="Агрегация рёбер"
    ):
        m, inc = parse_time_control(tc)
        weight = (2*m + mc*inc)/60 if mc else 0.0001
        if res == '1-0':
            G.add_edge(u, v, weight=weight)
        elif res == '0-1':
            G.add_edge(v, u, weight=weight)
    print(f"✅ Всего рёбер: {G.number_of_edges()}")
    return G


def save_graph(G: nx.DiGraph, path: str):
    nx.write_graphml(G, path)
    print(f"Граф сохранён в {path}")


def beam_search_max_path(G, source, target, beam_width=5, max_depth=10):
    frontier = [(source, [source], 0)]
    best, best_w = None, float('-inf')
    for _ in range(max_depth):
        new_f = []
        for node, path, w in frontier:
            if node == target and w > best_w:
                best, best_w = path, w
            for nbr in G.successors(node):
                if nbr not in path:
                    nw = w + G[node][nbr]['weight']
                    new_f.append((nbr, path+[nbr], nw))
        frontier = sorted(new_f, key=lambda x: x[2], reverse=True)[:beam_width]
        if not frontier: break
    return best, best_w


def find_top_neighbors(G, player, top_k=5):
    nbrs = {}
    for nbr in set(G.successors(player))|set(G.predecessors(player)):
        w = G[player][nbr]['weight'] if G.has_edge(player,nbr) else 0
        w += G[nbr][player]['weight'] if G.has_edge(nbr,player) else 0
        nbrs[nbr] = w
    return [n for n,_ in sorted(nbrs.items(), key=lambda x: x[1], reverse=True)[:top_k]]


def compute_centralities(G):
    # weighted degree
    wd = {n: sum(d['weight'] for _,_,d in G.edges(n,data=True)) for n in G}
    # eigenvector
    try:
        ec = nx.eigenvector_centrality(G, weight='weight', max_iter=250)
    except:
        ec = nx.eigenvector_centrality_numpy(G, weight='weight')
    # betweenness
    bc = nx.betweenness_centrality(G, weight='weight', k=5, seed=42)
    return wd, ec, bc


def normalize(d):
    mn, mx = min(d.values()), max(d.values())
    return {k:(v-mn)/(mx-mn) if mx>mn else 0 for k,v in d.items()}


def combined_rating(G):
    wd, ec, bc = compute_centralities(G)
    nw, ne, nb = normalize(wd), normalize(ec), normalize(bc)
    return {n:(nw[n]+ne[n]+nb[n])/3 for n in G}

def get_num_vertices(G: nx.Graph | None = None  ) -> int:
    """
    Возвращает число вершин (игроков) в графе G.
    """
    if G is None:
        G = generate_graph()
    return G.number_of_nodes()

def generate_graph(data_dir: str = os.path.join(os.getcwd(), 'src/parquets')) -> nx.Graph:
    """
    Генерирует граф G с заданными параметрами.
    """
    # Здесь можно добавить логику генерации графа
    spark = init_spark()
    files = list_parquet_files(data_dir)
    df = read_data(spark, files)
    edges_rdd = build_edges_rdd(df)
    agg = aggregate_edges(edges_rdd)
    G = build_graph(agg, edges_rdd.count())
    
    return G

if __name__ == "__main__":

    G = generate_graph(nx.DiGraph())
    
    save_graph(G, "graph_time.graphml")

    # примеры использования
    path, w = beam_search_max_path(G, "king04", "pmp", beam_width=100, max_depth=10)
    print("Path:", path, "Weight:", w)

    print("Top neighbors of pmp:", find_top_neighbors(G, "pmp", 5))

    wd, ec, bc = compute_centralities(G)
    print("Top 10 by WD:", sorted(wd.items(), key=lambda x: x[1], reverse=True)[:10])
    print("Top 10 by EC:", sorted(ec.items(), key=lambda x: x[1], reverse=True)[:10])
    print("Top 10 by BC:", sorted(bc.items(), key=lambda x: x[1], reverse=True)[:10])

    cr = combined_rating(G)
    print("Top 10 combined:", sorted(cr.items(), key=lambda x: x[1], reverse=True)[:10])
