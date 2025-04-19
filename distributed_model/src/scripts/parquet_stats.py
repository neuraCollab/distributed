# analysis.py
import polars as pl
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from typing import Tuple


def get_data_dir(depth: int = 1) -> Path:
    """Возвращает путь к папке с parquet-файлами."""
    return Path(__file__).resolve().parents[depth] / "parquets"


def load_parquets(data_dir: Path, pattern: str = "lichess_part*.parquet") -> pl.DataFrame:
    """Считывает и конкатенирует все parquet-файлы по шаблону."""
    files = sorted(data_dir.glob(pattern))
    dfs = [pl.read_parquet(f) for f in files]
    return pl.concat(dfs, how="vertical")


def compute_avg_elo(df: pl.DataFrame) -> pl.DataFrame:
    """Вычисляет средний рейтинг белых и чёрных."""
    return df.select([
        pl.col("white_elo").mean().alias("avg_white_elo"),
        pl.col("black_elo").mean().alias("avg_black_elo")
    ])


def compute_moves_stats(df: pl.DataFrame) -> pl.DataFrame:
    """Статистика по числу ходов: min, max, mean, median."""
    return df.select([
        pl.col("moves_count").min().alias("min_moves"),
        pl.col("moves_count").max().alias("max_moves"),
        pl.col("moves_count").mean().alias("avg_moves"),
        pl.col("moves_count").median().alias("median_moves")
    ])


def top_eco(df: pl.DataFrame, top_n: int = 10) -> pl.DataFrame:
    """ТОП-n дебютов по ECO-коду."""
    return (df
            .group_by("eco")
            .agg(pl.count().alias("games"))
            .sort("games", descending=True)
            .head(top_n))


def compute_hourly_stats(df: pl.DataFrame) -> pl.DataFrame:
    """Число партий и среднее moves_count по часу UTC."""
    df2 = df.with_columns(pl.col("timestamp").dt.hour().alias("hour"))
    return (df2
            .group_by("hour")
            .agg([
                pl.count().alias("num_games"),
                pl.col("moves_count").mean().alias("avg_moves")
            ])
            .sort("hour"))


def plot_hourly(df_hour: pd.DataFrame):
    """Два графика: num_games и avg_moves по часам."""
    fig, ax = plt.subplots(1, 2, figsize=(14, 4))
    ax[0].bar(df_hour["hour"], df_hour["num_games"])
    ax[0].set(title="Количество партий по часам (UTC)",
              xlabel="Час", ylabel="Партий")
    ax[0].set_xticks(range(24))
    ax[1].plot(df_hour["hour"], df_hour["avg_moves"], marker="o")
    ax[1].set(title="Среднее число ходов по часам (UTC)",
              xlabel="Час", ylabel="Среднее ходов")
    ax[1].set_xticks(range(24))
    fig.tight_layout()
    plt.show()


def plot_box_moves(df: pl.DataFrame):
    """Boxplot распределения moves_count по часам."""
    df_pd = df.select(["hour", "moves_count"]).to_pandas()
    plt.figure(figsize=(12, 6))
    sns.boxplot(x="hour", y="moves_count", data=df_pd)
    plt.title("Распределение ходов по часам (UTC)")
    plt.show()


def plot_moves_hist(df: pl.DataFrame, min_moves: int = 0):
    """Гистограмма и KDE распределения длины партий."""
    df_pd = df.filter(pl.col("moves_count") >= min_moves).select("moves_count").to_pandas()
    fig, ax = plt.subplots(1, 2, figsize=(14, 4))
    ax[0].hist(df_pd["moves_count"], bins=50, alpha=0.7)
    ax[0].set(title="Гистограмма длины партий", xlabel="Ходов", ylabel="Частота")
    sns.kdeplot(df_pd["moves_count"], fill=True, ax=ax[1])
    ax[1].set(title="KDE распределение ходов", xlabel="Ходов")
    plt.tight_layout()
    plt.show()


def build_heatmap(df: pl.DataFrame, threshold: int = 100):
    """Тепловая карта: сколько партий каждого ECO по часам."""
    df2 = df.with_columns(pl.col("timestamp").dt.hour().alias("hour"))
    heat = (df2
            .group_by(["hour", "eco"])
            .agg(pl.count().alias("games"))
            .pivot(index="hour", columns="eco", values="games")
            .fill_null(0)
            .sort("hour")
            .to_pandas())
    # отбираем только дебюты с суммарно > threshold партий
    heat = heat.loc[:, heat.sum() > threshold]
    plt.figure(figsize=(14, 6))
    sns.heatmap(heat, cmap="YlGnBu")
    plt.title("Активность по часам и дебютам (ECO)")
    plt.show()


def compute_top_players(df: pl.DataFrame, top_n: int = 20) -> pl.DataFrame:
    """Топ игроков по числу партий с доп. метриками."""
    df2 = df.select([
        pl.col("white").alias("player"), pl.col("moves_count")
    ]).vstack(
        df.select([pl.col("black").alias("player"), pl.col("moves_count")])
    )
    stats = (df2.group_by("player")
             .agg([
                 pl.count().alias("games_played"),
                 pl.col("moves_count").mean().alias("avg_moves"),
                 pl.col("moves_count").median().alias("median_moves"),
                 pl.col("moves_count").max().alias("max_moves")
             ])
             .sort("games_played", descending=True)
             .head(top_n))
    return stats.with_columns([
        (pl.col("games_played") * pl.col("avg_moves")).alias("move_volume"),
        (pl.col("max_moves") - pl.col("median_moves")).alias("variability_score"),
        (pl.col("avg_moves") > 70).alias("long_games")
    ])


def save_player_hour_activity(df: pl.DataFrame, top_stats: pl.DataFrame, out_csv: str):
    """Сохраняет CSV с активностью игроков по часам."""
    df2 = df.select([pl.col("white").alias("player"), pl.col("timestamp").dt.hour().alias("hour")]) \
            .vstack(df.select([pl.col("black").alias("player"), pl.col("timestamp").dt.hour().alias("hour")]))
    ph = (df2.group_by(["player", "hour"])
          .agg(pl.count().alias("games_in_hour")))
    ph = ph.join(top_stats.select(["player", "avg_moves"]), on="player", how="inner")
    ph = ph.with_columns((pl.col("games_in_hour") * pl.col("avg_moves")).alias("activity_score"))
    ph.write_csv(out_csv)
    print(f"Сохранено: {out_csv}")


def find_peak_load(
    hourly_stats: pl.DataFrame,
    dist_df: pl.DataFrame,
    hour_col: str = "hour",
    games_col: str = "num_games",
    avg_moves_col: str = "avg_moves",
    dist_col: str = "moves_fraction"
) -> Tuple[int, float, dict]:
    """Вычисляет час пикового load = num_games * avg_moves * moves_fraction."""
    df_load = hourly_stats.join(dist_df, on=hour_col, how="inner")
    df_load = df_load.with_columns(((pl.col(games_col)
                                      * pl.col(avg_moves_col)
                                      * pl.col(dist_col)).alias("load")))
    loads = {int(r[0]): float(r[1]) for r in df_load.select([hour_col, "load"]).iter_rows()}
    peak = max(loads, key=loads.get)
    return peak, loads[peak], loads


def get_peak_hour(df: pl.DataFrame | None = None ) -> int:
    """Утилита: возвращает час пикового load для DataFrame партий."""
    if df is None:
        data_dir = get_data_dir()
        df = load_parquets(data_dir)
    # Убираем дубликаты по timestamp и player
    hourly = compute_hourly_stats(df)
    moves_by_hour = (df.with_columns(pl.col("timestamp").dt.hour().alias("hour"))
                     .group_by("hour")
                     .agg(pl.col("moves_count").sum().alias("total_moves"))
                     .sort("hour"))
    total = moves_by_hour["total_moves"].sum()
    dist_df = moves_by_hour.with_columns((pl.col("total_moves") / total).alias("moves_fraction")) \
                           .select(["hour", "moves_fraction"])
    return find_peak_load(hourly, dist_df)

# %% Визуализация пикового load
if __name__ == "__main__":
    # 1. Загрузка
    data_dir = get_data_dir()
    df = load_parquets(data_dir)

    # 2. Базовые метрики
    print("Avg ELO:\n", compute_avg_elo(df))
    print("Moves stats:\n", compute_moves_stats(df))
    print("Top ECO:\n", top_eco(df))

    # 3. Временные метрики и графики
    hourly = compute_hourly_stats(df)
    plot_hourly(hourly)
    plot_box_moves(df)
    plot_moves_hist(df, min_moves=5)
    build_heatmap(df)

    # 4. Игроки
    top_players = compute_top_players(df)
    print(top_players)
    save_player_hour_activity(df, top_players, "player_hour_activity.csv")

    # 5. Пиковый час
    print("Peak hour:", get_peak_hour(df))
