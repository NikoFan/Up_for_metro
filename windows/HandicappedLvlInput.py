from PySide6.QtWidgets import (QLabel, QFrame, QPushButton, QLineEdit,
                               QVBoxLayout, QWidget, QHBoxLayout, QComboBox)

from windows import RegistrationWindow
from Storage.SaveInputUserData import UserInputDataSave
from tools.SystemMessages import SystemMessageBox

class HandicappedLvlInputClass(QFrame):
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
        title = QLabel("Укажите степень инвалидности")
        title.setWordWrap(True)
        title.setObjectName("title_style")
        widget_layout.addWidget(title)
        widget_layout.addStretch()

        instruction = QLabel("В дальнейшем предстоит подтвердить вашу степень, направив требуемые документы нам. "
                             "Просьба не указывать недостоверные данные")
        instruction.setWordWrap(True)
        instruction.setObjectName("instruction_label")
        widget_layout.addWidget(instruction)

        # Создание горизонтальной разметки
        levels_hbox = QHBoxLayout()
        first_level = QPushButton("I", objectName="level_choose")
        first_level.clicked.connect(
            lambda : self.add_data("Первая")
        )
        second_level = QPushButton("II", objectName="level_choose")
        second_level.clicked.connect(
            lambda : self.add_data("Вторая")
        )
        third_level = QPushButton("III", objectName="level_choose")
        third_level.clicked.connect(
            lambda : self.add_data("Третья")
        )

        # Размещение кнопок
        levels_hbox.addWidget(first_level)
        levels_hbox.addWidget(second_level)
        levels_hbox.addWidget(third_level)

        # Добавление кнопок на окно
        widget_layout.addLayout(levels_hbox)
        widget_layout.addStretch()

        back_btn = QPushButton("<- Назад")
        back_btn.setObjectName("hide_btn")
        back_btn.clicked.connect(
            lambda : self.controller.switch_window(RegistrationWindow.RegistrationWindowClass)
        )

        widget_layout.addWidget(back_btn)

    def add_data(self, level: str) -> None:
        """
        Отправка данных на регистрацию аккаунта пользователя
        :param level: Степень инвалидности
        :return: None
        """
        self.old_form_data["Степень инвалидности"] = level

        if SystemMessageBox("Вы точно хотите создать аккаунт?").send_W_messsage():
            if self.database.create_user_account(self.old_form_data):
                SystemMessageBox("Аккаунт создан!").send_I_messsage()
                return
            SystemMessageBox("Ошибка создания аккаунта!").send_C_messsage()






