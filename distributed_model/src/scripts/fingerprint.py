# device_performance.py

import pandas as pd
import ast
import matplotlib.pyplot as plt
from pathlib import Path


def load_data(path: str) -> pd.DataFrame:
    """Загружает CSV в DataFrame."""
    return pd.read_csv(path)

def filter_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Оставляет только нужные столбцы."""
    return df[['Device memory', 'Hardware concurrency', 'Screen resolution']].copy()


def parse_screen_resolution(df: pd.DataFrame) -> pd.DataFrame:
    """Преобразует строку 'Screen resolution' в два числа: width и height."""
    df = df.copy()
    df['Screen resolution'] = df['Screen resolution'].apply(
        lambda x: ast.literal_eval(x) if isinstance(x, str) else x
    )
    df[['Screen width', 'Screen height']] = pd.DataFrame(
        df['Screen resolution'].to_list(), index=df.index
    )
    return df


def compute_pixels(df: pd.DataFrame) -> pd.DataFrame:
    """Добавляет столбец 'Screen pixels' = width * height."""
    df = df.copy()
    df['Screen pixels'] = df['Screen width'] * df['Screen height']
    return df


def compute_flops(df: pd.DataFrame, cpu_frequency: float) -> pd.DataFrame:
    """
    Добавляет столбец 'FLOPS' = Hardware concurrency * cpu_frequency.
    cpu_frequency в Гц (например, 2.5e9 для 2.5 GHz).
    """
    df = df.copy()
    df['FLOPS'] = df['Hardware concurrency'] * cpu_frequency
    return df


def compute_performance_coefficient(df: pd.DataFrame, scale: float = 1e4) -> pd.DataFrame:
    """
    Добавляет 'Performance coefficient' = (pixels * memory) / FLOPS * scale.
    scale по умолчанию 1e4 для удобства.
    """
    df = df.copy()
    df['Performance coefficient'] = (
        df['Screen pixels'] * df['Device memory'] / df['FLOPS']
    ) * scale
    return df


def compute_means(df: pd.DataFrame) -> pd.Series:
    """Вычисляет средние по ключевым столбцам."""
    cols = ['Device memory', 'Hardware concurrency', 'Screen pixels', 'FLOPS', 'Performance coefficient']
    return df[cols].mean()


def save_means(means: pd.Series, path: str):
    """Сохраняет средние значения в CSV."""
    means.to_csv(path, header=True)


def save_full(df: pd.DataFrame, path: str):
    """Сохраняет полный DataFrame с расчётами в CSV."""
    df.to_csv(path, index=False)


def plot_histogram_pixels(df: pd.DataFrame, mean_pixels: float):
    """Гистограмма распределения 'Screen pixels' с линией среднего."""
    plt.figure(figsize=(10, 6))
    plt.hist(df['Screen pixels'], bins=30, edgecolor='black', color='lightblue')
    plt.axvline(mean_pixels, color='red', linestyle='dashed', linewidth=2, label='Среднее пикселей')
    plt.title("Гистограмма количества пикселей")
    plt.xlabel("Screen pixels")
    plt.ylabel("Частота")
    plt.legend()
    plt.tight_layout()
    plt.show()


def show_head(df: pd.DataFrame, n: int = 5):
    """Печатает первые n строк ключевых столбцов."""
    cols = ['Device memory', 'Hardware concurrency', 'Screen resolution',
            'Screen pixels', 'FLOPS', 'Performance coefficient']
    print(df[cols].head(n))


def get_average_cores(df: pd.DataFrame | None = None, 
                      data_path: str | None = "./src/data/fingerprint/survey-and-browser-attributes-data.csv") -> float:
    """Вспомогательная: среднее число ядер (hardware concurrency)."""
    if df is None:
        df = load_data(data_path) 
    return df['Hardware concurrency'].mean()


def main():
    
    data_path = "./data/fingerprint/survey-and-browser-attributes-data.csv"
    df = load_data(data_path)

    # 2. Предобработка
    df = filter_columns(df)
    df = parse_screen_resolution(df)
    df = compute_pixels(df)

    # 3. Расчёты
    cpu_freq = 2.5e9  # 2.5 GHz
    df = compute_flops(df, cpu_freq)
    df = compute_performance_coefficient(df)

    # 4. Средние и сохранение
    means = compute_means(df)
    print("Средние значения:")
    print(means)
    save_means(means, "mean_device_performance.csv")
    save_full(df, "filtered_device_performance.csv")

    # 5. Визуализация и вывод
    plot_histogram_pixels(df, means['Screen pixels'])
    print("\nПервые 5 строк с расчётами:")
    show_head(df)


if __name__ == "__main__":
    main()
