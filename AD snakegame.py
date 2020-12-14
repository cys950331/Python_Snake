from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import random
import sys


class SnakeGame(QMainWindow):
    def __init__(self):
        super(SnakeGame, self).__init__()
        self.game = Game(self)

        self.statusbar = self.statusBar()
        self.game.SIGNAL[str].connect(self.statusbar.showMessage)

        self.setCentralWidget(self.game)
        self.setWindowTitle('Snake game')
        self.resize(600, 400)

        # 가운데에서 창이 열리도록 설정
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2,
                  (screen.height()-size.height())/2)

        self.game.start()
        self.show()


class Game(QFrame):
    SIGNAL = pyqtSignal(str)  # 원하는 이벤트(시그널)을 직접 정의
    SPEED = 100  # 빠르기
    WIDTHINBLOCKS = 60  # 맵의 가로 블럭 수
    HEIGHTINBLOCKS = 40  # 맵의 세로 블럭 수

    def __init__(self, parent):
        super(Game, self).__init__(parent)
        self.timer = QBasicTimer()
        self.snake = [[5, 5], [5, 5]]  # 시작 위치
        self.current_x_head = self.snake[0][0]
        self.current_y_head = self.snake[0][1]
        self.food = []  # 음식 빈리스트
        self.grow_snake = False
        self.game = []
        self.direction = 1  # 이동 방향
        self.drop_food()  # 먹이 놓을 장소 지정 리스트
        self.setFocusPolicy(Qt.StrongFocus)
        self.sgame = False


    def square_width(self):  # 맵 가로 크기
        return self.contentsRect().width() / Game.WIDTHINBLOCKS

    def square_height(self):  # 맵 세로 크기
        return self.contentsRect().height() / Game.HEIGHTINBLOCKS

    def start(self):
        # class 내부에서 self.시그널객체.emit()로 발생시킬 수 있다.
        self.SIGNAL.emit("level: " + str(len(self.snake) - 2))
        self.timer.start(Game.SPEED, self)

    def paintEvent(self, event):
        painter = QPainter(self)  # 색깔 입력
        rect = self.contentsRect()  # 맵의 크기
        boardtop = -40

        for pos in self.snake:
            self.draw_square1(painter, rect.left() + pos[0] * self.square_width(),
                              boardtop + pos[1] * self.square_height())
        for pos in self.food:
            self.draw_square2(painter, rect.left() + pos[0] * self.square_width(),
                              boardtop + pos[1] * self.square_height())

    # snake 색깔 설정

    def draw_square1(self, painter, x, y):
        color = QColor(0x369F36)
        painter.fillRect(x, y, self.square_width(),
                         self.square_height(), color)

    # food 색깔 설정

    def draw_square2(self, painter, x, y):
        color = QColor(0xFF0000)
        painter.fillRect(x, y, self.square_width(),
                         self.square_height(), color)

    # 방향키로 이동

    def keyPressEvent(self, event):
        key = event.key()
        # direction = 1(왼쪽) / direction = 2(오른쪽) / direction = 3(아래) / direction = 4(위)
        if key == Qt.Key_Left:
            if self.direction != 2:
                self.direction = 1
        elif key == Qt.Key_Right:
            if self.direction != 1:
                self.direction = 2
        elif key == Qt.Key_Down:
            if self.direction != 4:
                self.direction = 3
        elif key == Qt.Key_Up:
            if self.direction != 3:
                self.direction = 4

    def move_snake(self):
        if self.direction == 1:
            self.current_x_head, self.current_y_head = self.current_x_head - 1, self.current_y_head
            if self.current_x_head < 0:
                self.current_x_head = Game.WIDTHINBLOCKS - 1
        if self.direction == 2:
            self.current_x_head, self.current_y_head = self.current_x_head + 1, self.current_y_head
            if self.current_x_head == Game.WIDTHINBLOCKS:
                self.current_x_head = 0
        if self.direction == 3:
            self.current_x_head, self.current_y_head = self.current_x_head, self.current_y_head + 1
            if self.current_y_head == Game.HEIGHTINBLOCKS:
                self.current_y_head = 0
        if self.direction == 4:
            self.current_x_head, self.current_y_head = self.current_x_head, self.current_y_head - 1
            if self.current_y_head < 0:
                self.current_y_head = Game.HEIGHTINBLOCKS

        head = [self.current_x_head, self.current_y_head]
        self.snake.insert(0, head)
        if not self.grow_snake:
            self.snake.pop()
        else:
            self.SIGNAL.emit("level: " + str(len(self.snake)-2))
            self.grow_snake = False

    def timerEvent(self, event):
        if event.timerId() == self.timer.timerId():
            self.move_snake()
            self.is_food_collision()
            self.End()
            self.update()

    def End(self):  # 뱀의 꼬리가 잡히면 끝이난다.
        for i in range(1, len(self.snake)):
            if self.snake[i] == self.snake[0]:
                self.SIGNAL.emit(str('GAME OVER'))
                self.snake = [[x, y]
                              for x in range(0, 61) for y in range(0, 41)]
                self.timer.stop()
                self.update()

    def is_food_collision(self):  # 뱀이 음식을 먹을 때
        for pos in self.food:
            if pos == self.snake[0]:  # 뱀의 머리에 닿을 시
                self.food.remove(pos)
                Game.SPEED -= 2
                self.timer.start(Game.SPEED, self)
                self.drop_food()  # 음식 위치 리셋
                self.grow_snake = True

    def drop_food(self):  # 음식 위치
        x = random.randint(3, 55)  # 가로 크기가 60 이므로 58 까지
        y = random.randint(3, 35)  # 세로 크기가 40 이므로 38 까지
        self.food.append([x, y])


    


if __name__ == '__main__':
    app = QApplication([])
    launch_game = SnakeGame()
    sys.exit(app.exec_())
