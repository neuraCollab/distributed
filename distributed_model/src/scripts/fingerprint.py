# %%
import pandas as pd
import ast
import matplotlib.pyplot as plt

# %% Загружаем данные
df = pd.read_csv("./work/src/data/fingerprint/survey-and-browser-attributes-data.csv")

# %% Оставляем только необходимые столбцы для оценки производительности ПК
df_filtered = df[['Device memory', 'Hardware concurrency', 'Screen resolution']].copy()

# %% Обрабатываем 'Screen resolution', преобразуем строку в список чисел
df_filtered['Screen resolution'] = df_filtered['Screen resolution'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

# %% Разделяем на ширину и высоту экрана
df_filtered[['Screen width', 'Screen height']] = pd.DataFrame(df_filtered['Screen resolution'].to_list(), index=df_filtered.index)

# %% Вычисляем количество пикселей
df_filtered['Screen pixels'] = df_filtered['Screen width'] * df_filtered['Screen height']


# %% Фильтруем строки, где количество пикселей попадает в диапазон ±20%
matching_range = df_filtered

# %% Добавляем колонку с расчетом FLOPS (предположим, что FLOPS = Hardware concurrency * частота процессора)
# Для гипотетической частоты процессора, допустим, 2.5 GHz (2.5 * 10^9 операций в секунду)
cpu_frequency = 2.5e9  # 2.5 GHz

# %% Рассчитываем FLOPS
matching_range['FLOPS'] = matching_range['Hardware concurrency'] * cpu_frequency

# %% Добавляем коэффициент производительности: Screen pixels * Device memory / FLOPS
matching_range['Performance coefficient'] = (matching_range['Screen pixels'] * matching_range['Device memory']) / matching_range['FLOPS'] * 1e4  # Умножаем на 10^4 для удобства

# %% Вычисляем средние значения для новых колонок
# Вычисляем средние значения для новых колонок
mean_values = matching_range[['Device memory', 'Hardware concurrency', 'Screen pixels', 'FLOPS', 'Performance coefficient']].mean()

# %% Выводим средние значения
print("Средние значения для устройств")
print(mean_values)

# Сохраняем средние значения в CSV файл
mean_values.to_csv("mean_device_performance.csv", header=True)

# %% Визуализируем данные
plt.figure(figsize=(10, 6))

# Плотим гистограмму для "Screen pixels"
plt.hist(matching_range['Screen pixels'], bins=30, edgecolor='black', color='lightblue')
plt.axvline(x=mean_values['Screen pixels'], color='red', linestyle='dashed', linewidth=2, label='Среднее значение пикселей')

# Плотим гистограмму для других столбцов
plt.title("Гистограмма количества пикселей для устройств в диапазоне ±20% от 1,254,486")
plt.xlabel("Количество пикселей")
plt.ylabel("Частота")
plt.legend()

# Показать график
plt.tight_layout()
plt.show()

# %% Выводим первые 5 значений с новыми колонками
print("Первые 5 строк с расчетами:")
print(matching_range[['Device memory', 'Hardware concurrency', 'Screen resolution', 'Screen pixels', 'FLOPS', 'Performance coefficient']].head())

# %% Сохраняем результат в новый CSV файл
matching_range.to_csv("filtered_device_performance.csv", index=False)
