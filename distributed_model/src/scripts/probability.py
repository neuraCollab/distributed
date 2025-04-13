import math

def compute_dp_flops(dp_flops_per_cycle, num_cores, frequency_ghz):
    """
    Вычисляет теоретическую вычислительную мощность в FLOPS для двойной точности,
    используя следующую формулу:
      P = dp_flops_per_cycle * num_cores * frequency_ghz * 1e9
    где:
      - dp_flops_per_cycle: число операций с плавающей точкой (64-bit) на такт (например, 8)
      - num_cores: количество ядер процессора
      - frequency_ghz: частота процессора в ГГц
    """
    return dp_flops_per_cycle * num_cores * frequency_ghz * 1e9

# Примерные параметры процессора Xeon E3-1275:
dp_flops_per_cycle = 8   # число операций с плавающей точкой (64-bit) за цикл
num_cores = 7.26            # количество ядер
frequency_ghz = 3.574    # частота в ГГц

def compute_delta_b(time_hour, optimal=13, max_deviation=12):
    """
    Вычисляет нормированное отклонение от оптимального часа атаки.
    
    Параметры:
      time_hour (float): заданное время атаки в часах (24-часовой формат, например, 14.5 для 14:30).
      optimal (float): оптимальный час атаки (по умолчанию 13, то есть 13:00).
      max_deviation (float): максимальное отклонение, при котором нормированное значение становится 0.
                             По умолчанию 12 часов.
    
    Формула:
       δ(b) = 1 - |time_hour - optimal| / max_deviation
    
    Возвращает:
      delta_b (float): нормированное значение отклонения (от 0 до 1).
    """
    deviation = abs(time_hour - optimal)
    delta_b = max(0, 1 - deviation / max_deviation)
    return delta_b

# Рассчитываем мощность P в FLOPS (для DP)
P = compute_dp_flops(dp_flops_per_cycle, num_cores, frequency_ghz)

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

country_counts = {
    "Iran": 328,
    "France": 168,
    "Russia": 203,
    "Argentina": 38,
    "Spain": 56,
    "Venezuela": 26,
    "Arab World": 25,
    "Brazil": 23,
    "Turkey": 11,
    "Poland": 9,
    "India": 12,
    "Libya": 6
}

country_coords = {
    "Iran": (35.6892, 51.3890),
    "France": (48.8566, 2.3522),
    "Russia": (55.7558, 37.6173),
    "Argentina": (-34.6037, -58.3816),
    "Spain": (40.4168, -3.7038),
    "Venezuela": (10.4806, -66.9036),
    "Arab World": (30.0444, 31.2357),
    "Brazil": (-23.5505, -46.6333),
    "Turkey": (41.0082, 28.9784),
    "Poland": (52.2297, 21.0122),
    "India": (28.6139, 77.2090),
    "Libya": (32.8872, 13.1913)
}

server_coords = country_coords["Russia"]

distances = {}
for country, coords in country_coords.items():
    distances[country] = haversine_distance(server_coords[0], server_coords[1], coords[0], coords[1])

def calculate_dnorm(country_counts, distances, a=1):
    # Сортируем страны по количеству участников по убыванию
    sorted_countries = sorted(country_counts.items(), key=lambda x: x[1], reverse=True)
    # Берем топ-5 стран
    top5_countries = [country for country, count in sorted_countries[:5]]
    # Получаем физические расстояния от сервера для этих стран
    d_top5 = [distances[country] for country in top5_countries]
    # Рассчитываем нормированное расстояние как сумму обратных расстояний
    # d_norm = a * (sum(1/d_i) по топ-5 странам)
    norm_sum = sum(1/d for d in d_top5 if d > 0)
    d_norm = a * (1 + norm_sum)
    return d_norm, top5_countries, d_top5

d_norm, top5_countries, d_top5 = calculate_dnorm(country_counts, distances, a=1)

def compute_probability(N, alpha, P, d_norm, time_hour, L, P_req, beta=5, gamma=1, optimal=13, max_deviation=12):
    """
    Расчет вероятности успеха атаки по следующей модели:
    
      X = (N * alpha * P * d_norm * delta_b * L) / P_req
      p = 1 / (1 + exp(-beta * (X - gamma)))
      
    Параметры:
      N      — количество участников сети.
      alpha  — доля доступной мощности устройств (от 0 до 1).
      P      — средняя вычислительная мощность одного участника (FLOPS).
      d_norm — нормированное среднее расстояние до серверов.
      delta_b — нормированное отклонение от оптимального часа атаки.
      L      — коэффициент распространения через лидеров (может быть 1 или отношение средней мощности лидеров к средней мощности участника).
      P_req  — требуемая мощность атаки (FLOPS).
      beta   — коэффициент крутизны логистической функции.
      gamma  — пороговое значение, при котором p = 0.5.
      
    Возвращает:
      X — отношение мощности сети к требуемой мощности.
      p — вероятность успеха атаки (значение от 0 до 1).
    """
    delta_b = compute_delta_b(time_hour, optimal, max_deviation)
    X = (N * alpha * P * d_norm * delta_b * L) / P_req
    p = 1 / (1 + math.exp(-beta * (X - gamma)))
    return X, p

# Параметры для compute_probability
N = 37788             # число участников сети
alpha = 0.3           # доступная мощность (30% от полной)
L = 1                 # коэффициент лидеров
P_req = 28e15          # 1 PFLOPS = 1*10^15 FLOPS
beta = 5              # коэффициент крутизны логистической функции
gamma = 1             # пороговое значение
time_hour = 14        # например, 14:00 нормированное отклонение от оптимального часа атаки

X, p_success = compute_probability(N, alpha, P, d_norm, time_hour, L, P_req, beta, gamma)
print("\nResults:")
print(f"X = {X:.6f}")
print(f"Probability of success, p = {p_success:.6f}")

# Функция для вычисления требуемого количества участников, чтобы добиться заданной вероятности успеха p_target
def required_N_for_probability(p_target, alpha, P, d_norm, delta_b, L, P_req, beta=5, gamma=1):
    # Вычисляем целевое значение X из логистической функции: X = gamma - ln((1/p)-1)/beta
    X_target = gamma - math.log((1/p_target) - 1) / beta
    # Из уравнения X = (N*alpha*P*d_norm*delta_b*L)/P_req решаем относительно N:
    N_required = (X_target * P_req) / (alpha * P * d_norm * delta_b * L)
    return N_required


# Вычисляем delta_b для заданного времени
delta_b = compute_delta_b(time_hour, optimal=13, max_deviation=12)
# Целевая вероятность успеха
p_target = 0.95
N_required = required_N_for_probability(p_target, alpha, P, d_norm, delta_b, L, P_req, beta, gamma)
print(f"\nКоличество участников сети, необходимое для достижения вероятности {p_target*100:.0f}%: {N_required:.0f}")