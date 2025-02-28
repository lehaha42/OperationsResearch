import graphviz as gz
from random import random, randint
from json import dumps, loads


class Graph:
    def __init__(self, graph):
        self.graph = [[i for i in j] for j in graph]
        self.ROW = len(graph)

    def BFS(self, s, t, parent):
        """
        Performs Breadth-First Search to find an augmenting path.

        Args:
            s: Source node.
            t: Sink node.
            parent: Array to store the parent node for each node in the path.

        Returns:
            True if an augmenting path is found, False otherwise.
        """
        visited = [False] * self.ROW
        queue = [s]
        visited[s] = True

        while queue:
            u = queue.pop(0)
            for ind, val in enumerate(self.graph[u]):
                if not visited[ind] and val > 0:
                    queue.append(ind)
                    visited[ind] = True
                    parent[ind] = u

        return True if visited[t] else False

    def FordFulkerson(self):
        source = 0
        sink = self.ROW-1
        parent = [-1] * self.ROW
        max_flow = 0

        while self.BFS(source, sink, parent):
            path_flow = float("Inf")
            s = sink
            while s != source:
                path_flow = min(path_flow, self.graph[parent[s]][s])
                s = parent[s]

            max_flow += path_flow

            v = sink
            while v != source:
                u = parent[v]
                self.graph[u][v] -= path_flow
                self.graph[v][u] += path_flow
                v = parent[v]

        return max_flow, self.graph


def gen_data(N, chance, inputs, outputs):
    assert inputs + outputs <= N
    chance = min(max(chance, 0.0), 1.0)
    arr = [[0 for _ in range(N + 2)]]
    n = 0
    for i in range(N):
        a = [0]
        for j in range(N):
            if (i != j) and (j >= inputs) and (i < N - outputs) and (random() < chance):
                a.append(randint(1, 20))
                n += 1
            else:
                a.append(0)
        a.append(0)
        arr.append(a)
    arr.append([0 for _ in range(N + 2)])
    for i in range(inputs):
        arr[0][i + 1] = 9999
    for i in range(outputs):
        arr[N - i][N + 1] = 9999
    print(f'edges: {n}')
    names = ["INPUTS"] + [f"{i + 1}" for i in range(N)] + ["OUTPUTS"]
    with open('data.json', 'w') as file:
        file.write(dumps({
            'arr': arr,
            'names': names,
            'inputs': inputs,
            'outputs': outputs
        }))


def load_data():
    with open('data.json') as file:
        return loads(file.read())


def show_graph(data, name):
    N = len(data['arr'])

    graph = gz.Digraph(name)

    for name in data['names']:
        graph.node(name)

    for i in range(N):
        for j in range(N):
            if data['arr'][i][j]:
                graph.edge(data['names'][i], data['names'][j], f"{data['arr'][i][j]}")

    graph.render(directory='d_render', view=True)


def solve(data):
    N = len(data['arr'])
    solution = {
        'names': data['names'].copy(),
        'arr': [['' for _ in range(N)] for __ in range(N)]
    }

    clean = {
        'names': data['names'].copy(),
        'arr': [['' for _ in range(N)] for __ in range(N)]
    }

    g = Graph(data['arr'].copy())
    max_flow, graph = g.FordFulkerson()
    for i in range(N):
        for j in range(N):
            if data['arr'][i][j]:
                solution['arr'][i][j] = f"{data['arr'][i][j]-graph[i][j]}/{data['arr'][i][j]}"
                if graph[i][j] != data['arr'][i][j]:
                    clean['arr'][i][j] = f"{data['arr'][i][j]-graph[i][j]}/{data['arr'][i][j]}"

    return solution, clean, max_flow


def main():
    if input('new data?(y/n): ').lower() == 'y':
        gen_data(
            int(input('N: ')),
            float(input('chance: ')),
            int(input('inputs: ')),
            int(input('outputs: ')),
        )
    data = load_data()
    show_graph(data, 'data')

    solution, clean, flow = solve(data)
    show_graph(solution, 'solution')
    show_graph(clean, 'clean')

    print(f"max flow: {flow}")


if __name__ == '__main__':
    main()
