from PySide6.QtWidgets import (QLabel, QFrame, QPushButton, QLineEdit,
                               QVBoxLayout, QWidget, QHBoxLayout, QComboBox)


import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from windows import RegistrationWindow, SelectWorkPlan
from Storage.SaveInputUserData import UserInputDataSave
from Storage.StaticDataSaver import StaticDataSaver
from tools.SystemMessages import SystemMessageBox
from tools.AlertMessage import show_alert_simple

from TOKEN import *


class MailVerificationClass(QFrame):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.database = controller.db_connect
        self.old_form_data = UserInputDataSave().get_data()
        self.frame_layout = QHBoxLayout(self)
        self.setup_ui()

    def setup_ui(self):
        """ Генерация интерфейса """
        widget = QWidget()
        widget.setFixedSize(350, 500)
        widget_layout = QVBoxLayout(widget)
        # Добавление Виджета с формой в центр окна
        self.frame_layout.addWidget(widget)

        # Создание интерфейса формы
        title = QLabel("Подтверждение почты")
        title.setWordWrap(True)
        title.setObjectName("title_style")
        widget_layout.addWidget(title)
        widget_layout.addStretch()

        instruction = QLabel("Нажмите на кнопку и отправьте письмо. Впишите код из письма в поле")
        instruction.setWordWrap(True)
        instruction.setObjectName("instruction_label")
        widget_layout.addWidget(instruction)

        self.mail_code = QLineEdit()
        self.mail_code.setMaxLength(6)
        self.mail_code.setObjectName("verification_mail_style")
        widget_layout.addWidget(self.mail_code)

        # Кнопка отправки письма
        message_sender = QPushButton("Отправить код")
        message_sender.setObjectName("simple_button")
        message_sender.clicked.connect(
            self.send_mail_code
        )
        widget_layout.addWidget(message_sender)

        # кнопка проверки кода
        code_checker = QPushButton("Проверить код")
        code_checker.setObjectName("hide_btn")
        code_checker.clicked.connect(
            self.check_mail_code
        )
        widget_layout.addWidget(code_checker)
        widget_layout.addStretch()

        back_btn = QPushButton("<- Назад")
        back_btn.setObjectName("hide_btn")
        back_btn.clicked.connect(
            lambda: self.controller.switch_window(RegistrationWindow.RegistrationWindowClass)
        )

        widget_layout.addWidget(back_btn)

    def check_mail_code(self):
        """ Метод проверки кода из письма """
        if self.mail_code.text() == str(StaticDataSaver().get_code()):
            self.controller.switch_window(SelectWorkPlan.SelectWorkPlanClass)
            return
        show_alert_simple(self, "Неверный код! Проверьте еще раз!")


    def send_mail_code(self):
        """ Метод отправки кода на почту"""
        try:
            # Генерация кода
            StaticDataSaver().generate_code()
            # Порт для отправки сообщения
            send_message_tool = smtplib.SMTP('smtp.mail.ru', 587)
            # Настройка шифрования
            send_message_tool.starttls()

            # Настройка письма для отправки
            self.send_code = StaticDataSaver().get_code()
            message = MIMEMultipart()
            message["From"] = mail_address  # Адрес из файла TOKEN.py
            message["To"] = UserInputDataSave().get_data()["Почта"]  # Адрес из ввода пользователя
            message['Subject'] = 'Код подтверждения создания аккаунта'
            body = f"Ваш код для подтверждения почты:\n{self.send_code}"
            message.attach(MIMEText(body, 'plain'))

            print("CODE::: ", self.send_code)
            # Отправка письма
            send_message_tool.login(mail_address, mail_token)
            send_message_tool.send_message(message)
            send_message_tool.quit()

            # Всплывающее сообщение
            show_alert_simple(self, "Письмо отправлено!")

        except Exception as error:
            print("send_mail_code() error:", error)
            SystemMessageBox("Произошла ошибка отправки сообщения! Проверьте свой почтовый адрес!").send_C_messsage()
            return

