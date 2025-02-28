import numpy as np
import graphviz as gz
from scipy.optimize import linprog
from json import loads, dumps
from random import randint


def generator(N, M):
    with open('data.json', 'w') as file:
        data = {'inputs': [], 'outputs': [], 'matrix': []}
        for i in range(N):
            data['inputs'].append(randint(10, 99))
        for i in range(M):
            data['outputs'].append(randint(10, 99))
        for i in range(N):
            line = []
            for j in range(M):
                line.append(randint(10, 99))
            data['matrix'].append(line)
        delta = sum(data['inputs']) - sum(data['outputs'])
        if delta > 0:
            data['outputs'].append(delta)
            for i in range(N):
                data['matrix'][i].append(0)
        if delta < 0:
            data['inputs'].append(-delta)
            data['matrix'].append([0 for _ in range(M)])

        file.write(dumps(data))


def show_matrix(data, name):
    N, M = len(data['inputs']), len(data['outputs'])
    names = [f"prov№{i}\n{data['inputs'][i]}" for i in range(N)] + [f"cons№{i}\n{data['outputs'][i]}" for i in range(M)]

    graph = gz.Digraph(name)

    for name in names:
        graph.node(name)

    for i in range(N):
        for j in range(M):
            if data['matrix'][i][j] != 0:
                graph.edge(names[i], names[N+j], f"{data['matrix'][i][j]}")

    graph.render(directory='d_render', view=True)


def main():
    if input('new data?(y/n): ').lower() == 'y':
        generator(int(input('inputs: ')), int(input('outputs: ')))
    with open('data.json', 'r') as file:
        data = loads(file.read())
    show_matrix(data, 'data')

    m = len(data['inputs'])
    n = len(data['outputs'])

    p = np.array(data['inputs'])
    q = np.array(data['outputs'])

    C = np.array(data['matrix'])

    C_vec = C.reshape((m * n, 1), order='F')

    A1 = np.kron(np.ones((1, n)), np.identity(m))
    A2 = np.kron(np.identity(n), np.ones((1, m)))
    A = np.vstack([A1, A2])

    b = np.hstack([p, q])

    res = linprog(C_vec, A_eq=A, b_eq=b)
    if res['success']:
        arr = []
        for i in range(m):
            l = []
            for j in range(n):
                l.append(int(res.x[j*m+i]))
            arr.append(l)
        data['matrix'] = arr
        show_matrix(data, 'solution')
    else:
        print(res)


if __name__ == '__main__':
    main()
