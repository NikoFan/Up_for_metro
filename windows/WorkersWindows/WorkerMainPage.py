from PySide6.QtWidgets import (QLabel, QFrame, QPushButton, QTextEdit,
                               QVBoxLayout, QWidget, QHBoxLayout, QComboBox)

from PySide6.QtGui import QPixmap

from windows import LoginWindow
from windows.UsersWindows import UserHistoryWindow
from Storage.SaveInputUserData import UserInputDataSave
from Storage.StaticDataSaver import StaticDataSaver
from tools.SystemMessages import SystemMessageBox
from tools.AlertMessage import *
from windows.UsersWindows.CreateRequest import CreateRequestClass


class MainWorkerPage(QFrame):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.database = controller.db_connect
        # Получение данных о сотруднике из таблицы
        self.user_data: dict = self.database.take_workers_data_by_id()

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
        request_data: dict = self.database.take_active_request_information_for_worker()
        # Разрешение на создание новой заявки. (чтобы пользователь не создавал несколько)
        create_new_req_approval: bool = True
        if len(request_data) != 0:
            create_new_req_approval = False

        # Заполнение виджета с активной заявкой
        if not create_new_req_approval:
            req_title = QLabel("Активная заявка")
            req_title.setObjectName("small_title_style")
            req_title.setWordWrap(True)

            route_info = QLabel(f"От {request_data['Начальная_станция']} до {request_data['Конечная_станция']}")
            route_info.setWordWrap(True)
            route_info.setObjectName("hint_text")

            req_date_info = QLabel(f"Дата: {request_data['Дата_начала']}")
            req_date_info.setWordWrap(True)
            req_date_info.setObjectName("hint_text")
            active_request_layout.addWidget(req_title)
            active_request_layout.addWidget(route_info)
            active_request_layout.addWidget(req_date_info)

            if request_data['Статус_заявки'] == "Не начата":
                action_req_btn = QPushButton("Начать поездку")

                action_req_btn.clicked.connect(
                    self.start_active_request
                )

            else:  # если статус заявки "В процессе"
                # Место для комментария от сотрудника
                comment_place = QTextEdit()
                comment_place.setPlaceholderText("Впишите комментарий к поездке!")
                comment_place.setObjectName(str(request_data['id']))
                active_request_layout.addWidget(comment_place)

                action_req_btn = QPushButton("Завершить поездку")
                action_req_btn.clicked.connect(
                    self.end_active_request
                )

            # Добавление элементов в интерфейс
            action_req_btn.setObjectName("hide_btn")
            action_req_btn.setAccessibleName(str(request_data['id']))
            active_request_layout.addWidget(action_req_btn)
        else:
            req_title = QLabel("Активных заявок нет!")
            req_title.setObjectName("small_title_style")
            req_title.setWordWrap(True)

            active_request_layout.addWidget(req_title)

        widget_layout.addWidget(active_request)

        # Кнопка выхода из аккаунта
        log_out_btn = QPushButton("Выйти")
        log_out_btn.setObjectName("hide_btn")
        log_out_btn.clicked.connect(
            self.log_out_btn_listener
        )
        widget_layout.addWidget(log_out_btn)

        self.frame_layout.addWidget(widget)

    def start_active_request(self):
        """ Метод начала исполнения активной заявки """
        sender_name = self.sender().accessibleName()
        print("начинаем заявку номер ", sender_name)

        if self.database.start_request_action(int(sender_name)):
            show_alert_simple(self, "Поездка началась!")
            self.controller.switch_window(MainWorkerPage)
            return
        show_critical_alert_simple(self, "Ошибка на сервере!")


    def end_active_request(self):
        """ Метод окончания исполнения активной заявки """
        sender_name = self.sender().accessibleName()
        print("заканчиваем заявку номер ", sender_name)

        comment_text = self.findChild(QTextEdit, sender_name).toPlainText()


        if self.database.cancel_active_req_in_table(
                new_req_status="Завершена",
                request_id_number=int(sender_name),
                comment_text=comment_text
        ):
            show_alert_simple(self, "Поездка успешно завершена!")
            self.controller.switch_window(MainWorkerPage)
            return
        show_critical_alert_simple(self, "Ошибка на сервере!")

    def profile_picture_setter(self) -> QHBoxLayout:
        """ Метод установки иконки аккаунта """
        picture_socket = QLabel()
        picture_socket.setFixedSize(100, 100)
        picture_socket.setScaledContents(True)

        # Загрузка файла с иконкой
        user_picture = QPixmap("./Images/worker_profile_picture.png")
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
