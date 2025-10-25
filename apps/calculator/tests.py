import pytest
from django.urls import reverse
from apps.users.models import User
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

def test_solver_contains_plot_data():
    """Проверяем что solve_neyman_pearson возвращает корректные данные для графика."""
    data = {
        'alpha': 0.1,
        'h0_dist': 'norm',
        'h0_param1': 0,
        'h0_param2': 1,
        'h1_dist': 'norm',
        'h1_param1': 1,
        'h1_param2': 1,
    }
    result = solve_neyman_pearson(data)
    assert 'plot_data' in result
    plot = result['plot_data']
    assert set(plot.keys()) == {'x', 'h0_pdf', 'h1_pdf', 'max_pdf'}
    assert len(plot['x']) == len(plot['h0_pdf']) == len(plot['h1_pdf'])
    # Все элементы должны быть float
    assert all(isinstance(v, float) for v in plot['x'][:5])
    assert all(isinstance(v, float) for v in plot['h0_pdf'][:5])
    assert plot['max_pdf'] >= max(plot['h0_pdf'][0], plot['h1_pdf'][0])

@pytest.mark.django_db
def test_calculate_view_returns_chart(client):
    """Интеграционный тест: POST к calculate должен вернуть HTML с canvas и json_script."""
    url = reverse('calculator:calculate')
    payload = {
        'alpha': 0.05,
        'h0_dist': 'norm', 'h0_param1': 0, 'h0_param2': 1,
        'h1_dist': 'norm', 'h1_param1': 1, 'h1_param2': 1,
    }
    resp = client.post(url, data=payload)
    assert resp.status_code == 200
    content = resp.content.decode('utf-8')
    assert 'distributionsChart' in content
    assert 'plot-data' in content  # id json_script
    # Проверим что присутствует ключ threshold в видимом HTML
    assert 'Порог (C):' in content

@pytest.mark.django_db
def test_calculate_view_twice(client):
    """Два последовательных запроса должны каждый раз возвращать график."""
    url = reverse('calculator:calculate')
    payload = {
        'alpha': 0.05,
        'h0_dist': 'norm', 'h0_param1': 0, 'h0_param2': 1,
        'h1_dist': 'norm', 'h1_param1': 1, 'h1_param2': 1,
    }
    first = client.post(url, data=payload)
    assert first.status_code == 200
    assert 'distributionsChart' in first.content.decode('utf-8')

    second = client.post(url, data=payload)
    assert second.status_code == 200
    assert 'distributionsChart' in second.content.decode('utf-8')

@pytest.mark.django_db
def test_calculate_negative_scale_returns_error(client):
    """Отрицательный scale должен вернуть partial с сообщением об ошибке и без графика."""
    url = reverse('calculator:calculate')
    payload = {
        'alpha': 0.05,
        'h0_dist': 'norm', 'h0_param1': 0, 'h0_param2': 1,
        'h1_dist': 'norm', 'h1_param1': 1, 'h1_param2': -1,
    }
    resp = client.post(url, data=payload)
    assert resp.status_code == 200
    html = resp.content.decode('utf-8')
    assert 'error' in html.lower() or 'Параметр scale/σ должен быть > 0' in html
    assert 'distributionsChart' not in html

@pytest.mark.django_db
def test_calculator_page_loads_for_anonymous(client):
    """Проверяем, что страница калькулятора открывается для анонимного пользователя."""
    url = reverse('calculator:page')
    response = client.get(url)
    assert response.status_code == 200

@pytest.mark.django_db
def test_history_page_requires_login(client):
    """Проверяем, что страница истории требует входа в систему."""
    url = reverse('calculator:history')
    response = client.get(url)
    # Ожидаем редирект (код 302) на страницу логина
    assert response.status_code == 302
    assert '/users/login/' in response.url

@pytest.mark.django_db
def test_history_page_loads_for_logged_in_user(client):
    """Проверяем, что страница истории доступна залогиненному пользователю."""
    # Создаем тестового пользователя
    user = User.objects.create_user(username='testuser', password='password123')
    # "Логиним" пользователя в тестовом клиенте
    client.force_login(user)
    
    url = reverse('calculator:history')
    response = client.get(url)
    # Теперь ожидаем код 200
    assert response.status_code == 200