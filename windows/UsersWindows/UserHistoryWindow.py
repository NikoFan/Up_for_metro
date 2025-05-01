from PySide6.QtWidgets import (QLabel, QFrame, QPushButton, QTextEdit,
                               QVBoxLayout, QWidget, QHBoxLayout, QScrollArea)

from Storage.StaticDataSaver import StaticDataSaver
from tools.AlertMessage import *
from windows.UsersWindows import MainPage


class UserHistoryWindowClass(QFrame):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.database = controller.db_connect

        print("-||-", StaticDataSaver().get_customer_id())

        # Получение данных о пользователе из таблицы
        self.user_data: dict = self.database.take_user_data_by_id()

        self.frame_layout = QHBoxLayout(self)
        self.setup_ui()

    def setup_ui(self):
        """ Генерация интерфейса """
        widget = QWidget()
        widget.setFixedSize(350, 500)
        widget_layout = QVBoxLayout(widget)

        # Установка ФИО пользователя
        title = QLabel("История поездок")
        title.setWordWrap(True)
        title.setObjectName("title_style")
        widget_layout.addWidget(title)

        # Область с прошлыми заявками
        old_requests_scroll_area = QScrollArea()
        old_requests_scroll_area.setObjectName("")
        old_requests_scroll_area.setWidgetResizable(True)

        # Контейнер для карточек с заявками
        requests_container = QWidget()
        requests_container.setObjectName("widget")
        container_layout = QVBoxLayout(requests_container)

        # Заполнение ScrollArea
        for request_example in self.database.take_requests_from_history():
            card = QWidget()
            card.setObjectName("req_card")
            card_layout = QVBoxLayout(card)

            from_to = QLabel(f"От {request_example['Start']} до {request_example['End']}")
            from_to.setWordWrap(True)
            from_to.setObjectName("verification_mail_style")

            last_time = QLabel(f"Завершилась: {request_example['Last']}")
            last_time.setWordWrap(True)
            last_time.setObjectName("hint_text")

            comment_text = QLabel(f"\nКомментарий:")
            comment_text.setWordWrap(True)
            comment_text.setObjectName("hint_text")

            user_comment = QTextEdit()
            user_comment.setText(request_example['Comment'])
            user_comment.setObjectName(str(request_example['Req_Id']) + "_text")

            change_comment_btn = QPushButton("Обновить комментарий")
            change_comment_btn.setObjectName("simple_button")
            change_comment_btn.clicked.connect(
                self.save_new_comment
            )
            change_comment_btn.setAccessibleName(str(request_example['Req_Id']))

            card_layout.addWidget(from_to)
            card_layout.addWidget(last_time)
            card_layout.addWidget(comment_text)
            card_layout.addWidget(user_comment)
            card_layout.addWidget(change_comment_btn)

            container_layout.addWidget(card)

        old_requests_scroll_area.setWidget(requests_container)
        widget_layout.addWidget(old_requests_scroll_area)

        # Кнопка возврата на главное окно
        go_back_btn = QPushButton("На главную")
        go_back_btn.setObjectName("hide_btn")
        go_back_btn.clicked.connect(
            self.go_back
        )
        widget_layout.addWidget(go_back_btn)

        self.frame_layout.addWidget(widget)

    def save_new_comment(self):
        """ Метод обновления комментария для записи """

        btn_name = self.sender().accessibleName()
        comment_text_block_text = f"'{self.findChild(QTextEdit, btn_name + '_text').toPlainText()}'"

        if len(comment_text_block_text) == 0:
            comment_text_block_text = "NULL"

        if self.database.update_request_comment(comment_text_block_text,
                                             int(btn_name)):
            show_alert_simple(self, "Комментарий обновлен!")
            return
        show_critical_alert_simple(self, "Ошибка на сервере! Попробуйте позже!")

    def go_back(self):
        """ Метод возвращения на главное окно """
        self.controller.switch_window(MainPage.MainUserPage)
