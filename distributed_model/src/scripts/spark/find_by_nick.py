# %%
# %pip install networkx matplotlib tqdm python-louvain

# %%
from pyspark.sql import SparkSession
import os
import networkx as nx
import matplotlib.pyplot as plt
from tqdm import tqdm  # Для прогресс-бара

# %%
# 📂 Путь к данным
data_dir = os.path.join(os.getcwd(), './work/src/parquets')

# Получаем все файлы Parquet, которые начинаются с "lichess_part"
parquet_files = sorted([os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.startswith("lichess_part") and f.endswith(".parquet")])


# %%
# Инициализация SparkSession
spark = SparkSession.builder \
    .appName("Lichess Data Processing") \
    .getOrCreate()

# 📥 Чтение и объединение
print(f"🔍 Найдено файлов: {len(parquet_files)}")
df = spark.read.parquet(*parquet_files)

# 🎮 Вывод общего числа партий
print(f"\n🎮 Всего партий: {df.count()}")

# Вывод первых 5 строк
df.show(5)

# %%
# 📥 Создание пар игроков для белых и черных
print("🔄 Создание пар игроков (white, black)...")
edges_df = df.select("white", "black", "white_elo", "black_elo", "result", "time_control", "moves_count")

edges_rdd = edges_df.rdd.flatMap(lambda row: [
    (
        (row["white"], row["black"]),
        (row["white_elo"], row["black_elo"], row["result"], row["time_control"], row["moves_count"])
    ),
    (
        (row["black"], row["white"]),
        (row["black_elo"], row["white_elo"], row["result"], row["time_control"], row["moves_count"])
    )
])

# %%
# Преобразование в RDD и агрегация
print("🔄 Аггрегация данных...")

# Получаем общее количество элементов в RDD
total_count = edges_rdd.count()

# Применяем агрегацию
edges_aggregated = edges_rdd.map(lambda edge: (edge[0], edge[1])) \
    .reduceByKey(lambda a, b: (a[0], a[1], a[2], a[3], a[4]))  # Для агрегации

# Создание графа (должно быть до добавления рёбер)

G = nx.DiGraph()  # Направленный граф

# Собираем результаты с отображением прогресса
edges = []

# %%
print("📊 Создание графа связей...")

# Преобразуем time_control в два числа: основное время и дополнительное время
def parse_time_control(time_control):
    try:
        if '+' in time_control:
            main_time, additional_time = time_control.split('+')
            return int(main_time), int(additional_time)
        else:
            # Если дополнительное время отсутствует, возвращаем 0 для дополнительного времени
            return int(time_control), 0
    except ValueError:
        # Если time_control не может быть преобразовано в число, возвращаем значение по умолчанию
        return 1, 0  # Можно настроить значения по умолчанию

for edge, (white_elo, black_elo, result, time_control, moves_count) in tqdm(
    edges_aggregated.collect(), total=total_count, desc="Агрегация рёбер", unit="партий"
):
    # Извлекаем основное и дополнительное время из time_control (формат "main+increment")
    main_time, additional_time = parse_time_control(time_control)
    
    # Рассчитываем вес как сумму основного времени для обеих сторон и дополнительного времени за все ходы, нормированную до минут:
    if moves_count == 0:
        weight = 0.0001
    else:
        weight = (2 * main_time + moves_count * additional_time) / 60

    # Направление рёбер зависит от результата игры:
    if result == '1-0':
        # Победили белые: направляем ребро от белых к чёрным
        G.add_edge(edge[0], edge[1], weight=weight)
    elif result == '0-1':
        # Победили чёрные: направляем ребро от чёрных к белым
        G.add_edge(edge[1], edge[0], weight=weight)

print(f"✅ Аггрегация завершена! Всего рёбер: {len(G.edges)}")

# %%
# Сохранение графа сложности партий в формате GraphML
output_path = os.path.join(os.getcwd(), 'graph_time.graphml')
nx.write_graphml(G, output_path)

print(f"Граф сохранён в {output_path}")

# %%
# for edge, (white_elo, black_elo, result, time_control, moves_count) in tqdm(edges_aggregated.collect(), total=total_count, desc="Агрегация рёбер", unit="партий"):
    
#     # Извлекаем основное и дополнительное время из time_control
#     main_time, additional_time = parse_time_control(time_control)
    
#     # Рассчитываем вес по формуле: (тут пару партий все равно отсеется, ну и ладно)
#     weight = abs(white_elo - black_elo) / 100 
#     if main_time != 0:
#         weight += moves_count * (additional_time / main_time)
#     else:    
#         weight = 0.0001

#     # Направление рёбер зависит от результата игры
#     if result == '1-0':
#         # Победили белые, направление от белых к черным
#         G.add_edge(edge[0], edge[1], weight=weight)
#     elif result == '0-1':
#         # Победили черные, направление от черных к белым
#         G.add_edge(edge[1], edge[0], weight=weight)

# print(f"✅ Аггрегация завершена! Всего рёбер: {len(G.edges)}")

# %%
# # Сохранение графа сложности партий в формате GraphML
# output_path = os.path.join(os.getcwd(), 'graph.graphml')
# nx.write_graphml(G, output_path)

# print(f"Граф сохранён в {output_path}")

# %%
def beam_search_max_path(G, source, target, beam_width=5, max_depth=10):
    # Пути будем хранить как кортежи (current_node, path_list, current_weight)
    current_frontier = [(source, [source], 0)]
    best_path = None
    best_weight = float('-inf')
    
    for depth in range(max_depth + 1):
        new_frontier = []
        for node, path, weight in current_frontier:
            if node == target and weight > best_weight:
                best_weight = weight
                best_path = path
            # Расширяем путь
            for neighbor in G.successors(node):
                if neighbor in path:
                    continue  # исключаем циклы
                edge_weight = G[node][neighbor]['weight']
                new_weight = weight + edge_weight
                new_frontier.append((neighbor, path + [neighbor], new_weight))
        
        # Отсортируем расширенные пути по убыванию веса и оставим beam_width лучших
        new_frontier.sort(key=lambda x: x[2], reverse=True)
        current_frontier = new_frontier[:beam_width]
        
        if not current_frontier:
            break

    return best_path, best_weight

# %%
def find_top_neighbors(G, player, top_k=5):
    """
    Находит топ-K соседей для игрока по суммарному весу рёбер.
    Для учета всех партий, рассматриваются как исходящие, так и входящие ребра.
    
    :param G: ориентированный граф (networkx.DiGraph) с атрибутом 'weight' на ребрах
    :param player: имя игрока (вершина графа)
    :param top_k: количество лучших соседей для выбора
    :return: список соседей (игроков) в порядке убывания суммарного веса
    """
    neighbors = {}
    
    # Объединяем входящих и исходящих соседей
    all_neighbors = set(G.successors(player)) | set(G.predecessors(player))
    
    for neighbor in all_neighbors:
        total_weight = 0
        if G.has_edge(player, neighbor):
            total_weight += G[player][neighbor]['weight']
        if G.has_edge(neighbor, player):
            total_weight += G[neighbor][player]['weight']
        neighbors[neighbor] = total_weight

    # Сортировка соседей по убыванию суммарного веса
    top_neighbors = sorted(neighbors.items(), key=lambda x: x[1], reverse=True)[:top_k]
    # Вернуть только имена соседей
    return [n for n, w in top_neighbors]

def find_path_via_tops(G, source, target, top_k=5, max_depth=10):
    """
    Ищет путь от source до target, проходящий только через топовых противников.
    На каждом шаге для текущего игрока рассматриваются только его топ-соседи.
    
    :param G: ориентированный граф (networkx.DiGraph) с атрибутом 'weight' на ребрах
    :param source: исходный игрок (начальная вершина)
    :param target: целевой игрок (конечная вершина)
    :param top_k: сколько топ-соседей рассматривать у каждого игрока
    :param max_depth: максимальная глубина поиска
    :return: найденный путь (список вершин) или None, если путь не найден
    """
    best_path = None

    def dfs(current, path, depth):
        nonlocal best_path
        if depth > max_depth:
            return
        if current == target:
            best_path = path
            return
        # Получаем топовых соседей для текущего игрока
        top_neighbors = find_top_neighbors(G, current, top_k)
        for neighbor in top_neighbors:
            if neighbor in path:
                continue  # избегаем циклов
            dfs(neighbor, path + [neighbor], depth + 1)
            if best_path is not None:
                # Если путь найден, можно остановиться
                return

    dfs(source, [source], 0)
    return best_path


# %%
# 1. Анализ центральности и влияния

# a. Взвешенная степень (Weighted Degree)
weighted_degrees = {}
for node in tqdm(G.nodes(), desc="Вычисление Weighted Degree"):
    total_weight = 0
    for _, _, data in G.out_edges(node, data=True):
        total_weight += data['weight']
    for _, _, data in G.in_edges(node, data=True):
        total_weight += data['weight']
    weighted_degrees[node] = total_weight

top_weighted = sorted(weighted_degrees.items(), key=lambda x: x[1], reverse=True)[:10]


# b. Eigenvector Centrality
print("\nВычисление Eigenvector Centrality...")
try:
    eigen_centrality = nx.eigenvector_centrality(G, weight='weight', max_iter=250, tol=1e-3)
except nx.PowerIterationFailedConvergence:
    print("Не удалось сходиться за 1000 итераций, использую eigenvector_centrality_numpy...")
    eigen_centrality = nx.eigenvector_centrality_numpy(G, weight='weight')

top_eigen = sorted(eigen_centrality.items(), key=lambda x: x[1], reverse=True)[:10]


# c. Betweenness Centrality
print("\nВычисление Betweenness Centrality...")
betweenness_centrality = nx.betweenness_centrality(G, weight='weight', k=5, seed=42)
top_betweenness = sorted(betweenness_centrality.items(), key=lambda x: x[1], reverse=True)[:10]

# %%
# 2. Информационный анализ и маркетинг

def normalize_dict(d):
    max_val = max(d.values())
    min_val = min(d.values())
    return {k: (v - min_val) / (max_val - min_val) if max_val != min_val else 0 for k, v in d.items()}

print("\nВычисление комбинированного рейтинга...")
norm_weighted = normalize_dict(weighted_degrees)
norm_eigen = normalize_dict(eigen_centrality)
norm_betweenness = normalize_dict(betweenness_centrality)

combined_rating = {}
for node in tqdm(G.nodes(), desc="Вычисление комбинированного рейтинга"):
    combined_rating[node] = (norm_weighted.get(node, 0) +
                             norm_eigen.get(node, 0) +
                             norm_betweenness.get(node, 0)) / 3

top_combined = sorted(combined_rating.items(), key=lambda x: x[1], reverse=True)[:10]

# %%
# Функция для вычисления статистики по противникам для заданного игрока.
def get_opponent_stats(G, player):
    """
    Для заданного игрока собирает статистику по всем противникам:
      - 'count': количество партий (если атрибут 'count' есть, иначе считается 1 за ребро)
      - 'weight': суммарный вес ребер (например, общее время партии)
    Рассматриваются как исходящие, так и входящие ребра.
    """
    stats = {}
    # Обрабатываем исходящие ребра (player -> neighbor)
    for _, neighbor, data in G.out_edges(player, data=True):
        if neighbor not in stats:
            stats[neighbor] = {'count': 0, 'weight': 0}
        stats[neighbor]['count'] += data.get('count', 1)
        stats[neighbor]['weight'] += data.get('weight', 0)
    # Обрабатываем входящие ребра (neighbor -> player)
    for neighbor, _, data in G.in_edges(player, data=True):
        if neighbor not in stats:
            stats[neighbor] = {'count': 0, 'weight': 0}
        stats[neighbor]['count'] += data.get('count', 1)
        stats[neighbor]['weight'] += data.get('weight', 0)
    return stats

# 1) Топ-5 самых частых соперников для целевого игрока.
def get_top_opponents_by_frequency(G, player, top_n=5):
    stats = get_opponent_stats(G, player)
    # Используем tqdm для отслеживания сортировки (если число противников велико)
    sorted_stats = sorted(stats.items(), key=lambda x: x[1]['count'], reverse=True)
    return sorted_stats[:top_n]

# 2) Топ-5 соперников по весу для целевого игрока.
def get_top_opponents_by_weight(G, player, top_n=5):
    stats = get_opponent_stats(G, player)
    sorted_stats = sorted(stats.items(), key=lambda x: x[1]['weight'], reverse=True)
    return sorted_stats[:top_n]

# Функция, возвращающая топ-N соседей по частоте для заданного игрока.
def get_top_neighbors_by_frequency(G, player, top_n=5):
    stats = get_opponent_stats(G, player)
    sorted_stats = sorted(stats.items(), key=lambda x: x[1]['count'], reverse=True)
    return [n for n, stat in sorted_stats[:top_n]]

# 3) Поиск пути от source до target, проходящего только через «топовых» (по частоте) соперников.
def find_path_via_top_frequency(G, source, target, top_n=5, max_depth=10):
    best_path = None
    def dfs(current, path, depth):
        nonlocal best_path
        if depth > max_depth:
            return
        if current == target:
            best_path = path
            return
        # Получаем топовых соседей для текущего игрока
        top_neighbors = get_top_neighbors_by_frequency(G, current, top_n)
        for neighbor in tqdm(top_neighbors, desc=f"Расширение {current}", leave=False):
            if neighbor in path:
                continue  # избегаем циклов
            dfs(neighbor, path + [neighbor], depth + 1)
            if best_path is not None:
                return  # прекращаем, если путь найден
    dfs(source, [source], 0)
    return best_path


# %%
# Пример использования:
target = "pmp"
source = "king04"

target_player = "pmp"

path, total_weight = beam_search_max_path(G, source, target, beam_width=1000, max_depth=10)

if path:
    print("Найден путь:", path)
    print("Суммарный вес пути (в минутах):", total_weight)
else:
    print("Путь не найден.")

# Определяем топ-5 соперников целевого игрока
top_opponents = find_top_neighbors(G, target, top_k=5)
print("Топ-5 соперников целевого игрока:", top_opponents)

# Для каждого из топ-противников ищем путь от source, проходящий только через топ-связи
for opponent in top_opponents:
    path = find_path_via_tops(G, source, opponent, top_k=5, max_depth=10)
    if path:
        print(f"Путь от {source} до {opponent} через топ-связи: {path}")
    else:
        print(f"Путь от {source} до {opponent} через топ-связи не найден.")


print("Топ-10 игроков по суммарной весовой степени (Weighted Degree):")
for node, wd in top_weighted:
    print(f"{node}: {wd:.2f}")
    

print("\nТоп-10 игроков по Eigenvector Centrality:")
for node, ec in top_eigen:
    print(f"{node}: {ec:.4f}")
    

print("\nТоп-10 игроков по Betweenness Centrality:")
for node, bc in top_betweenness:
    print(f"{node}: {bc:.4f}")


print("\nМаркетинговая аналитика:")
for node, rating in top_combined:
    print(f"Игрок {node} является ключевым участником сообщества с комбинированным рейтингом {rating:.4f}.")


# 1) Топ-5 самых частых соперников целевого игрока.
top5_freq = get_top_opponents_by_frequency(G, target_player, top_n=5)
print("Топ-5 самых частых соперников для", target_player)
for opponent, stat in top5_freq:
    print(f"{opponent}: Частота = {stat['count']}, Общий вес = {stat['weight']}")

# 2) Топ-5 соперников по весу для целевого игрока.
top5_weight = get_top_opponents_by_weight(G, target_player, top_n=5)
print("\nТоп-5 соперников по весу для", target_player)
for opponent, stat in top5_weight:
    print(f"{opponent}: Общий вес = {stat['weight']}, Частота = {stat['count']}")


# %%
num_vertices = G.number_of_nodes()
print("Количество вершин графа G:", num_vertices)


