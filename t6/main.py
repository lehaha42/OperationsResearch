import json


def show(arr):
    for i in range(3):
        for j in range(3):
            for k in range(3):
                for l in range(3):
                    print(f'{arr[i*3+j][k*3+l]} ', end='')
                if k < 2:
                    print('  ', end='')
            print()
        print()


def can_put(arr, x, y, n):
    for i in range(9):
        if i != x and arr[i][y] == n or i != y and arr[x][i] == n:
            return False
    for i in range(3):
        for j in range(3):
            if not (i == x % 3 and j == y % 3) and arr[i + (x//3)*3][j + (y//3)*3] == n:
                return False
    return True


def solve(arr):
    print('quest:')
    show(arr)
    ans = [[arr[i][j] for j in range(9)] for i in range(9)]
    i = 0
    b = 0
    while i < 81:
        x, y = i//9, i % 9
        if arr[x][y] != 0:
            if b == 0:
                i += 1
            else:
                i -= 1
            continue
        if ans[x][y] < 9:
            if can_put(ans, x, y, ans[x][y]+1):
                i += 1
            b = 0
            ans[x][y] += 1
        else:
            ans[x][y] = 0
            b = 1
            i -= 1
    print('answer:')
    show(ans)


def main():
    with open("data.json", "r") as file:
        data = json.loads(file.read())
    for name, arr in data.items():
        print(f'\n\n{name}')
        solve(arr)


if __name__ == '__main__':
    main()
