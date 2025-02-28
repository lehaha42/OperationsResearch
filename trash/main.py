import json
import random


def generate_data(I, J):
    data = {'a': [], 'b': [], 'c': []}
    for i in range(I):
        data['a'].append(random.randint(10, 99))
    for i in range(J):
        data['b'].append(random.randint(10, 99))
    for i in range(I):
        arr = []
        for j in range(J):
            arr.append(random.randint(10, 99))
        data['c'].append(arr)
    with open('../t1/data.json', 'w') as file:
        file.write(json.dumps(data))


def get_max(arr):
    if not arr:
        return 0, 0
    if len(arr) == 1:
        return arr[0], 0
    m, n = arr[0], 0
    for i in range(1, len(arr)):
        if arr[i] > m:
            m = arr[i]
            n = i
    return m, n


def get_min(arr):
    if not arr:
        return 0, 0
    m, n = arr[0], 0
    for i in range(1, len(arr)):
        if arr[i] < m:
            m = arr[i]
            n = i
    return m, n


def get_dif(arr_):
    arr = arr_.copy()
    m1, n = get_min(arr)
    del arr[n]
    m2, _ = get_min(arr)
    return m2 - m1


def solve(data):
    a, b, c = data['a'].copy(), data['b'].copy(), data['c'].copy()
    I, J = len(a), len(b)
    delta = sum(a) - sum(b)
    if delta > 0:
        for i in range(I):
            c[i].append(0)
        b.append(delta)
        J += 1
    if delta < 0:
        c.append([0 for _ in range(J)])
        a.append(-delta)
    flag = True
    while flag:
        m1, n1 = get_max(list(map(get_dif, a)))
        m2, n2 = get_max(list(map(get_dif, b)))
        flag = False
    solution = data.copy()
    solution['s'] = f"0"
    solution['u'] = f"0"
    solution['t'] = f"0"
    return solution


def display(data, solution):
    """
    print('## | ', end='')
    for i in data['a']:
        print(f'{i}{" " * (2 - len(str(i)))} ', end='')
    print('\n---+' + '-' * (len(data['a']) * 3))
    for i in range(len(data['b'])):
        print(f'{data["b"][i]} | ', end='')
        for j in data['c'][i]:
            print(f'{j}{" " * (2 - len(str(j)))} ', end='')
        print()
    print()
    print('## | ', end='')
    for i in solution['a']:
        print(f'{i}{" " * (2 - len(str(i)))} ', end='')
    print('\n---+' + '-' * (len(solution['a']) * 3))
    for i in range(len(solution['b'])):
        print(f'{solution["b"][i]} | ', end='')
        for j in solution['c'][i]:
            print(f'{j}{" " * (2 - len(str(j)))} ', end='')
        print()
    print(f"\nsatisfied: {solution['s']}\nunsatisfied: {solution['u']}\ntotal cost: {solution['t']}")"""
    print(data)
    print(solution)


def main():
    """if input('new data?(y/n): ') == 'y':
        generate_data(
            int(input('I: ')),
            int(input('J: '))
        )"""
    with open('../t1/data.json') as file:
        data = json.loads(file.read())
    solution = solve(data)
    display(data, solution)


if __name__ == '__main__':
    main()
