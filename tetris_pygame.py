#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Very simple tetris implementation
#
# Control keys:
#       Down - Drop stone faster
# Left/Right - Move stone
#         Up - Rotate Stone clockwise
#     Escape - Quit game
#          P - Pause game
#     Return - Instant drop
#
# Have fun!

import sys
import time
from random import randrange as rand

import pygame

# The configuration
cell_size = 18
cols = 10
rows = 22
maxfps = 30
cluster_thold = 3

colors = [
    "#B5B5B5",  # (0, 0, 0),  # black
    "#F7D04C",  # (255, 85, 85),  # red
    "#F69E53",  # (100, 200, 115),  # green
    "#FF747A",  # (120, 108, 245),  # blue
    "#4695D6",  # (255, 140, 50),  # orange
    "#46CFE4",  # (50, 120, 52),  # green(dark)
    "#8ADAC0",  # (146, 202, 73),  # green
    "#F0B4DC",  # (150, 161, 218),  # blue(light)
    "#DEDEDE",  # (35, 35, 35),  # Helper color for background grid # gray
]

# Define the shapes of the single parts
tetris_shapes = [
    [[1, 1, 1], [0, 1, 0]],
    [[0, 1, 1], [1, 1, 0]],
    [[1, 1, 0], [0, 1, 1]],
    [[1, 0, 0], [1, 1, 1]],
    [[0, 0, 1], [1, 1, 1]],
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
]
# tetris_shapes = [
#     [[1, 1, 1], [0, 1, 0]],
#     [[0, 2, 2], [2, 2, 0]],
#     [[3, 3, 0], [0, 3, 3]],
#     [[4, 0, 0], [4, 4, 4]],
#     [[0, 0, 5], [5, 5, 5]],
#     [[6, 6, 6, 6]],
#     [[7, 7], [7, 7]],
# ]

labels_dict = {
    1: "0",
    2: "1",
    3: "+",
    4: "-",
    5: "H",
    6: "Z",
    7: "X",
}

opperator_labels = ["H", "Z", "X"]

labels_dict_inv = {v: k for k, v in labels_dict.items()}


def rotate_clockwise(shape):
    return [
        [shape[y][x] for y in range(len(shape))]
        for x in range(len(shape[0]) - 1, -1, -1)
    ]


def check_collision(board, shape, offset):
    off_x, off_y = offset
    for cy, row in enumerate(shape):
        for cx, cell in enumerate(row):
            try:
                if cell and board[cy + off_y][cx + off_x]:
                    return True
            except IndexError:
                return True
    return False


def remove_row(board, row):
    del board[row]
    return [[0 for i in range(cols)]] + board


def find_idential_adjacent(board, x, y):
    """対象の座標(x,y)の隣接に同一ブロックがないかをチェック
    クラスター候補となる座標のsetを出力"""
    set_cluster_xy = {(x, y)}
    while True:
        pre_set_cluster_xy = set_cluster_xy.copy()
        for xx, yy in pre_set_cluster_xy:
            # 左端の場合以外で左側のブロック比較
            if (xx != 0) and (board[yy][xx] == board[yy][xx - 1]):
                set_cluster_xy.add((xx - 1, yy))
            # 右端の場合以外で右側のブロック比較
            if (xx != cols - 1) and (board[yy][xx] == board[yy][xx + 1]):
                set_cluster_xy.add((xx + 1, yy))
            # 上端の場合以外で上側のブロック比較
            if (yy != 0) and (board[yy][xx] == board[yy - 1][xx]):
                set_cluster_xy.add((xx, yy - 1))
            # 下端の場合以外で下側のブロック比較
            if (yy != rows - 1) and (board[yy][xx] == board[yy + 1][xx]):
                set_cluster_xy.add((xx, yy + 1))
        if len(pre_set_cluster_xy) == len(set_cluster_xy):
            break

    return set_cluster_xy


def find_cluster(board, threthold=cluster_thold):
    """cluster_tholdをクラスター判定の基準とし、同一ブロックが隣接した全座標setを出力"""
    clusters_cordinates = set()
    for x in range(cols):
        for y in range(rows):
            if (board[y][x] == 0) or ((x, y) in clusters_cordinates):
                continue
            else:
                cluster_candidate = find_idential_adjacent(board, x, y)
                if len(cluster_candidate) >= threthold:
                    clusters_cordinates.update(cluster_candidate)
    return clusters_cordinates


def delete_clusters(board, clusters):
    """クラスターを削除"""
    for x, y in clusters:
        board[y][x] = 0
    return board


def operate_gate(board, operator, target):
    "targetブロックにoperatorを作用"
    # operator: ()
    operator_x, operator_y, gate_type = operator
    target_x, target_y, qstate_pre = target

    if labels_dict[gate_type] == "H":
        qstate_transition_dict = {"0": "+", "1": "-", "+": "0", "-": "1"}
    elif labels_dict[gate_type] == "X":
        # 0 <-> 1
        qstate_transition_dict = {"0": "1", "1": "0", "+": "+", "-": "-"}
    elif labels_dict[gate_type] == "Z":
        qstate_transition_dict = {"0": "0", "1": "1", "+": "-", "-": "+"}

    # targetの量子状態を更新
    q_state_post = qstate_transition_dict[labels_dict[qstate_pre]]
    board[target_y][target_x] = labels_dict_inv[q_state_post]
    # ゲートブロックの削除
    board[operator_y][operator_x] = 0

    return board


def get_operator_target(board):
    "ゲートの(位置,種類)とターゲットの(位置,種類)ペアを取得"
    # ゲートの真下のみ作用する仕様へ変更
    operator_target_dict = {}
    for y in range(rows):
        for x in range(cols):
            if labels_dict[board[y][x]] not in opperator_labels:
                continue
            # if


def settle_board(board):
    """クラスター削除後に浮いたブロックを落下"""
    for x in range(cols):
        for y in range(rows - 2, 0, -1):
            if board[y][x] == 0:
                continue
            # ブロックの下にスペースがあれば落としていく
            for down_y in range(y + 1, rows):
                if board[down_y][x] == 0:
                    board[down_y][x] = board[down_y - 1][x]
                    board[down_y - 1][x] = 0
                else:
                    break
    return board


def join_matrixes(mat1, mat2, mat2_off):
    off_x, off_y = mat2_off
    for cy, row in enumerate(mat2):
        for cx, val in enumerate(row):
            mat1[cy + off_y - 1][cx + off_x] += val
    return mat1


def new_board():
    board = [[0 for x in range(cols)] for y in range(rows)]
    board += [[1 for x in range(cols)]]
    return board


class TetrisApp(object):
    def __init__(self):
        pygame.init()
        pygame.key.set_repeat(250, 25)
        self.width = cell_size * (cols + 6)
        self.height = cell_size * rows
        self.rlim = cell_size * cols
        self.bground_grid = [
            [8 if x % 2 == y % 2 else 0 for x in range(cols)] for y in range(rows)
        ]

        self.default_font = pygame.font.Font(pygame.font.get_default_font(), 12)
        self.screen = pygame.display.set_mode((self.width, self.height))

        pygame.event.set_blocked(pygame.MOUSEMOTION)  # We do not need
        # mouse movement
        # events, so we
        # block them.
        self.next_stone = tetris_shapes[rand(len(tetris_shapes))]
        self.next_stone = [
            [rand(1, +len(tetris_shapes) + 1) if i != 0 else 0 for i in col]
            for col in self.next_stone
        ]
        self.init_game()

    def new_stone(self):
        self.stone = self.next_stone[:]

        self.next_stone = tetris_shapes[rand(len(tetris_shapes))]
        self.next_stone = [
            [rand(1, len(tetris_shapes) + 1) if i != 0 else 0 for i in col]
            for col in self.next_stone
        ]
        self.stone_x = int(cols / 2 - len(self.stone[0]) / 2)
        self.stone_y = 0

        if check_collision(self.board, self.stone, (self.stone_x, self.stone_y)):
            self.gameover = True
        print(self.stone)
        print(self.board)

    def init_game(self):
        self.board = new_board()
        self.new_stone()
        self.level = 1
        self.score = 0
        self.lines = 0
        pygame.time.set_timer(pygame.USEREVENT + 1, 1000)

    def disp_msg(self, msg, topleft):
        x, y = topleft
        for line in msg.splitlines():
            self.screen.blit(
                self.default_font.render(line, False, (255, 255, 255), (0, 0, 0)),
                (x, y),
            )
            y += 14

    def center_msg(self, msg):
        for i, line in enumerate(msg.splitlines()):
            msg_image = self.default_font.render(
                line, False, (255, 255, 255), (0, 0, 0)
            )

            msgim_center_x, msgim_center_y = msg_image.get_size()
            msgim_center_x //= 2
            msgim_center_y //= 2

            self.screen.blit(
                msg_image,
                (
                    self.width // 2 - msgim_center_x,
                    self.height // 2 - msgim_center_y + i * 22,
                ),
            )

    def draw_matrix(self, matrix, offset):
        off_x, off_y = offset
        for y, row in enumerate(matrix):
            for x, val in enumerate(row):

                if val != 0:
                    val_rec = val
                elif (val == 0) and (off_x < cols):
                    # print(off_y, off_x)
                    # print([off_y + y], [off_x + x])
                    val_rec = self.bground_grid[off_y + y][off_x + x]
                else:
                    continue

                pygame.draw.rect(
                    self.screen,
                    colors[val_rec],
                    pygame.Rect(
                        (off_x + x) * cell_size,
                        (off_y + y) * cell_size,
                        cell_size,
                        cell_size,
                    ),
                    0,
                )

                if val in labels_dict:
                    text = self.default_font.render(labels_dict[val], True, "white")
                    text_rect = text.get_rect(
                        center=(
                            (off_x + x + 0.5) * cell_size,
                            (off_y + y + 0.5) * cell_size,
                        )
                    )
                    self.screen.blit(text, text_rect)
                    # self.screen.blit(
                    #     self.default_font.render(
                    #         labels_dict[val], True, "white"
                    #     ),
                    #     ((off_x + x) * cell_size, (off_y + y) * cell_size),
                    # )

    def update_matrix(self):
        self.draw_matrix(self.bground_grid, (0, 0))
        self.draw_matrix(self.board, (0, 0))
        self.draw_matrix(self.stone, (self.stone_x, self.stone_y))
        self.draw_matrix(self.next_stone, (cols + 1, 2))
        pygame.display.update()

    def add_cl_lines(self, n):
        linescores = [0, 40, 100, 300, 1200]
        self.lines += n
        self.score += linescores[n] * self.level
        if self.lines >= self.level * 6:
            self.level += 1
            newdelay = 1000 - 50 * (self.level - 1)
            newdelay = 100 if newdelay < 100 else newdelay
            pygame.time.set_timer(pygame.USEREVENT + 1, newdelay)

    def move(self, delta_x):
        if not self.gameover and not self.paused:
            new_x = self.stone_x + delta_x
            if new_x < 0:
                new_x = 0
            if new_x > cols - len(self.stone[0]):
                new_x = cols - len(self.stone[0])
            if not check_collision(self.board, self.stone, (new_x, self.stone_y)):
                self.stone_x = new_x

    def quit(self):
        self.center_msg("Exiting...")
        pygame.display.update()
        sys.exit()

    def drop(self, manual):
        if not self.gameover and not self.paused:
            self.score += 1 if manual else 0
            self.stone_y += 1
            if check_collision(self.board, self.stone, (self.stone_x, self.stone_y)):
                self.board = join_matrixes(
                    self.board, self.stone, (self.stone_x, self.stone_y)
                )
                self.new_stone()
                cleared_rows = 0
                # clusters = find_cluster(self.board)
                # while len(clusters) > 0:
                #     self.board = delete_clusters(self.board, clusters)
                #     self.board = settle_board(self.board)
                #     clusters = find_cluster(self.board)
                #     cleared_rows += 1

                # while True:
                #     for i, row in enumerate(self.board[:-1]):
                #         if 0 not in row:
                #             print(self.board)
                #             print(find_cluster(self.board))
                #             self.board = remove_row(self.board, i)
                #             print(self.board)
                #             cleared_rows += 1
                #             break
                #     else:
                #         break
                self.add_cl_lines(cleared_rows)
                return True
        return False

    def insta_drop(self):
        if not self.gameover and not self.paused:
            while not self.drop(True):
                pass

    def rotate_stone(self):
        if not self.gameover and not self.paused:
            new_stone = rotate_clockwise(self.stone)
            if not check_collision(self.board, new_stone, (self.stone_x, self.stone_y)):
                self.stone = new_stone

    def toggle_pause(self):
        self.paused = not self.paused

    def toggle_pause_display(self):
        self.paused_display = not self.paused_display

    def start_game(self):
        if self.gameover:
            self.init_game()
            self.gameover = False

    def run(self):
        key_actions = {
            "ESCAPE": self.quit,
            "LEFT": lambda: self.move(-1),
            "RIGHT": lambda: self.move(+1),
            "DOWN": lambda: self.drop(True),
            "UP": self.rotate_stone,
            "p": self.toggle_pause,
            "o": self.toggle_pause_display,
            "SPACE": self.start_game,
            "RETURN": self.insta_drop,
        }

        self.gameover = False
        self.paused = False
        self.paused_display = False

        dont_burn_my_cpu = pygame.time.Clock()
        while 1:
            self.screen.fill((0, 0, 0))
            if self.gameover:
                self.center_msg(
                    """Game Over!\nYour score: %d\nPress space to continue"""
                    % self.score
                )
            else:
                if self.paused:
                    if not self.paused_display:
                        self.center_msg("Paused")
                else:
                    pygame.draw.line(
                        self.screen,
                        (255, 255, 255),
                        (self.rlim + 1, 0),
                        (self.rlim + 1, self.height - 1),
                    )
                    self.disp_msg("Next:", (self.rlim + cell_size, 2))
                    self.disp_msg(
                        "Score: %d\n\nLevel: %d\nDeleted: %d"
                        % (self.score, self.level, self.lines),
                        (self.rlim + cell_size, cell_size * 5),
                    )
                if self.paused_display or not self.paused:

                    # self.draw_matrix(self.bground_grid, (0, 0))
                    # self.draw_matrix(self.board, (0, 0))
                    # self.draw_matrix(self.stone, (self.stone_x, self.stone_y))
                    # self.draw_matrix(self.next_stone, (cols + 1, 2))

                    clusters = find_cluster(self.board)
                    while len(clusters) > 0:
                        self.draw_matrix(self.bground_grid, (0, 0))
                        self.draw_matrix(self.board, (0, 0))
                        self.draw_matrix(self.next_stone, (cols + 1, 2))
                        pygame.display.update()
                        pygame.time.delay(1)

                        time.sleep(1)

                        self.board = delete_clusters(self.board, clusters)
                        # self.update_matrix()

                        self.screen.fill((0, 0, 0))
                        self.draw_matrix(self.bground_grid, (0, 0))
                        pygame.display.update()

                        self.draw_matrix(self.bground_grid, (0, 0))
                        self.draw_matrix(self.board, (0, 0))
                        self.draw_matrix(self.next_stone, (cols + 1, 2))
                        pygame.display.update()
                        pygame.time.delay(1)
                        time.sleep(1)

                        self.board = settle_board(self.board)
                        clusters = find_cluster(self.board)

                        # self.update_matrix()

                        self.draw_matrix(self.bground_grid, (0, 0))
                        self.draw_matrix(self.board, (0, 0))
                        self.draw_matrix(self.next_stone, (cols + 1, 2))
                        pygame.display.update()
                        pygame.time.delay(1)
                        # time.sleep(1)

                        pygame.event.clear()
                    else:
                        self.update_matrix()

            pygame.display.update()
            # print(len(pygame.event.get()))
            for event in pygame.event.get():
                if event.type == pygame.USEREVENT + 1:
                    self.drop(False)
                elif event.type == pygame.QUIT:
                    self.quit()
                elif event.type == pygame.KEYDOWN:
                    for key in key_actions:
                        if event.key == eval("pygame.K_" + key):
                            key_actions[key]()
                    else:
                        break

            dont_burn_my_cpu.tick(maxfps)


if __name__ == "__main__":
    App = TetrisApp()
    App.run()