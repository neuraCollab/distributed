# %%
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, udf, size
from pyspark.sql.types import ArrayType, StringType
import json
import os

# 📂 Путь к данным
data_dir = os.path.join(os.getcwd(), './work/src/parquets')

# Получаем все файлы Parquet, которые начинаются с "lichess_part"
parquet_files = sorted([os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.startswith("lichess_part") and f.endswith(".parquet")])


# Создаем Spark-сессию (если еще не создана)
spark = SparkSession.builder.getOrCreate()

# Загрузка DataFrame из Parquet (пример, замените *parquet_files на ваш список файлов)
df = spark.read.parquet(*parquet_files)

# Загружаем teams_members.json и преобразуем его в словарь для быстрого поиска.
# Предполагается, что исходный JSON имеет формат:
# {
#   "team1": [ { "username": "UserA", ... }, { "username": "UserB", ... } ],
#   "team2": [ { "username": "UserC", ... }, ... ],
#    ...
# }
with open("./work/src/data/teams/teams_members.json", "r", encoding="utf-8") as f:
    teams_data = json.load(f)

# Преобразуем данные в словарь: username (lowercase) -> список team_id, в которых состоит пользователь.
user_to_teams = {}
for team_id, members in teams_data.items():
    for member in members:
        username = member.get("name")
        if username:
            user_to_teams.setdefault(username, []).append(team_id)

# Создаем broadcast-переменную для быстрого доступа к user_to_teams
broadcast_user_to_teams = spark.sparkContext.broadcast(user_to_teams)

# Определяем функцию для поиска команд по имени игрока
def lookup_teams(username):
    if username is None:
        return []
    return broadcast_user_to_teams.value.get(username.lower(), [])

# Регистрируем UDF, который возвращает массив строк
lookup_teams_udf = udf(lookup_teams, ArrayType(StringType()))

# Применяем UDF для колонок "white" и "black"
df_with_teams = df.withColumn("white_teams", lookup_teams_udf(col("white")))\
                  .withColumn("black_teams", lookup_teams_udf(col("black")))

# Выводим результат (можно заменить на .write... для сохранения)
# df_with_teams.show(truncate=False)

df_filtered = df_with_teams.filter(
    (size(col("white_teams")) > 0) | (size(col("black_teams")) > 0)
)

df_filtered.show(truncate=False)
print("Количество строк с ненулевыми командами:", df_filtered.count())


# %%
from pyspark.sql.functions import col, array_distinct, flatten, collect_list

# Извлекаем данные по игрокам, где для белых используем white_teams, для черных — black_teams
white_df = df_with_teams.select(col("white").alias("username"), col("white_teams").alias("teams"))
black_df = df_with_teams.select(col("black").alias("username"), col("black_teams").alias("teams"))

# Объединяем данные о белых и черных игроках
players_df = white_df.union(black_df)

# Группируем по имени игрока и объединяем массивы команд, убирая дубликаты
players_teams_df = players_df.groupBy("username") \
    .agg(array_distinct(flatten(collect_list("teams"))).alias("teams"))

# Фильтруем строки, где teams не пустой (size > 0)
filtered_players = players_teams_df.filter(size(col("teams")) > 0)

# Выводим отфильтрованные данные
filtered_players.show(truncate=False)

# Выводим количество таких строк
print("Количество строк с непустыми teams:", filtered_players.count())


# %%
from pyspark.sql.functions import explode, countDistinct

# Разворачиваем массив команд: получаем по одной строке на каждую (username, team)
players_exploded = filtered_players.select("username", explode("teams").alias("team"))

# Группируем по команде и считаем количество уникальных игроков, затем сортируем по убыванию
team_counts = players_exploded.groupBy("team") \
    .agg(countDistinct("username").alias("player_count")) \
    .orderBy("player_count", ascending=False)

# Выводим результат
team_counts.show(truncate=False)


# %%
print("Список всех команд:")
for team_name in teams_data.keys():
    print(team_name)


# %%
%pip install folium branca

# %%
# Импортируем необходимые библиотеки
import folium
import branca.colormap as cm

# Предположим, что team_counts – это Spark DataFrame с колонками "team" и "player_count",
# полученный в предыдущем коде:
# team_counts = players_exploded.groupBy("team") \
#     .agg(countDistinct("username").alias("player_count")) \
#     .orderBy("player_count", ascending=False)

# Собираем данные из Spark DataFrame в Python (это небольшой набор данных, как правило)
team_counts_list = team_counts.collect()

# Задаем сопоставление команды -> страна
team_to_country = {
    "arab-world-team": "Arab World",
    "russian-chess-players": "Russia",
    "iran": "Iran",
    "liga-de-ajdrez-de-bolivar": "Venezuela",
    "club-de-ajedrez-ulp-san-luis": "Argentina",
    "marianczellisci": "Poland",
    "levitov-chess": "Russia",
    "chess_pune": "India",
    "lichess-en-espanol": "Spain",
    "Vj95dS0R": "Russia",
    "satranc-medya-youtube": "Turkey",
    "chess-champions-league": "International",
    "akademi-catur-ariez-azman-acaa": "Indonesia",
    "francophone": "France",
    "libya-chess-competition-team": "Libya",
    "clube-online-xadrez-brasilia-df": "Brazil",
    "army-chess": "International",
    "colegas-de-kike": "Spain",
    "bangalore-chess-club": "India",
    "ciudad-ajedrez": "Spain",
    "dansk-skoleskak": "Denmark"
}

# Задаем сопоставление страны -> (широта, долгота) (примерные координаты)
country_coords = {
    "Arab World": (30.0444, 31.2357),   # Cairo, Egypt
    "Russia": (55.7558, 37.6176),         # Moscow, Russia
    "Iran": (32.4279, 53.6880),
    "Venezuela": (6.4238, -66.5897),
    "Argentina": (-34.6037, -58.3816),    # Buenos Aires, Argentina
    "Poland": (52.2297, 21.0122),         # Warsaw, Poland
    "India": (20.5937, 78.9629),
    "Spain": (40.4637, -3.7492),
    "Turkey": (38.9637, 35.2433),
    "Indonesia": (-0.7893, 113.9213),
    "France": (46.6034, 1.8883),
    "Libya": (26.3351, 17.2283),
    "Brazil": (-14.2350, -51.9253),
    "Denmark": (56.2639, 9.5018)
}

# Агрегируем общее количество участников по странам
# (пропускаем "International", если такие записи не нужны)
country_counts = {}
for row in team_counts_list:
    team = row["team"]
    count = row["player_count"]
    country = team_to_country.get(team)
    if country and country != "International":
        country_counts[country] = country_counts.get(country, 0) + count

# Если необходимо, можно вывести полученный словарь для проверки:
print("Участники по странам:")
for country, cnt in country_counts.items():
    print(f"{country}: {cnt}")

# Создаем карту Folium, центрированную примерно по центру мира
m = folium.Map(location=[20, 0], zoom_start=2)

# Определяем минимальное и максимальное количество участников для настройки шкалы цвета
min_count = min(country_counts.values())
max_count = max(country_counts.values())

# Создаем линейную цветовую шкалу
colormap = cm.linear.YlOrRd_09.scale(min_count, max_count)
colormap.caption = 'Количество участников в командах'
m.add_child(colormap)

# Добавляем круговые маркеры для каждой страны
for country, count in country_counts.items():
    coords = country_coords.get(country)
    if coords:
        # Вычисляем радиус: базовый размер плюс масштабирование по количеству участников
        radius = 10 + (count - min_count) / (max_count - min_count + 1) * 20
        folium.CircleMarker(
            location=coords,
            radius=radius,
            popup=f"{country}: {count}",
            color=colormap(count),
            fill=True,
            fill_color=colormap(count)
        ).add_to(m)

# Сохраняем карту в HTML
m.save("teams_map.html")
print("Карта сохранена в teams_map.html")



