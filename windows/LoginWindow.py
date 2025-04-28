from PySide6.QtWidgets import (QLabel, QFrame, QPushButton, QLineEdit,
                               QVBoxLayout, QWidget, QHBoxLayout)
from windows import RegistrationWindow


class LoginWindowClass(QFrame):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.frame_layout = QHBoxLayout(self)
        self.setup_ui()

    def setup_ui(self):
        """ Генерация интерфейса """
        login_widget = QWidget()
        login_widget.setFixedSize(350, 500)
        login_widget_layout = QVBoxLayout(login_widget)
        # Добавление Виджета с формой в центр окна
        self.frame_layout.addWidget(login_widget)

        # Создание интерфейса формы
        title = QLabel("Авторизация")
        title.setObjectName("title_style")
        login_widget_layout.addWidget(title)
        login_widget_layout.addStretch()

        # Поле ввода логина
        login_hint = QLabel("Введите логин от аккаунта")
        login_hint.setObjectName("hint_text")
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Логин...")

        login_widget_layout.addWidget(login_hint)
        login_widget_layout.addWidget(self.login_input)


        # Поле ввода Пароля
        password_hint = QLabel("Введите пароль от аккаунта")
        password_hint.setObjectName("hint_text")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Пароль...")

        login_widget_layout.addWidget(password_hint)
        login_widget_layout.addWidget(self.password_input)
        login_widget_layout.addStretch()

        # Добавление кнопки "Войти"
        log_in_button = QPushButton("Войти")
        log_in_button.setObjectName("simple_button")
        log_in_button.clicked.connect(
            lambda : print("log in")
        )
        login_widget_layout.addWidget(log_in_button)

        registration_button = QPushButton("Нет аккаунта? Создайте!")
        registration_button.setObjectName("hide_btn")
        registration_button.clicked.connect(
            # Вызов метода для смены окон
            lambda: self.controller.switch_window(RegistrationWindow.RegistrationWindowClass)
        )
        login_widget_layout.addWidget(registration_button)

        login_widget_layout.addStretch()