import sys
import random
from PyQt6.QtWidgets import QLineEdit, QDialogButtonBox, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QDialog, QMessageBox, QApplication
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QFont
from base import DatabaseManager


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)

class Cell(QPushButton):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.is_mine = False
        self.is_flagged = False
        self.is_revealed = False
        self.neighbor_mines = 0

class Minesweeper(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Сапёр")
        self.setFixedSize(820, 740)
        self.central_widget = QWidget()
        self.setStyleSheet("background-color: #bfe6b8;")
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.menu_widget = QWidget()
        self.menu_layout = QVBoxLayout()
        self.menu_widget.setLayout(self.menu_layout)

        self.game_widget = QWidget()
        self.game_layout = QVBoxLayout()
        self.game_widget.setLayout(self.game_layout)

        self.create_menu()
        self.layout.addWidget(self.menu_widget)

        self.records_button.clicked.connect(self.show_records)
        self.db_manager = DatabaseManager()


    def create_menu(self):
        image_label = QLabel()
        pixmap = QPixmap("mina.png")
        pixmap = pixmap.scaled(650, 650, Qt.AspectRatioMode.KeepAspectRatio)
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        button_font = QFont()
        button_font.setPointSize(20)
        button_font.setBold(True)

        self.new_game_button = QPushButton("Новая игра")
        self.records_button = QPushButton("Рекорды")
        self.exit_button = QPushButton("Выход")

        buttons = [self.new_game_button, self.records_button, self.exit_button]

        for button in buttons:
            button.setFont(button_font)
            button.setStyleSheet("""
                QPushButton {
                    padding: 10px;
                    background-color: #4d1819;
                    color: #e1f2bb;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: rgb(56, 64, 29);
                }
                QPushButton:pressed {
                    background-color: rgb(56, 64, 29);
                }
            """)

        self.new_game_button.clicked.connect(self.show_difficulty_selection)
        self.exit_button.clicked.connect(self.close)

        # Добавляем виджеты в layout
        self.menu_layout.addWidget(image_label)
        self.menu_layout.addWidget(self.new_game_button)
        self.menu_layout.addWidget(self.records_button)
        self.menu_layout.addWidget(self.exit_button)

    def show_difficulty_selection(self):
        self.difficulty_widget = QWidget()
        self.difficulty_layout = QVBoxLayout()
        self.difficulty_widget.setLayout(self.difficulty_layout)


        self.novice_button = QPushButton("Новичок (9x9)")
        self.novice_button.clicked.connect(lambda: self.start_game(9, 9, 10))
        self.amateur_button = QPushButton("Любитель (16x16)")
        self.amateur_button.clicked.connect(lambda: self.start_game(16, 16, 40))
        self.professional_button = QPushButton("Профессионал (30x16)")
        self.professional_button.clicked.connect(lambda: self.start_game(30, 16, 99))

        button_font = QFont()
        button_font.setPointSize(20)
        button_font.setBold(True)

        buttons = [self.novice_button, self.amateur_button, self.professional_button]

        for button in buttons:
            button.setFont(button_font)

            button.setStyleSheet("""
                       QPushButton {
                           padding: 10px;
                           background-color: rgb(56, 64, 29);
                           color: white;
                           border-radius: 5px;
                       }
                       QPushButton:hover {
                           background-color: #45a049;
                       }
                       QPushButton:pressed {
                           background-color: #3d8b40;
                       }
                   """)


        self.difficulty_layout.addWidget(self.novice_button)
        self.difficulty_layout.addWidget(self.amateur_button)
        self.difficulty_layout.addWidget(self.professional_button)

        self.layout.replaceWidget(self.menu_widget, self.difficulty_widget)
        self.menu_widget.hide()
        self.difficulty_widget.show()

    def start_game(self, width, height, mines):
        self.width = width
        self.height = height
        self.mines = mines
        self.flags = mines
        self.time = 0
        self.first_click = True

        # Удаляем старое игровое поле, если оно существует
        if hasattr(self, 'game_widget'):
            self.game_widget.deleteLater()

        # Создаем новое игровое поле
        self.game_widget = QWidget()
        self.game_layout = QVBoxLayout()
        self.game_widget.setLayout(self.game_layout)

        self.create_game_board()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)

        # Заменяем виджет в основном layout
        if self.layout.indexOf(self.difficulty_widget) != -1:
            self.layout.replaceWidget(self.difficulty_widget, self.game_widget)
            self.difficulty_widget.hide()
        elif self.layout.indexOf(self.menu_widget) != -1:
            self.layout.replaceWidget(self.menu_widget, self.game_widget)
            self.menu_widget.hide()
        self.game_widget.show()

    def create_game_board(self):
        # Создаем контейнер для игрового поля
        game_container = QWidget()
        window_size = 600
        if self.width == 30:
            window_size = 780
        cell_size = min(window_size // self.width, window_size // self.height)
        game_container.setFixedSize(cell_size * self.width, cell_size * self.height)

        self.board = [[Cell(x, y) for y in range(self.height)] for x in range(self.width)]

        # Размещаем кнопки
        for x in range(self.width):
            for y in range(self.height):
                cell = self.board[x][y]
                cell.setParent(game_container)
                cell.setGeometry(x * cell_size, y * cell_size, cell_size, cell_size)
                cell.setFixedSize(cell_size, cell_size)
                cell.clicked.connect(self.cell_clicked)
                cell.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
                cell.customContextMenuRequested.connect(self.right_click)

                font = QFont()
                font.setPixelSize(cell_size // 2)  # Размер шрифта - половина высоты ячейки
                cell.setFont(font)

                cell.setStyleSheet("""
                       Cell {
                           background-color: #9cb092;
                           border: 1px solid #0a3b1e;
                           margin: 0px;
                           padding: 0px;
                       }
                   """)

        # Создаем информационную панель
        info_container = QWidget()
        info_layout = QHBoxLayout(info_container)
        self.flag_label = QLabel(f"Флаги: {self.flags}")
        self.time_label = QLabel("Время: 0")
        info_layout.addWidget(self.flag_label)
        info_layout.addWidget(self.time_label)
        info_container.setLayout(info_layout)

        # Очищаем предыдущий layout
        while self.game_layout.count():
            child = self.game_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Добавляем элементы в основной layout
        self.game_layout.addWidget(info_container)
        self.game_layout.addWidget(game_container)
        self.game_layout.setAlignment(game_container, Qt.AlignmentFlag.AlignCenter)

    def place_mines(self, first_x, first_y):
        safe_cells = [(first_x, first_y)] + self.get_neighbors(first_x, first_y)
        all_cells = [(x, y) for x in range(self.width) for y in range(self.height) if (x, y) not in safe_cells]
        mine_positions = random.sample(all_cells, min(self.mines, len(all_cells)))
        for x, y in mine_positions:
            self.board[x][y].is_mine = True

        for nx, ny in self.get_neighbors(first_x, first_y):
            self.board[nx][ny].neighbor_mines = 0

    def calculate_neighbors(self):
        for x in range(self.width):
            for y in range(self.height):
                if not self.board[x][y].is_mine:
                    neighbors = self.get_neighbors(x, y)
                    self.board[x][y].neighbor_mines = sum(1 for nx, ny in neighbors if self.board[nx][ny].is_mine)

    def get_neighbors(self, x, y):
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    neighbors.append((nx, ny))
        return neighbors

    def cell_clicked(self):
        cell = self.sender()
        if cell.is_revealed and cell.neighbor_mines > 0:
            # Открываем все соседние ячейки, которые не помечены флажком
            neighbors = self.get_neighbors(cell.x, cell.y)
            for nx, ny in neighbors:
                if not self.board[nx][ny].is_flagged and not self.board[nx][ny].is_revealed:
                    if self.board[nx][ny].is_mine:
                        self.game_over()
                        return
                    self.reveal_cell(nx, ny)
            self.check_win()
            return

        if cell.is_flagged or cell.is_revealed:
            return

        if self.first_click:
            self.place_mines(cell.x, cell.y)
            self.calculate_neighbors()
            self.first_click = False
            self.timer.start(1000)

        if cell.is_mine:
            self.game_over()
        else:
            self.reveal_cell(cell.x, cell.y)
            self.check_win()

    def right_click(self, pos):
        cell = self.sender()
        if not cell.is_revealed:
            if cell.is_flagged:
                cell.is_flagged = False
                cell.setText("")
                self.flags += 1
            else:
                cell.is_flagged = True
                cell.setText("🚩")
                self.flags -= 1
            self.flag_label.setText(f"Осталось флагов: {self.flags}")

    def reveal_cell(self, x, y):
        cell = self.board[x][y]
        if cell.is_revealed or cell.is_flagged:
            return

        cell.is_revealed = True
        cell.setStyleSheet("""
                Cell {
                    background-color: #ccdbca;
                    border: 1px solid #0a3b1e;
                    margin: 0px;
                    padding: 0px;
                }
            """)


        if cell.neighbor_mines > 0:
            cell.setText(str(cell.neighbor_mines))
            color = self.get_number_color(cell.neighbor_mines)
            cell.setStyleSheet(f"""
                    Cell {{
                        background-color: #E0E0E0;
                        border: 1px solid #0a3b1e;
                        margin: 0px;
                        padding: 0px;
                        color: {color};
                        font-weight: bold;
                    }}
                """)
        else:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        self.reveal_cell(nx, ny)

    def get_number_color(self, number):
        colors = ['#0000FF', '#008000', '#FF0000', '#000080', '#800000', '#008080', '#000000', '#808080']
        return colors[number - 1] if 1 <= number <= 8 else '#000000'

    def game_over(self):
        self.timer.stop()
        for row in self.board:
            for cell in row:
                if cell.is_mine:
                    cell.setText("💣")
                cell.setEnabled(False)
        msg = QMessageBox()
        msg.setWindowTitle("Игра окончена")
        msg.setText("Вы проиграли!")
        msg = self.msg_style(msg)
        msg.exec()
        self.return_to_menu()

    def check_win(self):
        if all(cell.is_revealed or cell.is_mine for row in self.board for cell in row):
            self.timer.stop()

            # Создаем кастомный диалог
            custom_dialog = QDialog(self)
            custom_dialog = self.msg_style(custom_dialog)
            custom_dialog.setWindowTitle("Ввод имени")
            custom_dialog.setModal(True)

            layout = QVBoxLayout()

            win_label = QLabel(f"Победа! Вы выиграли за {self.time} секунд!")
            layout.addWidget(win_label)

            recent_names = self.db_manager.get_recent_names()

            name_input = QLineEdit()

            # Создаем кнопки для последних имен
            if recent_names:
                recent_label = QLabel("Последние использованные имена:")
                layout.addWidget(recent_label)

                for name in recent_names:
                    name_button = QPushButton(name)
                    name_button.clicked.connect(lambda checked, n=name: name_input.setText(n))
                    layout.addWidget(name_button)

            layout.addWidget(QLabel("Ваше имя:"))
            layout.addWidget(name_input)

            button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
            button_box.accepted.connect(custom_dialog.accept)
            layout.addWidget(button_box)

            custom_dialog.setLayout(layout)

            if recent_names:
                name_input.setText(recent_names[0])

            if custom_dialog.exec() == QDialog.DialogCode.Accepted:
                name = name_input.text()
                if name:
                    self.db_manager.save_score(name, self.width, self.time)

            self.return_to_menu()

    def show_records(self):
        s = {9: 'Новичок', 16: 'Любитель', 30: 'Профи'}
        record_text = ""
        for i in [9, 16, 30]:
            records = self.db_manager.get_records_by_difficulty(i)

            record_text += f"<h2>{s[i]}:</h2>"
            if records:
                for j, record in enumerate(records):
                    name = record[0]
                    time = record[1]
                    record_text += f"<p>{j + 1}. {name} - {time} сек.</p>"
            else:
                record_text += "<p>Нет записей.</p>"
            record_text += "<br>"

        msg = QMessageBox()
        msg.setWindowTitle("Рекорды")
        msg.setText(record_text)
        msg = self.msg_style(msg)
        msg.exec()

    def closeEvent(self, event):
        # Закрываем соединение с БД при закрытии приложения
        self.db_manager.close_connection()
        event.accept()

    def msg_style(self, msg):
        msg.setStyleSheet("""
                    QMessageBox {
                        background-color: #c1e6b5; 
                    }
                    QLabel {
                        min-width: 300px;
                        font-size: 16pt;
                        font-family: 'Trebuchet MS';
                        color: #520c06;
                        background-color: #c1e6b5;
                    }
                    QPushButton {
                        background-color: #436946;
                        color: white;
                        padding: 10px;
                        border-radius: 3px;
                        font-size: 12pt;
                        font-family: 'Trebuchet MS';
                    }
                    QPushButton:hover {
                        background-color: #5F9EA0;
                    }
                    h2 {
                        color: #FFD700;
                        font-family: 'Trebuchet MS';
                    }
                    p {
                        font-size: 14pt;
                        font-family: 'Trebuchet MS';
                        color: #E0FFFF;
                    }
                """)
        return msg

    def update_timer(self):
        self.time += 1
        self.time_label.setText(f"Время: {self.time}")

    def return_to_menu(self):
        self.layout.replaceWidget(self.game_widget, self.menu_widget)
        self.game_widget.hide()
        self.menu_widget.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Minesweeper()
    window.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())