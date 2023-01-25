import sys
import time

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget, QLabel, QGridLayout, QHBoxLayout, QPushButton


class GameCore:
    def __init__(self):
        self.nums = [i for i in range(1, 36)]
        self.index = -1
        self.selected_times = 0
        self.front = []
        self.end = []

    def next(self):
        self.index += 1
        if self.index >= len(self.nums):
            self.index = 0

        return self.nums[self.index]

    def select(self):
        self.selected_times += 1
        if self.selected_times < 6:
            self.front.append(self.nums.pop(self.index))
        else:
            self.end.append(self.nums.pop(self.index))

        self.index -= 1

        if self.selected_times == 5:
            self.nums = [i for i in range(1, 13)]
            self.index = -1

        return ', '.join([str(i).zfill(2) for i in list(sorted(self.front)) + list(sorted(self.end))]), self.selected_times > 6


class Trigger(QThread):
    trigger_signal = pyqtSignal()

    def __init__(self):
        super().__init__()

    def run(self) -> None:
        while True:
            self.trigger_signal.emit()
            time.sleep(0.1)


class Simulator(QWidget):
    groups_title_text = ['第一组', '第二组', '第三组', '第四组', '第五组']

    def __init__(self):
        super().__init__()
        self.title = QLabel('摇奖开始')
        self.top_screen = QLabel('点击<开始>进行摇奖')
        self.groups_title = [QLabel(self.groups_title_text[i] + ' : ') for i in range(5)]
        self.groups = [QLabel() for _ in range(5)]
        self.start_btn = QPushButton('开始(space)')
        self.reset_btn = QPushButton('重置(backspace)')
        self.trigger = None
        self.game_core = GameCore()
        self.init_ui()

        self.game_running = False
        self.group_index = 0

    def init_ui(self):
        self.resize(400, 300)
        self.center()
        self.create_layout()

        self.setWindowTitle('彩票生成模拟器')
        self.show()

    def center(self):
        qr = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()

        qr.moveCenter(center_point)
        self.move(qr.topLeft())

    def create_layout(self):
        bold_font = QFont('Microsoft YaHei', 12, QFont.Bold)
        text_font = QFont('Microsoft YaHei', 10)

        self.title.setAlignment(Qt.AlignCenter)
        self.title.setFont(bold_font)

        self.top_screen.setAlignment(Qt.AlignCenter)
        self.top_screen.setFont(text_font)

        grid_layout = QGridLayout()
        grid_layout.addWidget(self.title, 0, 0)
        grid_layout.addWidget(self.top_screen, 1, 0)

        for i in range(5):
            self.groups_title[i].setFont(text_font)
            self.groups[i].setFont(text_font)

            h_layout = QHBoxLayout()
            h_layout.addWidget(self.groups_title[i], 4)
            h_layout.addWidget(self.groups[i], 9)
            grid_layout.addLayout(h_layout, 2 + i, 0)

        self.start_btn.setFont(text_font)
        self.start_btn.resize(self.start_btn.sizeHint())
        self.start_btn.setShortcut('space')
        self.start_btn.clicked.connect(self.start_click)

        self.reset_btn.setFont(text_font)
        self.reset_btn.resize(self.start_btn.sizeHint())
        self.reset_btn.setShortcut('backspace')
        self.reset_btn.clicked.connect(self.reset_click)

        h_layout = QHBoxLayout()
        h_layout.addWidget(self.start_btn)
        h_layout.addWidget(self.reset_btn)
        grid_layout.addLayout(h_layout, 7, 0)

        self.setLayout(grid_layout)

    def start_click(self):
        if not self.game_running:
            self.start_btn.setText('选择(space)')

            self.game_core = GameCore()

            self.trigger = Trigger()
            self.trigger.trigger_signal.connect(self.display)
            self.trigger.finished.connect(self.reset)
            self.trigger.start()
            self.game_running = True
            return

        result, finished = self.game_core.select()
        self.groups[self.group_index].setText(result)
        if finished:
            self.game_core = GameCore()
            self.groups_title[self.group_index].setText(self.groups_title_text[self.group_index] + '(完成) : ')
            self.group_index += 1
        self.top_screen.setText(str(self.game_core.next()))

        if self.group_index >= 5:
            self.start_btn.setEnabled(False)

    def reset(self):
        self.game_running = False
        self.group_index = 0
        self.start_btn.setText('开始(space)')
        self.top_screen.setText('点击<开始>进行摇奖')
        for i in range(5):
            self.groups_title[i].setText(self.groups_title_text[i] + ' : ')
            self.groups[i].setText('')
        self.start_btn.setEnabled(True)

    def display(self):
        self.top_screen.setText(str(self.game_core.next()))

    def reset_click(self):
        if self.trigger is None:
            return
        self.trigger.terminate()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    s = Simulator()
    sys.exit(app.exec_())
