# -*- coding:utf-8 -*-
import tkinter as tk
import random
import time

# 定数
BLOCK_SIZE = 25  # ブロックの縦横サイズpx
FIELD_WIDTH = 10  # フィールドの幅
FIELD_HEIGHT = 20  # フィールドの高さ

MOVE_LEFT = 0  # 左にブロックを移動することを示す定数
MOVE_RIGHT = 1  # 右にブロックを移動することを示す定数
MOVE_DOWN = 2  # 下にブロックを移動することを示す定数
base_color = "gray"
base_label = "N"

opperand_labels = ["0", "1", "+", "-", "i", "-i"]
opperator_labels = ["H", "X", "Z"]
label_color_dict = {"0":"red", "1": "blue", "+": "green", "-": "orange", "i": "black", "-i": "pink"}

# ルール
# (1) 同じ状態が隣り合うと消える(ぷよぷよ形式)
# (2) ゲートは量子状態にぶつかると状態を変えて消える
# (3) ブロックは宙に浮かずに形状を変えて落ちる

# 暫定案
# |i>と|-i>はひとまず含めない
# ゲートはZ,X,Hを使用
# 検討中
# ・3個以上で消えるようにするべきか？
# ・同じ状態で符号が揃った時だけ消えるようにするか？(→実装の難易度が上がるからひとまずなし)
# ・4ブロック内で一致していたらどうするか？(1.一致させない 2.落ちたときに評価)
# ・4ブロック内でゲートと量子状態を混合させるか？(混合させない方が楽？)
# ・両側からゲートが作用したら右側が優先


# To Do
# 色が同じなら消すのではなく、ラベルが同じなら消すという書き方に(ラベルに色を追従させる)
# 連鎖の過程を表示できるように

# ブロックを構成する正方形のクラス
class TetrisSquare():
    def __init__(self, x=0, y=0, color=base_color, label=base_label):
        '１つの正方形を作成'
        self.x = x
        self.y = y
        self.color = color
        self.label = label

    def set_cord(self, x, y):
        '正方形の座標を設定'
        self.x = x
        self.y = y

    def get_cord(self):
        '正方形の座標を取得'
        return int(self.x), int(self.y)

    def set_color(self, color):
        '正方形の色を設定'
        self.color = color

    def get_color(self):
        '正方形の色を取得'
        return self.color
    
    def set_label(self, label):
        '正方形の量子状態を設定'
        self.label = label

    def get_label(self):
        '正方形の量子状態を取得'
        return self.label
    
    def get_moved_cord(self, direction):
        '移動後の正方形の座標を取得'

        # 移動前の正方形の座標を取得
        x, y = self.get_cord()

        # 移動方向を考慮して移動後の座標を計算
        if direction == MOVE_LEFT:
            return x - 1, y
        elif direction == MOVE_RIGHT:
            return x + 1, y
        elif direction == MOVE_DOWN:
            return x, y + 1
        else:
            return x, y
        

# テトリス画面を描画するキャンバスクラス
class TetrisCanvas(tk.Canvas):
    def __init__(self, master, field):
        'テトリスを描画するキャンバスを作成'

        canvas_width = field.get_width() * BLOCK_SIZE
        canvas_height = field.get_height() * BLOCK_SIZE

        # tk.Canvasクラスのinit
        super().__init__(master, width=canvas_width, height=canvas_height, bg="white")

        # キャンバスを画面上に設置
        self.place(x=25, y=25)

        # 10x20個の正方形を描画することでテトリス画面を作成
        for y in range(field.get_height()):
            for x in range(field.get_width()):
                square = field.get_square(x, y)
                x1 = x * BLOCK_SIZE
                x2 = (x + 1) * BLOCK_SIZE
                y1 = y * BLOCK_SIZE
                y2 = (y + 1) * BLOCK_SIZE
                self.create_rectangle(
                    x1, y1, x2, y2,
                    outline="white", width=1,
                    fill=square.get_color()
                )

        # 一つ前に描画したフィールドを設定
        self.before_field = field

    def update(self, field, block):
        'テトリス画面をアップデート'

        # 描画用のフィールド（フィールド＋ブロック）を作成
        new_field = TetrisField()
        for y in range(field.get_height()):
            for x in range(field.get_width()):
                square = field.get_square(x, y)
                color = square.get_color()
                label = square.get_label()

                new_square = new_field.get_square(x, y)
                new_square.set_color(color)
                new_square.set_label(label)

        # フィールドにブロックの正方形情報を合成
        if block is not None:
            block_squares = block.get_squares()
            for block_square in block_squares:
                # ブロックの正方形の座標と色を取得
                x, y = block_square.get_cord()
                color = block_square.get_color()
                label = block_square.get_label()

                # 取得した座標のフィールド上の正方形の色を更新
                new_field_square = new_field.get_square(x, y)
                new_field_square.set_color(color)
                new_field_square.set_label(label)

        # 描画用のフィールドを用いてキャンバスに描画
        for y in range(field.get_height()):
            for x in range(field.get_width()):

                # (x,y)座標のフィールドの色を取得
                new_square = new_field.get_square(x, y)
                new_color = new_square.get_color()
                new_label = new_square.get_label()
                # (x,y)座標が前回描画時から変化ない場合は描画しない
                before_square = self.before_field.get_square(x, y)
                before_color = before_square.get_color()
                if(new_color == before_color):
                    continue

                x1 = x * BLOCK_SIZE
                x2 = (x + 1) * BLOCK_SIZE
                y1 = y * BLOCK_SIZE
                y2 = (y + 1) * BLOCK_SIZE
                x_c = (x1+x2)/2
                y_c = (y1+y2)/2
                # フィールドの各位置の色で長方形描画
                self.create_rectangle(
                    x1, y1, x2, y2,
                    outline="white", width=1, fill=new_color
                )
                if new_color != base_color:
                    self.create_text((x_c,y_c), text=new_label, fill="white")

        # 前回描画したフィールドの情報を更新
        self.before_field = new_field

# 積まれたブロックの情報を管理するフィールドクラス
class TetrisField():
    def __init__(self):
        self.width = FIELD_WIDTH
        self.height = FIELD_HEIGHT

        # フィールドを初期化
        self.squares = []
        for y in range(self.height):
            for x in range(self.width):
                # フィールドを正方形インスタンスのリストとして管理
                self.squares.append(TetrisSquare(x, y, base_color, base_label))

    def get_width(self):
        'フィールドの正方形の数（横方向）を取得'

        return self.width

    def get_height(self):
        'フィールドの正方形の数（縦方向）を取得'

        return self.height

    def get_squares(self):
        'フィールドを構成する正方形のリストを取得'

        return self.squares

    def get_square(self, x, y):
        '指定した座標の正方形を取得'

        return self.squares[y * self.width + x]

    def judge_game_over(self, block):
        'ゲームオーバーかどうかを判断'

        # フィールド上で既に埋まっている座標の集合作成
        no_empty_cord = set(square.get_cord() for square
                            in self.get_squares() if square.get_color() != base_color)

        # ブロックがある座標の集合作成
        block_cord = set(square.get_cord() for square
                         in block.get_squares())

        # ブロックの座標の集合と
        # フィールドの既に埋まっている座標の集合の積集合を作成
        collision_set = no_empty_cord & block_cord

        # 積集合が空であればゲームオーバーではない
        if len(collision_set) == 0:
            ret = False
        else:
            ret = True

        return ret

    def judge_can_move(self, block, direction):
        '指定した方向にブロックを移動できるかを判断'

        # フィールド上で既に埋まっている座標の集合作成
        no_empty_cord = set(square.get_cord() for square
                            in self.get_squares() if square.get_color() != base_color)

        # 移動後のブロックがある座標の集合作成
        move_block_cord = set(square.get_moved_cord(direction) for square
                              in block.get_squares())

        # フィールドからはみ出すかどうかを判断
        for x, y in move_block_cord:

            # はみ出す場合は移動できない
            if x < 0 or x >= self.width or \
                    y < 0 or y >= self.height:
                return False

        # 移動後のブロックの座標の集合と
        # フィールドの既に埋まっている座標の集合の積集合を作成
        collision_set = no_empty_cord & move_block_cord

        # 積集合が空なら移動可能
        if len(collision_set) == 0:
            ret = True
        else:
            ret = False

        return ret

    def fix_block(self, block):
        'ブロックを固定してフィールドに追加'

        for square in block.get_squares():
            # ブロックに含まれる正方形の座標と色を取得
            x, y = square.get_cord()
            color = square.get_color()
            label = square.get_label()

            # その座標と色をフィールドに反映
            field_square = self.get_square(x, y)
            field_square.set_color(color)
            field_square.set_label(label)
            
            
    # def delete_line(self):
    #     '行の削除を行う'

    #     # 全行に対して削除可能かどうかを調べていく
    #     for y in range(self.height):
    #         for x in range(self.width):
    #             # 行内に１つでも空があると消せない
    #             square = self.get_square(x, y)
    #             if(square.get_color() == base_color):
    #                 # 次の行へ
    #                 break
    #         else:
    #             # break されなかった場合はその行は空きがない
    #             # この行を削除し、この行の上側にある行を１行下に移動
    #             for down_y in range(y, 0, -1):
    #                 for x in range(self.width):
    #                     src_square = self.get_square(x, down_y - 1)
    #                     dst_square = self.get_square(x, down_y)
    #                     dst_square.set_color(src_square.get_color())
    #                     dst_square.set_label(src_square.get_label())
    #             # 一番上の行は必ず全て空きになる
    #             for x in range(self.width):
    #                 square = self.get_square(x, 0)
    #                 square.set_color(base_color)
        

    def down_after_fix(self):
        for y in range(self.height-2, 0, -1):
            for x in range(self.width):
                square = self.get_square(x, y)
                if square.get_color() == base_color:
                    continue
                # ブロックの下にスペースがあれば落としていく
                for down_y in range(y+1, FIELD_HEIGHT):
                    square_below =  self.get_square(x, down_y)
                    if square_below.get_color() == base_color:
                        square_below.set_color(square.get_color())
                        square_below.set_label(square.get_label())
                        square.set_color(base_color)
                        square.set_label(base_label)
                        square = self.get_square(x, down_y)
                    else:
                        break

    def delete_same(self):
        # 隣り合った量子状態が同じ場合消す
        # 全ブロックに対してペアの隣接ブロックを調べていく
        
        # 消した後に落下、さらに消せるところがないかチェックを変化がなくなるまでチェック
        while True:
            # 消すべき場所を取得
            squares_to_delete = []
            for y in range(self.height):
                for x in range(self.width):
                    square = self.get_square(x, y)
                    if square.get_color() == base_color:
                        continue
                    elif square.get_label() not in opperand_labels:
                        continue
                    # 右端の場合以外
                    if x != FIELD_WIDTH -1:
                        square_r = self.get_square(x+1, y)
                        if square.get_label() == square_r.get_label(): 
                            squares_to_delete.extend([square, square_r])
                    # 下端の場合以外
                    if y!= FIELD_HEIGHT-1:
                        square_up = self.get_square(x, y+1)
                        if square.get_label() == square_up.get_label(): 
                            squares_to_delete.extend([square, square_up])

            if len(squares_to_delete) == 0:
                break
            else:
                # ブロックの消去
                for square in set(squares_to_delete):
                    square.set_color(base_color)    
                    square.set_label(base_label) 
                self.down_after_fix()

    def operate_gate(self, operator_square, target_squares):
        if operator_square.get_label() == "H":
            # 0 <-> +,  1 <-> - 
            qstate_transition_dict = {"0": "+", "1": "-", "+": "0", "-": "1"}
        elif operator_square.get_label() == "X":
            # 0 <-> 1
            qstate_transition_dict = {"0": "1", "1": "0", "+": "+", "-": "-"}
        elif operator_square.get_label() == "Z":
            qstate_transition_dict = {"0": "0", "1": "1", "+": "-", "-": "+"}
            
        for square in target_squares:             
            new_qstate = qstate_transition_dict[square.get_label()]
            new_color = label_color_dict[new_qstate]
            square.set_label(new_qstate)
            square.set_color(new_color)        

        operator_square.set_color(base_color)
        operator_square.set_label(base_label)     

    def get_operator_target(self):
        operator_target_dict = {}
        for y in range(self.height):
            for x in range(self.width):
                opperands = []
                square = self.get_square(x, y)                
                if square.get_label() not in opperator_labels:
                    continue
                # 行列演算は順序があるため左右上下を確認する必要あり
                # 左端の場合以外、左側に量子状態ブロックがあるかチェック
                if x != 0:
                    square_l = self.get_square(x-1, y)
                    if square_l.get_label() in opperand_labels:
                        opperands.append(square_l)
                # 右端の場合以外、右側に量子状態ブロックがあるかチェック
                if x != FIELD_WIDTH -1:
                    square_r = self.get_square(x+1, y)
                    if square_r.get_label() in opperand_labels:
                        opperands.append(square_r)
                 # 上端の場合以外、上側に量子状態ブロックがあるかチェック
                if y!= 0:
                    square_down = self.get_square(x, y-1)
                    if square_down.get_label() in opperand_labels:
                        opperands.append(square_down)
                # 下端の場合以外、下側に量子状態ブロックがあるかチェック
                if y!= FIELD_HEIGHT-1:
                    square_up = self.get_square(x, y+1)
                    if square_up.get_label() in opperand_labels:
                        opperands.append(square_up)
                operator_target_dict[square] = opperands

        return operator_target_dict


    def operate_all_gates(self):
        for operator, opperands in self.get_operator_target().items():
            self.operate_gate(operator, opperands)

    def print_bottom_two_line(self):
        for y in range(self.height)[-2:]:
            for x in range(self.width):
                print(x,y, self.get_square(x, y).get_color(), self.get_square(x, y).get_label())
        print()

                
# テトリスのブロックのクラス
class TetrisBlock():
    def __init__(self):
        'テトリスのブロックを作成'

        # ブロックを構成する正方形のリスト
        self.squares = []

        # ブロックの形をランダムに決定
        block_type = random.randint(1, 8)
        
        # 乱数に応じた量子状態の色の設定
        # color_dict = {1:"red", 2:"blue", 3: "green", 4:"orange", 5:"black", 6:"pink"}
        label_dict = {1:"0", 2:"1", 3: "+", 4:"-", 5:"i", 6:"-i"}

        # 乱数に応じたゲート色の設定
        gate_label_dict = {1:"H", 2:"X", 3:"Z"}   
        gate_color_dict = {"H": "#70B7EB", "X": "#58C698", "Z": "#58C698"}


        # ブロックの中身を決定
        
        if block_type <=4: # 量子状態を生成
            # block_info = random.choices(range(1,5),k=4) # 重複あり
            block_info = random.sample(range(1,5),4) # 重複なし
            block_labels =  [label_dict[i] for i in block_info]     
            colors = [label_color_dict[label] for label in block_labels]

        elif block_type > 4: #量子ゲートを生成
            block_info = random.choices(range(1,4), k=4)
            block_labels =  [gate_label_dict[i] for i in block_info] 
            colors = [gate_color_dict[label] for label in block_labels]

        
        # ブロックの形に応じて４つの正方形の座標と色を決定
        if block_type == 1:
            # 縦棒を生成
            cords = [
                [FIELD_WIDTH / 2, 0],
                [FIELD_WIDTH / 2, 1],
                [FIELD_WIDTH / 2, 2],
                [FIELD_WIDTH / 2, 3],
            ]
        elif block_type == 2:
            # 正方形を生成
            cords = [
                [FIELD_WIDTH / 2, 0],
                [FIELD_WIDTH / 2, 1],
                [FIELD_WIDTH / 2 - 1, 0],
                [FIELD_WIDTH / 2 - 1, 1],
            ]
        elif block_type == 3:
            #  縦棒+右 を生成
            cords = [
                [FIELD_WIDTH / 2 - 1, 0],
                [FIELD_WIDTH / 2, 0],
                [FIELD_WIDTH / 2, 1],
                [FIELD_WIDTH / 2, 2],
            ]
        elif block_type == 4:
            # 縦棒+左を生成
            cords = [
                [FIELD_WIDTH / 2, 0],
                [FIELD_WIDTH / 2 - 1, 0],
                [FIELD_WIDTH / 2 - 1, 1],
                [FIELD_WIDTH / 2 - 1, 2],
            ]
        elif block_type == 5:
            # 横棒を生成
            cords = [
                [FIELD_WIDTH / 2 - 1, 0],
                [FIELD_WIDTH / 2, 0],
                [FIELD_WIDTH / 2 + 1, 0],
                [FIELD_WIDTH / 2 +2, 0],
            ]
        elif block_type == 6:
            # 正方形を生成
            cords = [
                [FIELD_WIDTH / 2, 0],
                [FIELD_WIDTH / 2, 1],
                [FIELD_WIDTH / 2 - 1, 0],
                [FIELD_WIDTH / 2 - 1, 1],
            ]
        elif block_type == 7:
            #  横棒+右 を生成
            cords = [
                [FIELD_WIDTH / 2 -1, 0],
                [FIELD_WIDTH / 2, 0],
                [FIELD_WIDTH / 2 +1, 0],
                [FIELD_WIDTH / 2 +1, 1],
            ]
        elif block_type == 8:
            # 縦棒+左を生成
            cords = [
                [FIELD_WIDTH / 2 -1, 0],
                [FIELD_WIDTH / 2, 0],
                [FIELD_WIDTH / 2 +1, 0],
                [FIELD_WIDTH / 2 -1, 1],
            ]

        # 決定した色と座標の正方形を作成してリストに追加
        for i, cord in enumerate(cords):
            self.squares.append(TetrisSquare(cord[0], cord[1], colors[i], block_labels[i]))

    def get_squares(self):
        'ブロックを構成する正方形を取得'

        # return [square for square in self.squares]
        return self.squares

    def move(self, direction):
        'ブロックを移動'

        # ブロックを構成する正方形を移動
        for square in self.squares:
            x, y = square.get_moved_cord(direction)
            square.set_cord(x, y)

# テトリスゲームを制御するクラス
class TetrisGame():

    def __init__(self, master):
        'テトリスのインスタンス作成'

        # ブロック管理リストを初期化
        self.field = TetrisField()

        # 落下ブロックをセット
        self.block = None

        # テトリス画面をセット
        self.canvas = TetrisCanvas(master, self.field)

        # テトリス画面アップデート
        self.canvas.update(self.field, self.block)

    def start(self, func):
        'テトリスを開始'

        # 終了時に呼び出す関数をセット
        self.end_func = func

        # ブロック管理リストを初期化
        self.field = TetrisField()

        # 落下ブロックを新規追加
        self.new_block()

    def new_block(self):
        'ブロックを新規追加'

        # 落下中のブロックインスタンスを作成
        self.block = TetrisBlock()

        if self.field.judge_game_over(self.block):
            self.end_func()
            print("GAMEOVER")

        # テトリス画面をアップデート
        self.canvas.update(self.field, self.block)

    def move_block(self, direction):
        'ブロックを移動'

        # 移動できる場合だけ移動する
        if self.field.judge_can_move(self.block, direction):

            # ブロックを移動
            self.block.move(direction)

            # 画面をアップデート
            self.canvas.update(self.field, self.block)

        else:
            # ブロックが下方向に移動できなかった場合
            if direction == MOVE_DOWN:
                # ブロックを固定する
                self.field.fix_block(self.block)
                # self.field.delete_line()
                self.field.down_after_fix()
                # self.canvas.update(self.field, self.block)
                # time.sleep(0.5)
                # self.field.fix_block(self.block)
                # self.canvas.update(self.field, self.block)
                # time.sleep(0.5)
                self.field.operate_all_gates()
                self.field.delete_same()
                # self.field.print_bottom_two_line()
                self.new_block()

# イベントを受け付けてそのイベントに応じてテトリスを制御するクラス
class EventHandller():
    def __init__(self, master, game):
        self.master = master

        # 制御するゲーム
        self.game = game

        # イベントを定期的に発行するタイマー
        self.timer = None

        # ゲームスタートボタンを設置
        button = tk.Button(master, text='START', command=self.start_event)
        button.place(x=25 + BLOCK_SIZE * FIELD_WIDTH + 25, y=30)

    def start_event(self):
        'ゲームスタートボタンを押された時の処理'

        # テトリス開始
        self.game.start(self.end_event)
        self.running = True

        # タイマーセット
        self.timer_start()

        # キー操作入力受付開始
        self.master.bind("<Left>", self.left_key_event)
        self.master.bind("<Right>", self.right_key_event)
        self.master.bind("<Down>", self.down_key_event)

    def end_event(self):
        'ゲーム終了時の処理'
        self.running = False

        # イベント受付を停止
        self.timer_end()
        self.master.unbind("<Left>")
        self.master.unbind("<Right>")
        self.master.unbind("<Down>")

    def timer_end(self):
        'タイマーを終了'

        if self.timer is not None:
            self.master.after_cancel(self.timer)
            self.timer = None

    def timer_start(self):
        'タイマーを開始'

        if self.timer is not None:
            # タイマーを一旦キャンセル
            self.master.after_cancel(self.timer)

        # テトリス実行中の場合のみタイマー開始
        if self.running:
            # タイマーを開始
            self.timer = self.master.after(1000, self.timer_event)

    def left_key_event(self, event):
        '左キー入力受付時の処理'

        # ブロックを左に動かす
        self.game.move_block(MOVE_LEFT)

    def right_key_event(self, event):
        '右キー入力受付時の処理'

        # ブロックを右に動かす
        self.game.move_block(MOVE_RIGHT)

    def down_key_event(self, event):
        '下キー入力受付時の処理'

        # ブロックを下に動かす
        self.game.move_block(MOVE_DOWN)

        # 落下タイマーを再スタート
        self.timer_start()

    def timer_event(self):
        'タイマー満期になった時の処理'

        # 下キー入力受付時と同じ処理を実行
        self.down_key_event(None)


class Application(tk.Tk):
    def __init__(self):
        super().__init__()

        # アプリウィンドウの設定
        self.geometry("400x600")
        self.title("テトリス")

        # テトリス生成
        game = TetrisGame(self)

        # イベントハンドラー生成
        EventHandller(self, game)


def main():
    'main関数'

    # GUIアプリ生成
    app = Application()
    app.mainloop()


if __name__ == "__main__":
    main()