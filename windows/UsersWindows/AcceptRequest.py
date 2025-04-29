from PySide6.QtWidgets import (QLabel, QTextEdit, QGroupBox,
                               QRadioButton, QFrame, QPushButton, QLineEdit,
                               QVBoxLayout, QWidget, QHBoxLayout, QComboBox)

from windows.UsersWindows import CreateRequest, SetRequestOtherData

from tools.MetroGraphLogic import MetroGraph
from Storage.SaveInputUserData import UserInputDataSave
from Storage.StaticDataSaver import StaticDataSaver
from tools.SystemMessages import SystemMessageBox
from tools.AlertMessage import *
import json


class AcceptNewRequest(QFrame):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.database = controller.db_connect

        self.start = StaticDataSaver().get_start_station()
        self.end = StaticDataSaver().get_end_station()
        self.criterion = StaticDataSaver().get_req_type()

        # Создание Дата Сета
        self.metro_data = self.load_metro_data()

        self.frame_layout = QHBoxLayout(self)
        self.setup_ui()

        self.calculate_route()

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

        title = QLabel("Одобрение заявки\nШаг 1")
        title.setObjectName("title_style")
        widget_layout.addWidget(title)
        widget_layout.addStretch()

        self.route = QLabel()
        self.route.setWordWrap(True)
        self.route.setObjectName("account_normal_text")
        widget_layout.addWidget(self.route)

        self.result_text = QTextEdit()
        widget_layout.addWidget(self.result_text)

        self.time_result = QLabel()
        self.time_result.setWordWrap(True)
        self.time_result.setObjectName("account_normal_text")
        widget_layout.addWidget(self.time_result)

        self.transfer = QLabel()
        self.transfer.setWordWrap(True)
        self.transfer.setObjectName("account_normal_text")
        widget_layout.addWidget(self.transfer)

        self.stations_count = QLabel()
        self.stations_count.setWordWrap(True)
        self.stations_count.setObjectName("account_normal_text")
        widget_layout.addWidget(self.stations_count)

        self.info = QLabel()
        self.info.setWordWrap(True)
        self.info.setObjectName("account_normal_text")
        widget_layout.addWidget(self.info)

        # Кнопка далее
        next_step_btn = QPushButton("Следующий шаг")
        next_step_btn.setObjectName("simple_button")
        next_step_btn.clicked.connect(
            self.open_next_step
        )
        widget_layout.addWidget(next_step_btn)

        # Кнопка назад
        back_btn = QPushButton("Вернуться к заявке")
        back_btn.setObjectName("hide_btn")
        back_btn.clicked.connect(
            lambda: self.controller.switch_window(CreateRequest.CreateRequestClass)
        )
        widget_layout.addWidget(back_btn)


    def calculate_route(self):
        """ Расчет маршрута на основе выбранных параметров """
        # Поиск маршрута
        route = self.find_route(self.start,
                                self.end,
                                self.criterion)
        # Вывод результата
        if route:
            self.display_route(route,
                               self.criterion)
        else:
            self.result_text.setPlainText("Маршрут не найден!")

    def find_route(self, start, end, criterion):
        """ Поиск маршрута с учетом критерия """
        metro_graph = MetroGraph(self.metro_data)
        return metro_graph.find_shortest_path(start, end, criterion)

    def display_route(self, route, criterion):
        """Отображение найденного маршрута"""
        self.route.setText(f"Маршрут от '{self.start}' до '{self.end}':")
        self.result_text.setPlainText(" → ".join(route["path"]))
        self.time_result.setText(f"Общее время: {route['time']} минут")
        self.transfer.setText(f"Пересадок: {route['transfers']}")
        self.stations_count.setText(f"Станций: {route['stations']}")

        if criterion == "time":
            self.info.setText("Оптимизировано по времени")
        elif criterion == "transfers":
            self.info.setText("Оптимизировано по количеству пересадок")
        else:
            self.info.setText("Оптимизировано по количеству станций")


    def open_next_step(self):
        """ Метод перехода в следующий шаг + сохранение данных """
        print(self.result_text.toPlainText())
        StaticDataSaver().set_route(self.result_text.toPlainText())
        StaticDataSaver().set_route_time(int(self.time_result.text().split(" ")[2]))
        self.controller.switch_window(SetRequestOtherData.AddNewRequestData)
