from PySide6.QtWidgets import (QLabel, QTextEdit, QGroupBox, QCalendarWidget,
                               QTimeEdit,
                               QRadioButton, QFrame, QPushButton, QLineEdit,
                               QVBoxLayout, QWidget, QHBoxLayout, QComboBox)
from PySide6.QtCore import QLocale

from windows.UsersWindows import AcceptRequest, SetInfoAboutItems

from Storage.StaticDataSaver import StaticDataSaver
from tools.AlertMessage import *
from tools.CheckData import is_date_valid

class AddNewRequestData(QFrame):
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

        title = QLabel("Шаг 2")
        title.setObjectName("title_style")
        widget_layout.addWidget(title)

        instruction = QLabel("Введите дополнительные данные")
        instruction.setObjectName("instruction_label")
        widget_layout.addWidget(instruction)

        time_hint = QLabel("Укажите дату и время поездки")
        time_hint.setObjectName("hint_text")
        widget_layout.addWidget(time_hint)

        # Создание элементов для ввода данных
        self.date_input = QCalendarWidget()
        self.date_input.setLocale(QLocale.Language.Russian)
        self.time_input = QTimeEdit()
        self.time_input.setLocale(QLocale.Language.Russian)
        self.time_input.setDisplayFormat("h:m:s")

        widget_layout.addWidget(self.date_input)
        widget_layout.addWidget(self.time_input)

        next_step_btn = QPushButton("Следующий шаг")
        next_step_btn.setObjectName("simple_button")
        next_step_btn.clicked.connect(
            self.next_step_click_listener
        )
        widget_layout.addWidget(next_step_btn)

        back_btn = QPushButton("<- Назад")
        back_btn.setObjectName("hide_btn")
        back_btn.clicked.connect(
            lambda : self.controller.switch_window(AcceptRequest.AcceptNewRequest)
        )
        widget_layout.addWidget(back_btn)

    def next_step_click_listener(self):
        """ Сохранение выбранной даты """
        y, m, d = self.date_input.selectedDate().getDate()



        user_date = f"{y}-{m}-{d}"
        if not is_date_valid(user_date):
            print("no")
            show_critical_alert_simple(self, "Дата не может быть в прошлом!")
            return


        week_day_translate = {
            1:"Понедельник",
            2:"Вторник",
            3:"Среда",
            4:"Четверг",
            5:"Пятница",
            6:"Суббота",
            7:"Воскресенье"
        }
        week_day = week_day_translate[self.date_input.selectedDate().dayOfWeek()]
        print("week_day", week_day)
        user_time = self.time_input.text()
        if (1 < int(user_time.split(":")[0]) <= 5):
            show_critical_alert_simple(self, "Метро не работает с 1:00 до 5:30.\nСервис работает с 6 утра!")
            return

        elif int(user_time.split(":")[1]) + StaticDataSaver().get_route_time() >= 60 and int(user_time.split(":")[0]) == 0:
            show_critical_alert_simple(self, "Поездка должна закончиться до 1:00 по МСК")
            return

        StaticDataSaver().set_req_time(user_time)
        StaticDataSaver().set_req_date(user_date)
        StaticDataSaver().set_req_week_day(week_day)

        # Переход в последнее окно
        self.controller.switch_window(SetInfoAboutItems.AddInfoAboutItems)

