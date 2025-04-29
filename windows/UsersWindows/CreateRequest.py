from PySide6.QtWidgets import (QLabel, QTextEdit, QGroupBox,
                               QRadioButton, QFrame, QPushButton, QLineEdit,
                               QVBoxLayout, QWidget, QHBoxLayout, QComboBox)

from windows.UsersWindows import MainPage

from windows.UsersWindows.AcceptRequest import AcceptNewRequest
from Storage.StaticDataSaver import StaticDataSaver
from tools.SystemMessages import SystemMessageBox
from tools.AlertMessage import *
import json


class CreateRequestClass(QFrame):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.database = controller.db_connect

        # Создание Дата Сета
        self.metro_data = self.load_metro_data()

        self.frame_layout = QHBoxLayout(self)
        self.setup_ui()

    def load_metro_data(self):
        """ Загрузка данных из JSON """
        try:
            # Считывание данных из json
            with open('moscow_metro.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            SystemMessageBox("Ошибка на сервере! Попробуйте позже!")
            # Минимальные тестовые данные, если нет файла
            return {}

    def populate_station_combo(self, combo):
        """ Заполнение комбобокса станциями """
        combo.clear()
        stations = []
        for line in self.metro_data["lines"]:
            stations.extend(line["stations"])
        combo.addItems(sorted(stations))

    def setup_ui(self):
        """ Генерация интерфейса """
        widget = QWidget()
        widget.setFixedSize(350, 500)
        widget_layout = QVBoxLayout(widget)
        # Добавление Виджета с формой в центр окна
        self.frame_layout.addWidget(widget)

        title = QLabel("Создание заявки")
        title.setObjectName("title_style")
        widget_layout.addWidget(title)

        instruction = QLabel("Создайте заявку для поездки!")
        instruction.setObjectName("instruction_label")
        widget_layout.addWidget(instruction)

        widget_layout.addStretch()

        # Создание логики окна
        block_title = QLabel("Выбор станций")
        block_title.setObjectName("small_title_style")

        # Разметка для элементов "Откуда" и выпадающий список
        from_hbox = QHBoxLayout()
        from_label = QLabel("Откуда:")
        from_label.setObjectName("small_text")
        from_hbox.addWidget(from_label)

        self.stations_from = QComboBox()
        self.populate_station_combo(self.stations_from)
        from_hbox.addWidget(self.stations_from)

        # Разметка для элементов "Куда" и выпадающего списка
        to_hbox = QHBoxLayout()
        to_label = QLabel("Куда:")
        to_label.setObjectName("small_text")
        to_hbox.addWidget(to_label)

        self.stations_to = QComboBox()
        self.populate_station_combo(self.stations_to)
        to_hbox.addWidget(self.stations_to)

        widget_layout.addWidget(block_title)
        widget_layout.addLayout(from_hbox)
        widget_layout.addLayout(to_hbox)

        # Критерии поиска
        criteria_group = QGroupBox("Критерии поиска")
        criteria_layout = QVBoxLayout()
        # Блок для генерации маршрута
        self.time_radio = QRadioButton("Минимум времени")

        self.time_radio.setChecked(True)
        self.transfers_radio = QRadioButton("Минимум пересадок")
        self.stations_radio = QRadioButton("Минимум станций")

        criteria_layout.addWidget(self.time_radio)
        criteria_layout.addWidget(self.transfers_radio)
        criteria_layout.addWidget(self.stations_radio)
        criteria_group.setLayout(criteria_layout)

        # Кнопка построения маршрута
        self.route_button = QPushButton("Построить маршрут")
        self.route_button.setObjectName("simple_button")
        self.route_button.clicked.connect(self.open_accept_window)

        back_btn = QPushButton("На главную")
        back_btn.setObjectName("hide_btn")
        back_btn.clicked.connect(
            lambda: self.controller.switch_window(
                MainPage.MainUserPage
            )
        )

        widget_layout.addWidget(criteria_group)
        widget_layout.addWidget(self.route_button)
        widget_layout.addWidget(back_btn)

    def open_accept_window(self):
        """ Метод перехода в окно одобрения заявки """
        if self.stations_from.currentText() == self.stations_to.currentText():
            show_critical_alert_simple(self, "Вы выбрали одинаковые станции!")
            return
        StaticDataSaver().set_start_station(self.stations_from.currentText())
        StaticDataSaver().set_end_station(self.stations_to.currentText())

        # Определение критерия поиска
        if self.time_radio.isChecked():
            criterion = "time"
        elif self.transfers_radio.isChecked():
            criterion = "transfers"
        else:
            criterion = "stations"

        # Установка типа создаваемой заявки
        StaticDataSaver().set_type_of_request(criterion)

        self.controller.switch_window(AcceptNewRequest)
