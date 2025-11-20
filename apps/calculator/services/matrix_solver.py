import math

def solve_strategy_matrix(strategies: dict, controlled_state: int, L_star: float):
    names = list(strategies.keys())
    points = [strategies[n] for n in names]
    n = len(points)

    controlled_idx = controlled_state
    uncontrolled_idx = 1 - controlled_idx

    best_solution = None
    best_J = math.inf
    best_desc = ""

    # 1) Чисті стратегії з L == L*
    for i, (L_i, J_i) in enumerate(points):
        if abs(L_i - L_star) < 1e-9:
            if J_i < best_J:
                best_J = J_i
                probs = {name: 0.0 for name in names}
                probs[names[i]] = 1.0
                best_solution = probs
                best_desc = f"pure {names[i]} (L exactly = L*)"

    # 2) Пари (i,j) для змішаних стратегій
    for i in range(n):
        Li = points[i][controlled_idx]
        Ji = points[i][uncontrolled_idx]
        for j in range(i+1, n):
            Lj = points[j][controlled_idx]
            Jj = points[j][uncontrolled_idx]

            denom = Li - Lj
            if abs(denom) < 1e-12:
                continue

            x = (L_star - Lj) / denom
            if x < -1e-9 or x > 1+1e-9:
                continue

            x_clipped = max(0.0, min(1.0, x))
            Jx = x_clipped * Ji + (1 - x_clipped) * Jj

            if Jx < best_J - 1e-12:
                best_J = Jx
                probs = {name: 0.0 for name in names}
                probs[names[i]] = round(float(x_clipped), 6)
                probs[names[j]] = round(1.0 - float(x_clipped), 6)
                best_solution = probs
                best_desc = f"mix {names[i]} (x={round(x_clipped,4)}) and {names[j]}"

    if best_solution is None:
        raise ValueError("Розв'язок не знайдено: немає пари чи чистої стратегії, що дає L* на відрізках.")

    return {
        "best_J": best_J,
        "best_desc": best_desc,
        "best_solution": best_solution,
        "strategies": strategies,
        "controlled_state": controlled_state,
        "L_star": L_star,
    }
