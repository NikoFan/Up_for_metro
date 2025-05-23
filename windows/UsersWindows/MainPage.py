from PySide6.QtWidgets import (QLabel, QFrame, QPushButton, QLineEdit,
                               QVBoxLayout, QWidget, QHBoxLayout, QComboBox)

from PySide6.QtGui import QPixmap

from windows import LoginWindow
from windows.UsersWindows import UserHistoryWindow
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

        # Активная заявка
        active_request = QWidget()
        active_request.setObjectName("active_req_style")
        active_request_layout = QVBoxLayout(active_request)

        # Данные активной заявки
        request_data: dict = self.database.take_user_active_request_by_id()
        # Разрешение на создание новой заявки. (чтобы пользователь не создавал несколько)
        create_new_req_approval: bool = True
        if len(request_data) != 0:
            create_new_req_approval = False

        # Заполнение виджета с активной заявкой
        if not create_new_req_approval:
            req_title = QLabel("Активная заявка")
            req_title.setObjectName("small_title_style")
            req_title.setWordWrap(True)

            route_info = QLabel(f"От {request_data['Начало']} до {request_data['Конец']}")
            route_info.setWordWrap(True)
            route_info.setObjectName("hint_text")

            req_date_info = QLabel(f"Дата: {request_data['Дата']}")
            req_date_info.setWordWrap(True)
            req_date_info.setObjectName("hint_text")

            # Кнопка отмены (Можно отменить если еще не началась)
            cancel_btn = QPushButton("Отменить")
            cancel_btn.setObjectName("hide_btn")
            cancel_btn.setEnabled(request_data['Статус'] == "Не начата")
            cancel_btn.clicked.connect(
                lambda: self.cancel_active_request(request_data['id'])
            )

            # Добавление элементов в интерфейс
            active_request_layout.addWidget(req_title)
            active_request_layout.addWidget(route_info)
            active_request_layout.addWidget(req_date_info)
            active_request_layout.addWidget(cancel_btn)
        else:
            req_title = QLabel("Активных заявок нет!")
            req_title.setObjectName("small_title_style")
            req_title.setWordWrap(True)

            active_request_layout.addWidget(req_title)

        widget_layout.addWidget(active_request)

        # Кнопка Создать заявку
        create_request = QPushButton("Создать заявку")
        create_request.setObjectName("simple_button")
        # Установка активности кнопки в зависимости от наличия заявки
        create_request.setEnabled(create_new_req_approval)
        create_request.clicked.connect(
            lambda: self.controller.switch_window(CreateRequestClass)
        )
        widget_layout.addWidget(create_request)

        # Кнопка просмотра истории
        history_look_btn = QPushButton("Прошлые поездки")
        history_look_btn.setObjectName("simple_button")
        history_look_btn.clicked.connect(
            lambda: self.controller.switch_window(UserHistoryWindow.UserHistoryWindowClass)
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

    def cancel_active_request(self, request_id: int):
        """ Метод отмены активной заявки """
        if SystemMessageBox("Вы точно хотите отменить заявку? "
                            "Отменить действие будет невозможно! "
                            "Группа будет расформирована, и для формирования новой потребуется время").send_W_messsage():
            self.database.cancel_active_req_in_table(
                new_req_status="Отменена",
                request_id_number=request_id
            )
        self.controller.switch_window(MainUserPage)

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
        if SystemMessageBox(
                "Вы точно хотите выйти из аккаунта? Несохраненные действия будут удалены!").send_W_messsage():
            self.controller.switch_window(LoginWindow.LoginWindowClass)
