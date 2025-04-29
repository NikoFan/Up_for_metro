from PySide6.QtWidgets import (QLabel, QFrame, QPushButton, QLineEdit,
                               QVBoxLayout, QWidget, QHBoxLayout, QComboBox)

from windows import (LoginWindow, MailVerificationWindow,
                     HandicappedLvlInput)
from Storage.SaveInputUserData import UserInputDataSave
from Storage.StaticDataSaver import StaticDataSaver


class RegistrationWindowClass(QFrame):
    def __init__(self, controller):
        super().__init__()
        # Пересоздание кода для почты, для исключения фактора дырявой верификации
        StaticDataSaver.generate_code()

        self.controller = controller
        self.old_input_data = UserInputDataSave().get_data()
        self.frame_layout = QHBoxLayout(self)
        self.setup_ui()

    def setup_ui(self):
        """ Генерация интерфейса """
        registration_widget = QWidget()
        registration_widget.setFixedSize(350, 700)
        registration_widget_layout = QVBoxLayout(registration_widget)
        # Добавление Виджета с формой в центр окна
        self.frame_layout.addWidget(registration_widget)

        # Создание интерфейса формы
        title = QLabel("Создание аккаунта")
        title.setObjectName("title_style")
        registration_widget_layout.addWidget(title)
        registration_widget_layout.addStretch()

        # Поле для ввода ФИО
        user_name_hint = QLabel("Введите ФИО")
        user_name_hint.setObjectName("hint_text")
        self.user_name_input = QLineEdit()
        self.user_name_input.setText(self.old_input_data["ФИО"])

        registration_widget_layout.addWidget(user_name_hint)
        registration_widget_layout.addWidget(self.user_name_input)

        # Поле ввода логина
        login_hint = QLabel("Введите логин")
        login_hint.setObjectName("hint_text")
        self.login_input = QLineEdit()
        self.login_input.setText(self.old_input_data["Логин"])

        registration_widget_layout.addWidget(login_hint)
        registration_widget_layout.addWidget(self.login_input)

        # Поле ввода Пароля
        password_hint = QLabel("Введите пароль")
        password_hint.setObjectName("hint_text")
        self.password_input = QLineEdit()
        self.password_input.setText(self.old_input_data["Пароль"])

        registration_widget_layout.addWidget(password_hint)
        registration_widget_layout.addWidget(self.password_input)

        # Добавление поля для почты
        mail_hint = QLabel("Введите почту")
        mail_hint.setObjectName("hint_text")
        # Простая разметка, для установки близко расположенных элементов интерфейса
        input_mail_hbox = QHBoxLayout()
        self.mail_input = QLineEdit()
        self.mail_input.setText(self.old_input_data["Почта"].replace("@mail.ru", ""))

        mail_element = QLabel("@mail.ru")
        mail_element.setObjectName("small_text")

        # Добавление поля для ввода и почтового ящика в горизонтальную разметку
        input_mail_hbox.addWidget(self.mail_input)
        input_mail_hbox.addWidget(mail_element)

        registration_widget_layout.addWidget(mail_hint)
        registration_widget_layout.addLayout(input_mail_hbox)

        # Поле для ввода телефона
        phone_hint = QLabel("Введите номер телефона")
        phone_hint.setObjectName("hint_text")
        # Простая разметка, для установки близко расположенных элементов интерфейса
        input_phone_hbox = QHBoxLayout()
        self.phone_input = QLineEdit()
        self.phone_input.setText(self.old_input_data["Телефон"].replace("+7", ""))
        self.phone_input.setInputMask("0000000000")

        phone_element = QLabel("+7")
        phone_element.setObjectName("small_text")

        # Добавление поля для ввода и почтового ящика в горизонтальную разметку
        input_phone_hbox.addWidget(phone_element)
        input_phone_hbox.addWidget(self.phone_input)

        registration_widget_layout.addWidget(phone_hint)
        registration_widget_layout.addLayout(input_phone_hbox)

        # Поле для выбора Пола
        sex_hint = QLabel("Укажите пол")
        sex_hint.setObjectName("hint_text")
        self.sex = QComboBox()
        const_sex = ["Мужчина", "Женщина"]
        const_sex.remove(self.old_input_data["Пол"])
        self.sex.addItems([self.old_input_data["Пол"]] + const_sex)

        registration_widget_layout.addWidget(sex_hint)
        registration_widget_layout.addWidget(self.sex)

        # Поле для выбора Роли
        role_hint = QLabel("Кем вы хотите быть в системе?")
        role_hint.setObjectName("hint_text")
        self.role = QComboBox()
        roles_const = ["Волонтер", "Пользователь"]
        roles_const.remove(self.old_input_data["Роль"])
        self.role.addItems([self.old_input_data["Роль"]] + roles_const)

        registration_widget_layout.addWidget(role_hint)
        registration_widget_layout.addWidget(self.role)

        registration_widget_layout.addStretch()

        # Добавление кнопки "Создать аккаунт"
        log_in_button = QPushButton("Создать аккаунт")
        log_in_button.setObjectName("simple_button")
        log_in_button.clicked.connect(
            self.do_registration_account
        )
        registration_widget_layout.addWidget(log_in_button)

        registration_button = QPushButton("Аккаунт есть?")
        registration_button.setObjectName("hide_btn")
        registration_button.clicked.connect(
            lambda: self.controller.switch_window(LoginWindow.LoginWindowClass)
        )
        registration_widget_layout.addWidget(registration_button)

        registration_widget_layout.addStretch()

    def do_registration_account(self):
        """ Обработчик нажатия на кнопку создания аккаунта """
        form_input_data: dict = {
            "ФИО": self.user_name_input.text(),
            "Логин": self.login_input.text(),
            "Пароль": self.password_input.text(),
            "Почта": self.mail_input.text() + "@mail.ru",
            "Телефон": "+7" + self.phone_input.text(),
            "Пол": self.sex.currentText(),
            "Роль": self.role.currentText()
        }
        # Запись данных в статическое хранилище
        UserInputDataSave().set_input_data(form_input_data)

        if self.role.currentText() == "Пользователь":
            # Если регистрируется пользователь - Он должен указать степень инвалидности
            self.controller.switch_window(HandicappedLvlInput.HandicappedLvlInputClass)
            return
        # Если роль - Волонтер
        # Необходимо перейти в окно подтверждения почты
        self.controller.switch_window(MailVerificationWindow.MailVerificationClass)
