import numpy as np
from scipy import stats
from scipy.optimize import brentq
from scipy.integrate import quad

def get_distribution(dist_name, param1, param2):
    """Возвращает объект распределения SciPy, проверяя допустимость параметров.

    param2 для всех используемых распределений является scale / sigma / шириной и должен быть > 0.
    """
    if param2 <= 0:
        raise ValueError("Параметр scale/σ/ширина має бути > 0")
    if dist_name == 'norm':
        return stats.norm(loc=param1, scale=param2)
    if dist_name == 'uniform':
        return stats.uniform(loc=param1, scale=param2)
    if dist_name == 'expon':
        return stats.expon(loc=param1, scale=param2)
    raise ValueError(f"Не підтримує розподіл: {dist_name}")

def solve_neyman_pearson(data: dict) -> dict:
    """Основная логика критерия Неймана–Пирсона (упрощённый вариант).

    Находит порог c такой, что P(X > c | H0) = alpha для одностороннего теста.
    Возвращает словарь с порогом, мощностью и данными для визуализации.
    """
    alpha = data['alpha']
    h0 = get_distribution(data['h0_dist'], data['h0_param1'], data['h0_param2'])
    h1 = get_distribution(data['h1_dist'], data['h1_param1'], data['h1_param2'])

    def find_c_func(c):
        return h0.sf(c) - alpha

    try:
        interval_start = h0.ppf(0.001)
        interval_end = h0.ppf(0.999)
        c_threshold = brentq(find_c_func, interval_start, interval_end)
    except ValueError:
        raise ValueError("Не вдалося знайти унікальний порог. Перевірте параметри розподілу и alpha.")

    power = h1.sf(c_threshold)
    gamma = 0.0  # В этой упрощённой реализации рандомизация не используется

    x = np.linspace(
        min(h0.ppf(0.001), h1.ppf(0.001)),
        max(h0.ppf(0.999), h1.ppf(0.999)),
        400
    )
    h0_pdf = h0.pdf(x)
    h1_pdf = h1.pdf(x)
    max_pdf = float(max(h0_pdf.max(), h1_pdf.max()))

    return {
        "threshold": round(c_threshold, 4),
        "power": round(power, 4),
        "gamma": round(gamma, 4),
        "plot_data": {
            "x": list(map(float, x)),
            "h0_pdf": list(map(float, h0_pdf)),
            "h1_pdf": list(map(float, h1_pdf)),
            "max_pdf": max_pdf,
        }
    }
