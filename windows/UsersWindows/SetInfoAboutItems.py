from PySide6.QtWidgets import (QLabel, QTextEdit, QGroupBox, QCalendarWidget,
                               QTimeEdit,
                               QRadioButton, QFrame, QPushButton, QLineEdit,
                               QVBoxLayout, QWidget, QHBoxLayout, QComboBox)
from PySide6.QtCore import QLocale

from windows.UsersWindows import SetRequestOtherData

from tools.MetroGraphLogic import MetroGraph
from Storage.SaveInputUserData import UserInputDataSave
from Storage.StaticDataSaver import StaticDataSaver
from tools.SystemMessages import SystemMessageBox
from tools.AlertMessage import *
import json


class AddInfoAboutItems(QFrame):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.database = controller.db_connect

        self.frame_layout = QHBoxLayout(self)
        self.setup_ui()

    def setup_ui(self):
        """ Генерация интерфейса """
        widget = QWidget()
        widget.setFixedSize(350, 500)
        widget_layout = QVBoxLayout(widget)
        # Добавление Виджета с формой в центр окна
        self.frame_layout.addWidget(widget)

        title = QLabel("Укажите наличие багажа")
        title.setWordWrap(True)
        title.setObjectName("title_style")
        widget_layout.addWidget(title)
        widget_layout.addStretch()

        instruction = QLabel(
            "Багаж - все, для переноски чего требуется отдельный человек! (Чемодан, Большая коробка, Костыли)")
        instruction.setObjectName("instruction_label")
        instruction.setWordWrap(True)
        widget_layout.addWidget(instruction)

        # Создание элементов для ввода данных
        self.yes_answer = QRadioButton("Да, багаж есть")
        self.no_answer = QRadioButton("Нет, все в руках")

        widget_layout.addWidget(self.yes_answer)
        widget_layout.addWidget(self.no_answer)
        widget_layout.addStretch()

        next_step_btn = QPushButton("Следующий шаг")
        next_step_btn.setObjectName("simple_button")
        next_step_btn.clicked.connect(
            self.next_step_listener
        )
        widget_layout.addWidget(next_step_btn)

        back_btn = QPushButton("<- Назад")
        back_btn.setObjectName("hide_btn")
        back_btn.clicked.connect(
            lambda: self.controller.switch_window(SetRequestOtherData.AddNewRequestData)
        )
        widget_layout.addWidget(back_btn)

    def next_step_listener(self):
        """ Регистрация заявки и создание группы реагирования """
        # Есть ли багаж?
        is_luggage = self.yes_answer.isChecked()

        user_data = self.database.take_user_data_by_id()
        # Сбор данных для создания группы (Пустой)
        # Количество человек зависит от категории инвалидности и наличия багажа
        workers_count = 1
        user_disabled_level = user_data["Категория_инвалидности"]
        if user_disabled_level == "II":
            workers_count = 2
        elif user_disabled_level == "III":
            workers_count = 4

        if is_luggage:
            workers_count += 1

        # Набор сотрудников.
        """ В процессе отбора сотрудников смотрится их занятость и график """
        workers_id: list = self.database.take_workers_in_group(workers_count)
        print(workers_id)
        # После добавления сотрудников в группу - им следует изменить занятость и выслать письмо на почту
        """
        select * from Сотрудник
WHERE id_сотрудника = ANY(ARRAY[1, 3, 5, 7]);"""

        # Сбор данных для заявки