from pulp import *


# отображение судоку
def show(arr, pos_arr):
    # общий размер
    size = [0, 0]
    for p in pos_arr:
        size = [max(size[0], p[0]+9), max(size[1], p[1]+9)]

    # какие клетки показывать
    s = [[-1 for _ in range(size[1])] for _ in range(size[0])]
    for n in range(len(arr)):
        for i in range(9):
            for j in range(9):
                s[i+pos_arr[n][0]][j+pos_arr[n][1]] = arr[n][i][j]

    # вывод
    for i in range(size[0]):
        if i % 3 == 0 and i != 0:
            print()
        for j in range(size[1]):
            if j % 3 == 0 and j != 0:
                print('   ', end='')
            if s[i][j] != -1:
                print(f'{s[i][j]}  ', end='')
            else:
                print('   ', end='')
        print()


# решение
def solve(data):
    # главная проблема
    prob = LpProblem("sudoku")

    # переменные
    pos_arr = []
    arr = []
    connections = []
    choices = [LpVariable.dicts(f"Choice_{i}", (range(9), range(9), range(1, 10)), cat=LpBinary) for i in range(len(data))]

    # для каждой сетки судоку
    for num in range(len(data)):

        # одна цифра на клетку
        for i in range(9):
            for j in range(9):
                prob += lpSum([choices[num][i][j][k] for k in range(1, 10)]) == 1

        # уникальные цифры в строке
        for i in range(9):
            for k in range(1, 10):
                prob += lpSum([choices[num][i][j][k] for j in range(9)]) == 1

        # уникальные цифры в столбце
        for j in range(9):
            for k in range(1, 10):
                prob += lpSum([choices[num][i][j][k] for i in range(9)]) == 1

        # уникальные цифры в квадрате 3х3
        for r in range(3):
            for c in range(3):
                for k in range(1, 10):
                    prob += lpSum([choices[num][i][j][k]
                                   for i in range(r*3, (r+1)*3)
                                   for j in range(c*3, (c+1)*3)]) == 1

        # ввод изначальных значений
        for i in range(9):
            for j in range(9):
                if data[num]['arr'][i][j] != 0:
                    k = data[num]['arr'][i][j]
                    prob += choices[num][i][j][k] == 1

        # оброаботка пересечений
        p = data[num]['pos']
        for n in range(len(pos_arr)):
            pos = pos_arr[n]
            for i in range(max(p[0], pos[0]), min(p[0]+9, pos[0]+9)):
                for j in range(max(p[1], pos[1]), min(p[1]+9, pos[1]+9)):
                    connections.append((n, i-pos[0], j-pos[1], num, i-p[0], j-p[1]))

        pos_arr.append(p)
        arr.append(data[num]['arr'])

    # условие равенства пересекающихся клеток
    for g1, i1, j1, g2, i2, j2 in connections:
        for k in range(1, 10):
            prob += choices[g1][i1][j1][k] == choices[g2][i2][j2][k]

    # решатель
    prob.solve()

    # проверка наличия решения
    if LpStatus[prob.status] != "Optimal":
        print("ERROR")
        return [arr, [], pos_arr]

    # преобразование решения для отображения
    solutions = [[[0 for _ in range(9)] for _ in range(9)] for _ in range(len(data))]
    for n in range(len(data)):
        for i in range(9):
            for j in range(9):
                for k in range(1, 10):
                    if choices[n][i][j][k].value() == 1:
                        solutions[n][i][j] = k
                        break

    return [arr, solutions, pos_arr]


# вывод исходного судоку и решения
def dispay(solution):
    print("\nquest:\n")
    show(solution[0], solution[2])
    print("\nanswer:\n")
    show(solution[1], solution[2])


# главная функция
def main():
    solutions = []
    with open("data.json", "r") as file:
        data = json.loads(file.read())
        for name, s_data in data.items():
            print(f'\n\n{name}')
            solutions.append(solve(s_data))
        for name, _ in data.items():
            print(f'\n\n{name}')
            dispay(solutions.pop(0))


if __name__ == '__main__':
    main()
