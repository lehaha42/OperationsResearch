import networkx as nx
from pyvis.network import Network
import pulp
from itertools import combinations


def create_weighted_graph():
    # Задаем граф
    G = nx.Graph()
    edges = [
        ('A', 'B', 4), ('A', 'H', 8),
        ('B', 'C', 8), ('B', 'H', 11),
        ('C', 'D', 7), ('C', 'F', 4), ('C', 'I', 2),
        ('D', 'E', 9), ('D', 'F', 14),
        ('E', 'F', 10),
        ('F', 'G', 2),
        ('G', 'H', 1), ('G', 'I', 6),
        ('H', 'I', 7)
    ]
    G.add_weighted_edges_from(edges)
    return G


def find_mst_with_lp(graph):
    edges = list(graph.edges(data=True))
    nodes = list(graph.nodes())
    n = len(nodes)

    # Создаем задачу
    prob = pulp.LpProblem("Minimum_Spanning_Tree", pulp.LpMinimize)

    # Бинарные переменные для каждого ребра
    edge_vars = {
        (u, v): pulp.LpVariable(f"x_{u}_{v}", cat=pulp.LpBinary)
        for u, v, data in edges
    }

    # Целевая функция: минимизировать суммарный вес
    prob += pulp.lpSum(
        edge_vars[(u, v)] * data['weight']
        for u, v, data in edges
    )

    # Ограничение: ровно (n-1) ребро
    prob += pulp.lpSum(edge_vars.values()) == n - 1

    # Условия на разрезы для всех подмножеств (исключаем циклы)
    for size in range(2, n):
        for subset in combinations(nodes, size):
            # Сумма рёбер внутри подмножества <= |subset| - 1
            prob += pulp.lpSum(
                edge_vars[(u, v)] for u, v in edge_vars
                if u in subset and v in subset
            ) <= len(subset) - 1

    # Решаем задачу
    prob.solve(pulp.PULP_CBC_CMD(msg=False))

    # Собираем
    mst = nx.Graph()
    for u, v, data in edges:
        if pulp.value(edge_vars[(u, v)]) > 0.5:
            mst.add_edge(u, v, weight=data['weight'])

    return mst


def visualize_graphs(original_graph, mst_graph):
    # Исходный граф
    net_original = Network(height="900px", width="100%")
    for node in original_graph.nodes():
        net_original.add_node(node)
    for u, v, data in original_graph.edges(data=True):
        net_original.add_edge(u, v, label=f"{data['weight']}")

    # Минимальное остовное дерево
    net_mst = Network(height="900px", width="100%")
    for node in original_graph.nodes():
        net_mst.add_node(node)
    for u, v, data in original_graph.edges(data=True):
        net_mst.add_edge(u, v, label=f"{data['weight']}", color='red' if (u, v, data) in mst_graph.edges(data=True) else 'blue')

    net_original.show("original_graph.html", notebook=False)
    net_mst.show("mst_lp.html", notebook=False)


def main():
    # Создаем граф
    G = create_weighted_graph()

    # Находим дерево
    mst = find_mst_with_lp(G)

    # Выводим
    print("Суммарный вес:", sum(data['weight'] for _, _, data in mst.edges(data=True)))

    visualize_graphs(G, mst)


if __name__ == "__main__":
    main()