import numpy as np

def solve_neyman_pearson(data: dict) -> dict:
    matrix = np.array(data['matrix_input'])
    l_star = data['l_star']
    c_idx = int(data['controlled_state']) # 0 або 1
    u_idx = 1 - c_idx                     # 1 або 0
    
    candidates = []
    rows_count = matrix.shape[0]

    # --- ЕТАП 1: Пошук усіх можливих точок перетину з лінією L* ---

    # 1. Перевіряємо змішані стратегії (розв'язуємо рівняння)
    for i in range(rows_count):
        for j in range(i + 1, rows_count):
            c1 = matrix[i][c_idx]
            c2 = matrix[j][c_idx]
            
            # Шукаємо перетин: одне значення >= L*, інше <= L*
            if (c1 - l_star) * (c2 - l_star) <= 0:
                # Уникаємо ділення на нуль
                if abs(c1 - c2) < 1e-9:
                    continue
                    
                # Формула з методички: x * c1 + (1-x) * c2 = l_star
                x = (l_star - c2) / (c1 - c2)
                
                if 0 <= x <= 1:
                    u1 = matrix[i][u_idx]
                    u2 = matrix[j][u_idx]
                    
                    val_uncontrolled_mixed = x * u1 + (1 - x) * u2
                    
                    # Список ймовірностей (floats)
                    probs = [0.0] * rows_count
                    probs[i] = x
                    probs[j] = 1 - x

                    # Координати
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
                        'on_boundary': True
                    })

    # 2. Перевіряємо чисті стратегії (тільки ті, що на лінії L* або в "безпечній" зоні)
    for i in range(rows_count):
        val_controlled = matrix[i][c_idx]
        val_uncontrolled = matrix[i][u_idx]
        
        # Точка на лінії L*
        if abs(val_controlled - l_star) < 1e-5:
            probs = [0.0] * rows_count
            probs[i] = 1.0
            candidates.append({
                'type': 'Чиста',
                'probabilities': probs,
                'value_controlled': val_controlled,
                'value_uncontrolled': val_uncontrolled,
                'point': {'x': matrix[i][0], 'y': matrix[i][1]},
                'on_boundary': True
            })
        # Точка строго менша за L*
        elif val_controlled < l_star:
             probs = [0.0] * rows_count
             probs[i] = 1.0
             candidates.append({
                'type': 'Чиста (внутрішня)',
                'probabilities': probs,
                'value_controlled': val_controlled,
                'value_uncontrolled': val_uncontrolled,
                'point': {'x': matrix[i][0], 'y': matrix[i][1]},
                'on_boundary': False
            })

    if not candidates:
        raise ValueError("Розв'язок не знайдено (L* занадто мале або матриця некоректна).")

    # --- ЕТАП 2: Вибір рішення як у методичці ---
    
    # Пріоритет: спочатку шукаємо ті, що 'on_boundary' (перетин з L*)
    boundary_candidates = [c for c in candidates if c['on_boundary']]
    
    if boundary_candidates:
        best_solution = min(boundary_candidates, key=lambda x: x['value_uncontrolled'])
    else:
        # Якщо перетинів немає, беремо найкращу внутрішню
        best_solution = min(candidates, key=lambda x: x['value_uncontrolled'])

    # Форматування тексту стратегій
    strategies_text_parts = []
    for idx, prob in enumerate(best_solution['probabilities']):
        if prob > 0.001:
            strategies_text_parts.append(f"{prob:.3f} (Стр. {idx + 1})")
    strategies_text = ", ".join(strategies_text_parts)

    # Дані для графіка
    all_points = [{'x': row[0], 'y': row[1]} for row in matrix]
    limit_line = {'value': l_star, 'axis': 'x' if c_idx == 0 else 'y'}
    mixed_segment = best_solution.get('parents', [])

    return {
        "best_value": round(best_solution['value_uncontrolled'], 4),
        "controlled_limit": l_star,
        "controlled_col": c_idx + 1,
        "strategies_text": strategies_text,
        "matrix": matrix.tolist(),
        "is_mixed": best_solution['type'] == 'Змішана',
        "candidates": candidates,
        
        # ОСЬ ЦЕЙ РЯДОК БУВ ПРОПУЩЕНИЙ, Я ЙОГО ПОВЕРНУВ:
        "full_probabilities": best_solution['probabilities'], 
        
        "plot_data": {
            "all_points": all_points,
            "solution_point": best_solution['point'],
            "limit_line": limit_line,
            "mixed_segment": mixed_segment
        }
    }