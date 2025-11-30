import numpy as np

def solve_neyman_pearson(data: dict) -> dict:
    matrix = np.array(data['matrix_input'])
    l_star = data['l_star']
    c_idx = int(data['controlled_state']) # 0 або 1
    u_idx = 1 - c_idx                     # 1 або 0
    
    candidates = []
    rows_count = matrix.shape[0]

    # --- ЕТАП 1: Збір усіх допустимих кандидатів ---

    # 1. Змішані стратегії (Ті, що лежать рівно на лінії L*)
    for i in range(rows_count):
        for j in range(i + 1, rows_count):
            c1 = matrix[i][c_idx]
            c2 = matrix[j][c_idx]
            
            # Шукаємо перетин з L*
            if (c1 - l_star) * (c2 - l_star) <= 0:
                if abs(c1 - c2) < 1e-9: continue # Уникаємо ділення на нуль
                    
                x = (l_star - c2) / (c1 - c2)
                
                if 0 <= x <= 1:
                    u1 = matrix[i][u_idx]
                    u2 = matrix[j][u_idx]
                    val_uncontrolled_mixed = x * u1 + (1 - x) * u2
                    
                    probs = [0.0] * rows_count
                    probs[i] = x
                    probs[j] = 1 - x

                    mixed_p_x = x * matrix[i][0] + (1 - x) * matrix[j][0]
                    mixed_p_y = x * matrix[i][1] + (1 - x) * matrix[j][1]

                    candidates.append({
                        'type': 'Змішана',
                        'probabilities': probs,
                        'value_controlled': l_star,
                        'value_uncontrolled': val_uncontrolled_mixed,
                        'point': {'x': mixed_p_x, 'y': mixed_p_y},
                        'parents': [
                            {'x': matrix[i][0], 'y': matrix[i][1]}, 
                            {'x': matrix[j][0], 'y': matrix[j][1]}
                        ],
                        'description': f"Стр. {i+1} + Стр. {j+1}"
                    })

    # 2. Чисті стратегії (Всі, що задовольняють умову <= L*)
    for i in range(rows_count):
        val_controlled = matrix[i][c_idx]
        val_uncontrolled = matrix[i][u_idx]
        
        # Головна умова: чи вписується стратегія в ліміт?
        if val_controlled <= l_star + 1e-9: # +epsilon для точності
            probs = [0.0] * rows_count
            probs[i] = 1.0
            
            candidates.append({
                'type': 'Чиста',
                'probabilities': probs,
                'value_controlled': val_controlled,
                'value_uncontrolled': val_uncontrolled,
                'point': {'x': matrix[i][0], 'y': matrix[i][1]},
                'description': f"Стр. {i+1}"
            })

    if not candidates:
        raise ValueError(f"Жодна стратегія не задовольняє умову L{c_idx+1} <= {l_star}")

    # --- ЕТАП 2: Вибір АБСОЛЮТНО найкращого рішення ---
    # Ми просто шукаємо мінімум втрат серед усіх допустимих варіантів.
    # Неважливо, на межі він чи всередині.
    
    best_solution = min(candidates, key=lambda x: x['value_uncontrolled'])
    
    # Якщо бот знайшов "змішану" стратегію, де ймовірність однієї компоненти = 1.0 (100%),
    # то це насправді "Чиста" стратегія.
    max_prob = max(best_solution['probabilities'])
    if best_solution['type'] == 'Змішана' and max_prob > 0.999:
        best_solution['type'] = 'Чиста'
        # Прибираємо лінію "батьків" для графіка, щоб малювалась тільки точка
        best_solution['parents'] = []

    # --- ЕТАП 3: Пошук еквівалентних стратегій ---
    # Якщо кілька стратегій дають однаковий мінімальний результат (наприклад, 1, 3, 4, 5)
    best_value = best_solution['value_uncontrolled']
    equivalent_solutions = [
        c for c in candidates 
        if abs(c['value_uncontrolled'] - best_value) < 1e-5
    ]
    
    # Формування красивого тексту
    if len(equivalent_solutions) > 1 and best_solution['type'] == 'Чиста':
        # Якщо це кілька чистих стратегій
        indices = []
        for eq in equivalent_solutions:
            if eq['type'] == 'Чиста':
                # Знаходимо індекс, де ймовірність 1.0
                idx = eq['probabilities'].index(1.0)
                indices.append(str(idx + 1))
        
        strategies_text = f"Стратегії: {', '.join(indices)} (100%)"
        # Для вектора ймовірностей беремо першу знайдену
        full_probs = best_solution['probabilities']
    else:
        # Звичайний вивід (змішана або одна чиста)
        parts = []
        for idx, prob in enumerate(best_solution['probabilities']):
            if prob > 0.001:
                parts.append(f"{prob:.3f} (Стр. {idx + 1})")
        strategies_text = ", ".join(parts)
        full_probs = best_solution['probabilities']


    # Дані для графіка
    all_points = [{'x': row[0], 'y': row[1]} for row in matrix]
    limit_line = {'value': l_star, 'axis': 'x' if c_idx == 0 else 'y'}
    mixed_segment = best_solution.get('parents', [])

    return {
        "best_value": round(best_value, 4),
        "controlled_limit": l_star,
        "controlled_col": c_idx + 1,
        "strategies_text": strategies_text,
        "matrix": matrix.tolist(),
        "is_mixed": best_solution['type'] == 'Змішана',
        "candidates": candidates,
        "full_probabilities": full_probs,
        "plot_data": {
            "all_points": all_points,
            "solution_point": best_solution['point'],
            "limit_line": limit_line,
            "mixed_segment": mixed_segment
        }
    }