# %%
import polars as pl
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# 📂 Путь к данным
data_dir = Path(__file__).resolve().parents[1] / "./work/src/parquets"
parquet_files = sorted(data_dir.glob("lichess_part*.parquet"))
print(f"🔍 Найдено файлов: {len(parquet_files)}")

# %%
# 📥 Чтение и объединение
dfs = [pl.read_parquet(f) for f in parquet_files]
df = pl.concat(dfs, how="vertical")
print(f"\n🎮 Всего партий: {df.shape[0]}")
df.head(5)

# %%
# 📊 Средние рейтинги
avg_elo = df.select([
pl.col("white_elo").mean().alias("avg_white_elo"),
pl.col("black_elo").mean().alias("avg_black_elo")
])
print("\n📈 Средние рейтинги:")
print(avg_elo)

# %%
# ♟️ Статистика по числу ходов
moves_stats = df.select([
pl.col("moves_count").min().alias("min_moves"),
pl.col("moves_count").max().alias("max_moves"),
pl.col("moves_count").mean().alias("avg_moves"),
pl.col("moves_count").median().alias("median_moves")
])
print("\n♟️ Статистика по числу ходов:")
print(moves_stats)

# %%
# 📚 ТОП-10 дебютов по ECO
eco_stats = df.group_by("eco").len().sort("len", descending=True).head(10)
print("\n📚 ТОП-10 дебютов (по ECO):")
print(eco_stats)

# %%
# ⏰ Активность по времени и среднее число ходов
df = df.with_columns([
    pl.col("timestamp").dt.hour().alias("hour")
])

hourly_stats = (
    df.group_by("hour")
    .agg([
        pl.len().alias("num_games"),
        pl.col("moves_count").mean().alias("avg_moves")
    ])
    .sort("hour")
)

print("\n⏰ Активность и среднее число ходов по времени (UTC):")
print(hourly_stats)

# %%
# 📈 Графики
hourly_pd = hourly_stats.to_pandas()

# График 1: количество партий по часам
plt.figure(figsize=(10, 4))
plt.bar(hourly_pd["hour"], hourly_pd["num_games"], color="skyblue")
plt.title("📊 Количество партий по часам (UTC)")
plt.xlabel("Час")
plt.ylabel("Количество партий")
plt.xticks(range(0, 24))
plt.grid(True)
plt.tight_layout()
plt.show()

# %%
# График 2: среднее число ходов по часам
plt.figure(figsize=(10, 4))
plt.plot(hourly_pd["hour"], hourly_pd["avg_moves"], marker="o", color="green")
plt.title("📈 Среднее число ходов по часам (UTC)")
plt.xlabel("Час")
plt.ylabel("Среднее число ходов")
plt.xticks(range(0, 24))
plt.grid(True)
plt.tight_layout()
plt.show()

# %%
# 📦 BOXPLOT: Распределение количества ходов по часам
df_pd = df.select(["hour", "moves_count"]).drop_nulls().to_pandas()

plt.figure(figsize=(12, 6))
sns.boxplot(x="hour", y="moves_count", data=df_pd, palette="Set3")
plt.title("📦 Распределение числа ходов по часам (UTC)")
plt.xlabel("Час")
plt.ylabel("Число ходов в партии")
plt.grid(True)
plt.tight_layout()
plt.show()

# %%
# 📊 Гистограмма общего распределения длины партий
plt.figure(figsize=(10, 4))
plt.hist(df_pd["moves_count"], bins=50, color="mediumpurple", edgecolor="black", alpha=0.8)
plt.title("📊 Распределение длины партий (moves_count)")
plt.xlabel("Число ходов")
plt.ylabel("Количество партий")
plt.grid(True)
plt.tight_layout()
plt.show()

# %%
# Отфильтруем партии с менее чем 5 ходами
df = df.filter(pl.col("moves_count") >= 5)
df_pd = df.select(["moves_count"]).to_pandas()

# KDE-график распределения длины партий
plt.figure(figsize=(10, 4))
sns.kdeplot(df_pd["moves_count"], fill=True, color="teal")
plt.title("📈 KDE-график: Распределение длины партий (moves_count)")
plt.xlabel("Число ходов")
plt.ylabel("Плотность")
plt.grid(True)
plt.tight_layout()
plt.show()

# %%
# Группировка: сколько партий в час по каждому ECO
heatmap_df = (
    df.group_by(["hour", "eco"])
    .len()
    .pivot(values="len", index="hour", columns="eco")
    .fill_null(0)
    .sort("hour")
    .to_pandas()
)

heatmap_df = heatmap_df.loc[:, (heatmap_df.sum() > 100)]  # например, > 100 партий всего

# Строим тепловую карту
plt.figure(figsize=(14, 6))
sns.heatmap(heatmap_df.set_index("hour"), cmap="YlGnBu", linewidths=0.5, linecolor='white')
plt.title("🌐 Активность по часам и дебютам (ECO)")
plt.xlabel("ECO-код (дебют)")
plt.ylabel("Час UTC")
plt.tight_layout()
plt.show()

# %%
# Объединяем белых и чёрных в один столбец "player"
df_players = df.select([
    pl.col("white").alias("player"),
    pl.col("moves_count")
]).vstack(
    df.select([
        pl.col("black").alias("player"),
        pl.col("moves_count")
    ])
)

# Группировка по игроку + статистика
top_players_stats = (
    df_players.group_by("player")
    .agg([
        pl.len().alias("games_played"),
        pl.col("moves_count").mean().alias("avg_moves"),
        pl.col("moves_count").median().alias("median_moves"),
        pl.col("moves_count").max().alias("max_moves")
    ])
    .sort("games_played", descending=True)
    .head(20)  # топ-20 игроков
)

top_players_stats = top_players_stats.with_columns([
    (pl.col("games_played") * pl.col("avg_moves")).alias("move_volume"),
    (pl.col("max_moves") - pl.col("median_moves")).alias("variability_score"),
    (pl.col("avg_moves") > 70).alias("long_games")
])

print(top_players_stats)

# %%
# Подсчёт количества партий по каждому игроку по каждому часу
df_players = df.select([
    pl.col("white").alias("player"),
    pl.col("hour")
]).vstack(
    df.select([
        pl.col("black").alias("player"),
        pl.col("hour")
    ])
)

player_hour_stats = (
    df_players.group_by(["player", "hour"])
    .agg([
        pl.len().alias("games_in_hour")
    ])
)

player_hour_stats = player_hour_stats.join(
    top_players_stats.select(["player", "avg_moves"]),
    on="player",
    how="inner"
)

player_hour_stats = player_hour_stats.with_columns([
    (pl.col("games_in_hour") * pl.col("avg_moves")).alias("activity_score")
])

player_hour_stats.write_csv("player_hour_activity.csv")
print("\n✅ Сохранено в player_hour_activity.csv")
