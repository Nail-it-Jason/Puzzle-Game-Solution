# 日期拼图游戏的解
# 首先定义棋盘
#    0      1      2      3      4      5      6      7
# 0  🐶     Mon    Tue    Wed    JAN    FEB    MAR    APR
# 1  Thu    Fri    Sat    Sun    MAY    JUN    JUL    AUG
# 2  1      2      3      4      SEP    OCT    NOV    DEC
# 3  5      6      7      8      9      10     11     12
# 4  13     14     15     16     17     18     19     20
# 5  21     22     23     24     25     26     27     28
# 6  29     30     31
size1 = 7 # 行数
size2 = 8 # 列数
board = [
    [0, 0, 0, 0, 0, 0, 0, 0],  # 0
    [0, 0, 0, -1, 0, 0, -1, 0],  # 1
    [0, 0, 0, 0, 0, 0, 0, 0],  # 2
    [0, -1, 0, 0, 0, 0, 0, 0],  # 3
    [0, 0, 0, 0, 0, 0, 0, 0],  # 4
    [0, 0, 0, 0, 0, 0, 0, 0],  # 5
    [0, 0, 0, -1, -1, -1, -1, -1],  # 6
]


# 所有的积木块形状（11种），可90度旋转以及反转，则一个积木块有8个形态(虽然部分有对称性但可以忽略)
# 3格
L3 = [(0, 0), (0, 1), (1, 1)]
# 4格
L4 = [(0, 0), (0, 1), (0, 2), (1, 2)]
T4 = [(0, 0), (0, 1), (0, 2), (1, 1)]
# Square
Sq = [(0, 0), (0, 1), (1, 0), (1, 1)]
# Line
Ln = [(0, 0), (0, 1), (0, 2), (0, 3)]
# Z or S
ZS = [(0, 0), (0, 1), (1, 1), (1, 2)]
# 5格
L5 = [(0, 0), (0, 1), (0, 2), (0, 3), (1, 3)]
# 对称的L
LL = [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2)]
# "Bowl"
BL = [(0, 0), (0, 1), (1, 1), (2, 1), (2, 0)]
# "Asymmetric T"
AT = [(0, 0), (0, 1), (0, 2), (0, 3), (1, 1)]
# "Hammer"
Hm = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1)]

# blocks = [L3, L4, T4, Sq, Ln, ZS, L5, LL, BL, AT, Hm]
blocks = [L3, L4, T4, Sq, Ln, ZS, L5, LL, BL, AT]

# ------------------------------------------------------

def printshape(block, pattern='X', empty='0'):
    x_max = max(x for (x, y) in block)
    y_max = max(y for (x, y) in block)
    printlist = [[empty for _ in range(x_max + 1)] for _ in range(y_max + 1)]
    for x, y in block:
        printlist[y][x] = pattern
    for row in printlist:
        print(''.join(row))

def print_board(board):
    for row in board:
        line = ''
        for cell in row:
            if cell == -1:
                line += '■ '
            elif cell == 0:
                line += '· '
            else:
                line += f'{cell} '
        print(line)

class Transform: # 包括镜像、顺时针旋转90度以及归一化防止坐标超出棋盘
    def __init__(self, block):
        self.block = [tuple(p) for p in block]

    def copy(self):
        return Transform(self.block.copy())

    def normalize(self): # 旋转镜像以后得到的坐标可能是负的，需要把它平移到以(0, 0)起始
        x_min = min(x for (x, y) in self.block)
        y_min = min(y for (x, y) in self.block)
        self.block = [(x - x_min, y - y_min) for (x, y) in self.block]
        return self

    def mirror(self):
        self.block = [(-x, y) for (x, y) in self.block]
        return self.normalize().block

    def rotate90(self): # 顺时针，以(0, 0)为旋转中心
        self.block = [(y, -x) for (x, y) in self.block]
        return self.normalize().block

    def mirrored(self):
        new_block = [(-x, y) for(x, y) in self.block]
        return Transform(new_block).normalize().block

    def rotated90(self):
        new_block = [(y, -x) for (x, y) in self.block]
        return Transform(new_block).normalize().block


def test_blocks(blocks):
    for idx, block in enumerate(blocks):
        print(f"\n=== Block #{idx + 1} 原始形状: {block} ===")
        transforms = generate_all_transforms(block)

        for t_idx, trans in enumerate(transforms):
            print(f"\n变换 {t_idx + 1}:")
            print("坐标:", trans)
            printshape(trans)

def generate_all_transforms(block):  # 返回4个旋转90度，然后翻转后再旋转90度的4个，共8个
    block0 = block
    block1 = Transform(block0).rotated90()
    block2 = Transform(block1).rotated90()
    block3 = Transform(block2).rotated90()
    block4 = Transform(block3).mirrored()
    block5 = Transform(block4).rotated90()
    block6 = Transform(block5).rotated90()
    block7 = Transform(block6).rotated90()

    return [block0, block1, block2, block3,
            block4, block5, block6, block7]

def solve_puzzle(board, blocks):
    charset = ['a', 'b', 'c', 'd', 'e', 'f', 'g',
               'h', 'i', 'j', 'k']

    def backtrack(depth):
        def can_place(board, block, i, j):
            for (x, y) in block:
                row, col = i + y, j + x
                if row >= size1 or col >= size2 or row < 0 or col < 0:
                    return False
                if board[row][col] != 0:
                    return False
            return True

        def place(board, block, i, j, ch):
            for (x, y) in block:
                board[i + y][j + x] = ch

        def undo(board, block, i, j):
            for (x, y) in block:
                board[i + y][j + x] = 0


        if depth == len(blocks):
            print("********** Success! **********")
            print_board(board)
            return True  # 停止所有后续递归

        for transform in generate_all_transforms(blocks[depth]):
            max_x = max(x for x, y in transform)
            max_y = max(y for x, y in transform)
            for i in range(size1 - max_y):  # 行方向
                for j in range(size2 - max_x):  # 列方向
                    if can_place(board, transform, i, j):
                        place(board, transform, i, j, charset[depth])

                        if backtrack(depth + 1):
                            return True

                        undo(board, transform, i, j)

        return False  # 所有放置都失败

    backtrack(0)

if __name__ == '__main__':
    solve_puzzle(board, blocks)
