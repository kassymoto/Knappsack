from pulp import *
from PIL import Image, ImageDraw, ImageFont
import copy

count = 0  # 調査したノードの数をカウントしておく。
ans = {}  # 解を格納する。Keyが暫定値、Valueがその時の暫定解

# 緩和して、上界を求める。
def knapsack(ini, goods_num, capacity, values, weight):
    m = LpProblem(sense=LpMaximize)  # 数理モデルを最大化問題として生成
    x = [LpVariable(f'x{i}', lowBound=0, upBound=1) for i in range(goods_num)]  # 変数 要するに品物
    m += lpDot(values, x) # 目的関数 要するに品物の価値
    m += lpDot(weight, x) <= capacity # 制約条件 要するに品物の重さ

    for i, xi in zip(ini, x):
        if i >= 0:  # 固定なら
            m += xi == i  # xiの値を固定された値にする。
    m.solve()  # 解を求める。
    # m.statusが1なら実行可能解があった。なければ0を返す。
    return value(m.objective) if m.status==1 else 0

'''
分枝限定法を行う
iniは固定状態を表す。負なら非固定。最初は全て-1
posは深さ
zanteiは暫定値
goods_numは品物の数
capacityはナップサックの容量
valuesは品物の価値
weightは品物の重さ
'''
def BB(ini, pos, zantei, goods_num, capacity, values, weight):
    global count
    global ans
    r = knapsack(ini, goods_num, capacity, values, weight)  # 上界（目的関数値）を求める
    if r < zantei[0]:  # 求めた上界が暫定解より小さいなら探索を終了する。
        return

    # 葉ノードでないとき
    if pos < len(ini):
        count += 1
        ini[pos] = 1  # xi(i=pos)を1に固定して探索する。
        BB(ini, pos+1, zantei, goods_num, capacity, values, weight)
        ini[pos] = 0  # xi(i=pos)を0に固定して探索する。
        BB(ini, pos+1, zantei, goods_num, capacity, values, weight)
        ini[pos] = -1

    # 葉ノードの時
    else:
        count += 1
        # 葉ノードかつ、暫定値より高い目的関数値のとき
        if zantei[0] < r:
            zantei[0] = r  # 暫定値を更新する。
            ans = {}
            ans[r] = copy.copy(ini)  # 暫定解を記録する。

# 入力から値を得る
def value_input(s):
    print(s,end="")
    try:
        num = int(input())
    except ValueError:
        print('有効な数字を入力してください')
        value_input(s)
    else:
        if num <= 0:
            print('有効な数字を入力してください')
            value_input(s)
        return num

# 各品物の価値と重さを入力から設定する。
def goods_input(goods_num):
    values = []
    weights = []

    print('各品物の価値を入力して下さい')
    for i in range(goods_num):
        value = value_input(f'x{i+1}:')
        values.append(value)

    print('各品物の重さを入力して下さい')
    for i in range(goods_num):
        weight = value_input(f'x{i+1}:')
        weights.append(weight)

    return values, weights

# 結果を印字する
def print_ans(goods_num):
    global ans
    global count
    s = '最適解：('
    v = '('
    print('このナップサックの問題の解は次のようになります。')
    for sol, val in ans.items():
        for i in range(len(val)):
            s += f'x{i+1}, ' if i<len(val)-1 else f'x{i+1}) = '
            v += f'{val[i]}, ' if i<len(val)-1 else f'{val[i]})'
        print(f'目標関数値：{sol}')

    print(s + v)
    print(f'全探索した場合のノード数(root除く)は{2**(goods_num+1)-2}個。')
    print(f'実際に探索したノードの数(root除く)は{count-1}個でした。')


goods_num = value_input('品物の数：')
capacity = value_input('ナップサックの容量：')
values, weight = goods_input(goods_num)

# 分枝限定法を実行する。
BB([-1]*goods_num, 0, [-999], goods_num, capacity, values, weight)

print_ans(goods_num)
