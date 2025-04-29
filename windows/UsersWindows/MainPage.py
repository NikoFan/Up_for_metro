from PySide6.QtWidgets import (QLabel, QFrame, QPushButton, QLineEdit,
                               QVBoxLayout, QWidget, QHBoxLayout, QComboBox)

from PySide6.QtGui import QPixmap

from windows import LoginWindow
from Storage.SaveInputUserData import UserInputDataSave
from Storage.StaticDataSaver import StaticDataSaver
from tools.SystemMessages import SystemMessageBox
from tools.AlertMessage import *
from windows.UsersWindows.CreateRequest import CreateRequestClass


class MainUserPage(QFrame):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.database = controller.db_connect

        # Получение данных о пользователе из таблицы
        self.user_data: dict = self.database.take_user_data_by_id()

        self.frame_layout = QHBoxLayout(self)
        self.setup_ui()

    def setup_ui(self):
        """ Генерация интерфейса """
        widget = QWidget()
        widget.setFixedSize(350, 500)
        widget_layout = QVBoxLayout(widget)

        # Установка фото на экран
        widget_layout.addLayout(self.profile_picture_setter())

        # Установка ФИО пользователя
        user_name = QLabel(f"{self.user_data['ФИО']}")
        user_name.setWordWrap(True)
        user_name.setObjectName("account_title_text")
        widget_layout.addWidget(user_name)
        widget_layout.addStretch()

        # Кнопка Создать заявку
        create_request = QPushButton("Создать заявку")
        create_request.setObjectName("simple_button")
        create_request.clicked.connect(
            lambda: self.controller.switch_window(CreateRequestClass)
        )
        widget_layout.addWidget(create_request)

        # Кнопка просмотра истории
        history_look_btn = QPushButton("Прошлые поездки")
        history_look_btn.setObjectName("simple_button")
        history_look_btn.clicked.connect(
            lambda: print("История")
        )
        widget_layout.addWidget(history_look_btn)
        widget_layout.addStretch()

        # Кнопка выхода из аккаунта
        log_out_btn = QPushButton("Выйти")
        log_out_btn.setObjectName("hide_btn")
        log_out_btn.clicked.connect(
            self.log_out_btn_listener
        )
        widget_layout.addWidget(log_out_btn)

        self.frame_layout.addWidget(widget)

    def profile_picture_setter(self) -> QHBoxLayout:
        """ Метод установки иконки аккаунта """
        picture_socket = QLabel()
        picture_socket.setFixedSize(100, 100)
        picture_socket.setScaledContents(True)

        # Загрузка файла с иконкой
        user_picture = QPixmap("./Images/user_profile_picture.png")
        picture_socket.setPixmap(user_picture)

        # Горизонтальная разметка для центровки иконки
        central_hbox = QHBoxLayout()
        central_hbox.addWidget(QWidget())
        central_hbox.addWidget(picture_socket)
        central_hbox.addWidget(QWidget())

        return central_hbox

    def log_out_btn_listener(self):
        """ Метод выхода из аккаунта пользователя """
        if SystemMessageBox("Вы точно хотите выйти из аккаунта? Несохраненные действия будут удалены!").send_W_messsage():
            self.controller.switch_window(LoginWindow.LoginWindowClass)
