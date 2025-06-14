import numpy as np
from scipy.optimize import linprog
from pyvis.network import Network
from json import loads, dumps
from random import randint


def optimize_production_transport_linprog(
        p,  # цены реализации товаров [k]
        b,  # запасы сырья [l]
        A,  # нормы расхода сырья [l][k]
        d,  # пропускная способность дуг [i][j] (матрица)
        Q,  # спрос на товары {потребитель: {k: количество}}
        c,  # стоимость перевозок [i][j] (матрица)
        nodes,  # список всех узлов графа
        source_node,  # узел производства
        consumers  # словарь {потребитель: узел}
):
    """
    Оптимизация производства и транспортировки с использованием linprog.
    Корректно обрабатывает случаи недостатка сырья.
    """

    # Проверки входных данных
    num_raw_materials = len(b)
    num_products = len(p)
    num_nodes = len(nodes)

    assert len(A) == num_raw_materials
    for row in A:
        assert len(row) == num_products

    # Проверяем матрицы d и c
    assert d.shape == (num_nodes, num_nodes)
    assert c.shape == (num_nodes, num_nodes)

    # 1. Создаем переменные:
    # x[k] - производство товара k
    # y[k,i,j] - перевозка товара k из узла i в узел j

    # Определяем количество переменных
    num_x = num_products
    num_y = num_products * np.count_nonzero(d)
    total_vars = num_x + num_y

    # 2. Целевая функция: максимизация прибыли = доход - транспортные расходы
    # Преобразуем к задаче минимизации: -прибыль
    c_obj = np.zeros(total_vars)

    # Доход от производства (первые num_x переменных)
    c_obj[:num_x] = -np.array(p)  # отрицательный доход (так как минимизируем)

    # Транспортные расходы (переменные y)
    y_idx = 0
    for k in range(num_products):
        for i in range(num_nodes):
            for j in range(num_nodes):
                if d[i, j] > 0:
                    c_obj[num_x + y_idx] = c[i, j] / max(d[i, j], 1e-6)  # переменные затраты
                    y_idx += 1

    # 3. Ограничения

    # Матрица ограничений и вектор правой части
    A_ub = []  # неравенства
    b_ub = []
    A_eq = []  # равенства
    b_eq = []

    # 3.1 Ограничения по сырью (A*x <= b)
    for l in range(num_raw_materials):
        row = np.zeros(total_vars)
        row[:num_x] = A[l]
        A_ub.append(row)
        b_ub.append(b[l])

    # 3.2 Ограничения по спросу (для каждого потребителя и товара)
    # Изменено: теперь это неравенства (<= вместо ==), чтобы допускать неполное удовлетворение спроса
    for consumer, demand_dict in Q.items():
        consumer_node = consumers[consumer]
        for k, quantity in demand_dict.items():
            if quantity > 0:
                # Сумма входящих потоков <= спроса (можем удовлетворить частично)
                row = np.zeros(total_vars)
                y_idx = 0
                for k2 in range(num_products):
                    for i in range(num_nodes):
                        for j in range(num_nodes):
                            if d[i, j] > 0:
                                if k2 == k and j == consumer_node:
                                    row[num_x + y_idx] = 1  # sum(y) <= demand
                                y_idx += 1
                A_ub.append(row)
                b_ub.append(quantity)

    # 3.3 Баланс потоков для каждого товара и узла
    for k in range(num_products):
        for node in range(num_nodes):
            if node == source_node:
                # Производство = исходящий поток
                row = np.zeros(total_vars)
                row[k] = -1  # -x[k]

                y_idx = 0
                for k2 in range(num_products):
                    for i in range(num_nodes):
                        for j in range(num_nodes):
                            if d[i, j] > 0:
                                if k2 == k and i == source_node:
                                    row[num_x + y_idx] = 1  # sum(y)
                                y_idx += 1
                A_eq.append(row)
                b_eq.append(0)
            elif node in consumers.values():
                continue  # уже обработали в спросе
            else:
                # Входящий поток = исходящий для промежуточных узлов
                row = np.zeros(total_vars)
                y_idx = 0
                for k2 in range(num_products):
                    for i in range(num_nodes):
                        for j in range(num_nodes):
                            if d[i, j] > 0:
                                if k2 == k:
                                    if j == node:
                                        row[num_x + y_idx] = 1  # inflow
                                    if i == node:
                                        row[num_x + y_idx] = -1  # outflow
                                y_idx += 1
                A_eq.append(row)
                b_eq.append(0)

    # 3.4 Ограничения пропускной способности
    for i in range(num_nodes):
        for j in range(num_nodes):
            if d[i, j] > 0:
                row = np.zeros(total_vars)
                y_idx = 0
                for k in range(num_products):
                    for i2 in range(num_nodes):
                        for j2 in range(num_nodes):
                            if d[i2, j2] > 0:
                                if i2 == i and j2 == j:
                                    row[num_x + y_idx] = 1  # sum(y) <= d[i,j]
                                y_idx += 1
                A_ub.append(row)
                b_ub.append(d[i, j])

    # Преобразуем в numpy массивы
    A_ub = np.array(A_ub) if len(A_ub) > 0 else None
    b_ub = np.array(b_ub) if len(b_ub) > 0 else None
    A_eq = np.array(A_eq) if len(A_eq) > 0 else None
    b_eq = np.array(b_eq) if len(b_eq) > 0 else None

    # Границы переменных (все >= 0)
    bounds = [(0, None) for _ in range(total_vars)]

    # Решаем задачу линейного программирования
    res = linprog(c=c_obj, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                  bounds=bounds, method='highs')

    # Даже если решение не оптимальное, попробуем использовать лучшее найденное
    if not res.success:
        print(f"Предупреждение: решение может быть неоптимальным. Статус: {res.message}")
        if not hasattr(res, 'x'):
            raise ValueError("Не удалось найти допустимое решение")

    # Разбираем решение
    solution = res.x if res.success else np.zeros(total_vars)
    x_sol = solution[:num_x]
    y_sol = solution[num_x:]

    # Собираем результаты
    results = {
        'status': res.message if res.success else 'suboptimal',
        'total_profit': -res.fun if res.success else 0,
        'production': {},
        'transport': {},
        'raw_material_used': {},
        'demand_satisfaction': {},
        'raw_material_utilization': {}  # Добавляем информацию об использовании сырья
    }

    # Производство
    for k in range(num_products):
        results['production'][k] = max(0, x_sol[k])

    # Использование сырья и уровень использования
    for l in range(num_raw_materials):
        used = sum(A[l][k] * results['production'][k] for k in range(num_products))
        results['raw_material_used'][l] = min(used, b[l])
        results['raw_material_utilization'][l] = min(used / b[l], 1.0) if b[l] > 0 else 0.0

    # Транспортные потоки
    y_idx = 0
    for k in range(num_products):
        for i in range(num_nodes):
            for j in range(num_nodes):
                if d[i, j] > 0:
                    val = max(0, y_sol[y_idx])
                    if val > 1e-6:
                        results['transport'][(k, nodes[i], nodes[j])] = val
                    y_idx += 1

    # Удовлетворение спроса
    for consumer, demand_dict in Q.items():
        results['demand_satisfaction'][consumer] = {}
        consumer_node = consumers[consumer]
        for k in demand_dict:
            inflow = sum(
                val for (k2, i, j), val in results['transport'].items()
                if k2 == k and j == nodes[consumer_node]
            )
            results['demand_satisfaction'][consumer][k] = inflow

    return results


def main():
    # Параметры задачи
    p = [10, 15, 8]  # цены на товары
    b = [50, 80, 40]  # запасы сырья
    A = [[2, 3, 1], [1, 2, 2], [0, 1, 1]]  # расход

    # Узлы сети
    nodes = ['factory', 'hub1', 'hub2', 'store1', 'store2', 'store3']
    node_to_idx = {node: idx for idx, node in enumerate(nodes)}
    source_node = node_to_idx['factory']

    # Потребители
    consumers = {
        'retailer1': node_to_idx['store1'],
        'retailer2': node_to_idx['store2'],
        'wholesaler': node_to_idx['store3']
    }

    # Матрица пропускных способностей
    d = np.zeros((len(nodes), len(nodes)))
    d[node_to_idx['factory'], node_to_idx['hub1']] = 50
    d[node_to_idx['factory'], node_to_idx['hub2']] = 40
    d[node_to_idx['factory'], node_to_idx['store1']] = 30
    d[node_to_idx['hub1'], node_to_idx['store2']] = 35
    d[node_to_idx['hub2'], node_to_idx['store3']] = 45
    d[node_to_idx['hub1'], node_to_idx['store3']] = 25

    # Матрица стоимостей перевозок (переменные затраты)
    c = np.zeros((len(nodes), len(nodes)))
    c[node_to_idx['factory'], node_to_idx['hub1']] = 0.5
    c[node_to_idx['factory'], node_to_idx['hub2']] = 0.6
    c[node_to_idx['factory'], node_to_idx['store1']] = 1.0
    c[node_to_idx['hub1'], node_to_idx['store2']] = 0.3
    c[node_to_idx['hub2'], node_to_idx['store3']] = 0.4
    c[node_to_idx['hub1'], node_to_idx['store3']] = 0.35

    # Спрос
    Q = {
        'retailer1': {0: 20, 1: 10, 2: 5},
        'retailer2': {0: 15, 1: 20},
        'wholesaler': {1: 30, 2: 25}
    }

    # Запуск оптимизации
    try:
        results = optimize_production_transport_linprog(
            p, b, A, d, Q, c,
            list(range(len(nodes))),
            source_node,
            consumers
        )

        show(results, nodes)

        # Вывод результатов
        print("Статус решения:", results['status'])
        print("Общая прибыль:", results['total_profit'])

        print("\nПроизводство:")
        for k, amount in results['production'].items():
            print(f"Товар {k}: {amount:.2f} (цена: {p[k]})")

        print("\nИспользование сырья:")
        for l, amount in results['raw_material_used'].items():
            print(
                f"Сырье {l}: использовано {amount:.2f} из {b[l]} ({results['raw_material_utilization'][l] * 100:.1f}%)")

    except ValueError as e:
        print("Ошибка при решении задачи:", e)


def show(res, nodes):
    net = Network(directed=True, height="600px", width="100%")

    for i in range(len(nodes)):
        net.add_node(i, label=nodes[i])

    for (k, i, j), capacity in res['transport'].items():
        net.add_edge(i, j, label=f'т{k}: {capacity}')

    net.options.physics.springLength = 350

    net.show("transport_graph.html", notebook=False)


def generate():
    pass


# Пример использования
if __name__ == "__main__":

    # generate()

    main()
