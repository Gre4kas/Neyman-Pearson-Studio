import pytest
from .services.neyman_pearson_solver import solve_neyman_pearson

def test_solver_simple_normal_case():
    """
    Тестируем решатель на простом случае двух нормальных распределений.
    H0: N(0, 1) vs H1: N(1, 1) с alpha=0.05
    Ожидаемые значения можно рассчитать заранее.
    Порог для одностороннего теста N(0,1) при alpha=0.05 равен ~1.645.
    Мощность = P(Z > 1.645 | H1), где Z ~ N(1, 1). Это P(Z-1 > 0.645) = 1 - Ф(0.645) ≈ 0.259.
    """
    # 1. Подготовка данных (Arrange)
    test_data = {
        'alpha': 0.05,
        'h0_dist': 'norm',
        'h0_param1': 0,
        'h0_param2': 1,
        'h1_dist': 'norm',
        'h1_param1': 1,
        'h1_param2': 1,
    }

    # 2. Выполнение действия (Act)
    result = solve_neyman_pearson(test_data)

    # 3. Проверка результата (Assert)
    assert 'threshold' in result
    assert 'power' in result
    
    # Используем pytest.approx для сравнения чисел с плавающей точкой
    assert result['threshold'] == pytest.approx(1.645, abs=0.01)
    assert result['power'] == pytest.approx(0.259, abs=0.01)