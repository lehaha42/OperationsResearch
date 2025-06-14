from pulp import *


def main():
    # Параметры задачи
    K = 3  # количество типов товаров
    L = 2  # количество типов сырья
    N = 4  # количество пунктов в транспортном графе
    M = 5  # количество дней

    # Создаем модель
    model = LpProblem("Production_Transportation_Problem", LpMaximize)

    # Определяем переменные
    x = LpVariable.dicts("x", ((k, m) for k in range(1, K + 1) for m in range(1, M + 1)), lowBound=0, cat='Continuous')
    u = LpVariable.dicts("u", ((i, j) for i in range(1, N + 1) for j in range(1, N + 1)), cat='Binary')
    z = LpVariable.dicts("z", ((i, j) for i in range(1, N + 1) for j in range(1, N + 1)), lowBound=0, cat='Continuous')
    b = LpVariable.dicts("b", ((l, m) for l in range(1, L + 1) for m in range(1, M + 1)), lowBound=0, cat='Continuous')

    # Генерация случайных параметров (в реальной задаче нужно заменить на реальные данные)
    import numpy as np

    np.random.seed(0)

    p = np.random.rand(K, M) * 100  # цены реализации
    A = np.random.rand(L, K) * 0.5  # нормозатраты сырья
    y = np.random.rand(L, M) * 100  # поступление сырья
    d = np.random.rand(N, N) * 200  # пропускные способности
    Q = np.random.rand(K) * 500  # спрос на товары
    c = np.random.rand(N, N) * 50  # стоимости перевозок

    # Целевая функция: максимизация прибыли (выручка от продаж минус транспортные расходы)
    model += lpSum(p[k - 1][m - 1] * x[(k, m)] for k in range(1, K + 1) for m in range(1, M + 1)) - \
             lpSum(c[i - 1][j - 1] * u[(i, j)] for i in range(1, N + 1) for j in range(1, N + 1))

    # Ограничения

    # 1. Баланс сырья: запас в день m равен запасу в день m-1 плюс поступления минус расходы
    for l in range(1, L + 1):
        for m in range(1, M + 1):
            if m == 1:
                # Для первого дня начальный запас равен поступлениям минус расходы
                model += b[(l, m)] == y[l - 1][m - 1] - lpSum(A[l - 1][k - 1] * x[(k, m)] for k in range(1, K + 1))
            else:
                model += b[(l, m)] == b[(l, m - 1)] + y[l - 1][m - 1] - lpSum(
                    A[l - 1][k - 1] * x[(k, m)] for k in range(1, K + 1))

            # Запас сырья не может быть отрицательным
            model += b[(l, m)] >= 0

    # 2. Ограничения на производство: не превышать спрос
    for k in range(1, K + 1):
        model += lpSum(x[(k, m)] for m in range(1, M + 1)) <= Q[k - 1]

    # 3. Транспортные ограничения
    for i in range(1, N + 1):
        for j in range(1, N + 1):
            # Если есть перевозка, то объем должен быть положительным
            model += z[(i, j)] <= d[i - 1][j - 1] * u[(i, j)]
            # Связь между бинарной и непрерывной переменной
            model += z[(i, j)] >= 0
            model += z[(i, j)] <= d[i - 1][j - 1]

    # 4. Ограничения на поток товаров (упрощенное - в реальной задаче нужно уточнить)
    # Предположим, что пункт 1 - производитель, пункт N - потребитель
    # Все произведенные товары должны быть отправлены из пункта 1
    total_production = lpSum(x[(k, m)] for k in range(1, K + 1) for m in range(1, M + 1))
    model += lpSum(z[(1, j)] for j in range(2, N + 1)) >= total_production

    # Все товары должны прибыть в пункт N
    model += lpSum(z[(i, N)] for i in range(1, N)) >= total_production

    # Решаем задачу
    model.solve()

    # Выводим результаты
    print("Status:", LpStatus[model.status])
    print("Optimal Profit:", value(model.objective))

    # Выводим оптимальные значения переменных
    print("\nProduction:")
    for k in range(1, K + 1):
        for m in range(1, M + 1):
            print(f"x[{k}][{m}] = {x[(k, m)].varValue}")

    print("\nTransportation (binary):")
    for i in range(1, N + 1):
        for j in range(1, N + 1):
            if u[(i, j)].varValue > 0:
                print(f"u[{i}][{j}] = {u[(i, j)].varValue}")

    print("\nTransportation (volume):")
    for i in range(1, N + 1):
        for j in range(1, N + 1):
            if z[(i, j)].varValue > 0:
                print(f"z[{i}][{j}] = {z[(i, j)].varValue}")

    print("\nRaw Material Inventory:")
    for l in range(1, L + 1):
        for m in range(1, M + 1):
            print(f"b[{l}][{m}] = {b[(l, m)].varValue}")


if __name__ == '__main__':
    main()
