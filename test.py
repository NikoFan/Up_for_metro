import sys
import json
import requests
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QComboBox, QPushButton, QTextEdit,
                               QLabel, QGroupBox, QRadioButton)
from PySide6.QtCore import Qt


class MetroRoutePlanner(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Московский метро - планировщик маршрутов")
        self.setGeometry(100, 100, 600, 500)

        # Загрузка данных о метро
        self.metro_data = self.load_metro_data()
        print(self.metro_data)

        # Создание интерфейса
        self.init_ui()

    def load_metro_data(self):
        """Загрузка данных о метро из API или локального файла"""
        try:
            with open('moscow_metro.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Минимальные тестовые данные, если нет файла
            return {
                "lines": [
                    {
                        "name": "Сокольническая",
                        "color": "red",
                        "stations": ["Коммунарка", "Ольховая", "Прокшино", "Филатов Луг", "Саларьево", "Румянцево"]
                    },
                    {
                        "name": "Замоскворецкая",
                        "color": "green",
                        "stations": ["Ховрино", "Беломорская", "Речной вокзал", "Водный стадион"]
                    }
                ],
                "transfers": [
                    {"from": "Коммунарка", "to": "Ховрино", "time": 5}
                ]
            }

    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Выбор станций
        station_group = QGroupBox("Выбор станций")
        station_layout = QVBoxLayout()

        # Выбор начальной станции
        start_layout = QHBoxLayout()
        start_layout.addWidget(QLabel("Откуда:"))
        self.start_combo = QComboBox()
        self.populate_station_combo(self.start_combo)
        start_layout.addWidget(self.start_combo)

        # Выбор конечной станции
        end_layout = QHBoxLayout()
        end_layout.addWidget(QLabel("Куда:"))
        self.end_combo = QComboBox()
        self.populate_station_combo(self.end_combo)
        end_layout.addWidget(self.end_combo)

        station_layout.addLayout(start_layout)
        station_layout.addLayout(end_layout)
        station_group.setLayout(station_layout)

        # Критерии поиска
        criteria_group = QGroupBox("Критерии поиска")
        criteria_layout = QVBoxLayout()

        self.time_radio = QRadioButton("Минимальное время")
        self.time_radio.setChecked(True)
        self.transfers_radio = QRadioButton("Минимальное количество пересадок")
        self.stations_radio = QRadioButton("Минимальное количество станций")

        criteria_layout.addWidget(self.time_radio)
        criteria_layout.addWidget(self.transfers_radio)
        criteria_layout.addWidget(self.stations_radio)
        criteria_group.setLayout(criteria_layout)

        # Кнопка построения маршрута
        self.route_button = QPushButton("Построить маршрут")
        self.route_button.clicked.connect(self.calculate_route)

        # Вывод результата
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)

        # Добавление виджетов в основной лейаут
        main_layout.addWidget(station_group)
        main_layout.addWidget(criteria_group)
        main_layout.addWidget(self.route_button)
        main_layout.addWidget(self.result_text)

    def populate_station_combo(self, combo):
        """Заполнение комбобокса станциями"""
        combo.clear()
        stations = []
        for line in self.metro_data["lines"]:
            stations.extend(line["stations"])
        combo.addItems(sorted(stations))

    def calculate_route(self):
        """Расчет маршрута на основе выбранных параметров"""
        start = self.start_combo.currentText()
        end = self.end_combo.currentText()

        if start == end:
            self.result_text.setPlainText("Вы выбрали одну и ту же станцию!")
            return

        # Определяем критерий поиска
        if self.time_radio.isChecked():
            criterion = "time"
        elif self.transfers_radio.isChecked():
            criterion = "transfers"
        else:
            criterion = "stations"

        # Поиск маршрута
        route = self.find_route(start, end, criterion)

        # Вывод результата
        if route:
            self.display_route(route, criterion)
        else:
            self.result_text.setPlainText("Маршрут не найден!")

    def find_route(self, start, end, criterion):
        """Поиск маршрута с учетом критерия"""
        metro_graph = MetroGraph(self.metro_data)
        return metro_graph.find_shortest_path(start, end, criterion)

    def display_route(self, route, criterion):
        """Отображение найденного маршрута"""
        result = f"Маршрут от '{self.start_combo.currentText()}' до '{self.end_combo.currentText()}':\n\n"
        result += " → ".join(route["path"]) + "\n\n"
        result += f"Общее время: {route['time']} минут\n"
        result += f"Пересадок: {route['transfers']}\n"
        result += f"Станций: {route['stations']}\n"

        if criterion == "time":
            result += "\nОптимизировано по времени"
        elif criterion == "transfers":
            result += "\nОптимизировано по количеству пересадок"
        else:
            result += "\nОптимизировано по количеству станций"

        self.result_text.setPlainText(result)


class MetroGraph:
    def __init__(self, metro_data):
        self.graph = {}
        self.metro_data = metro_data
        self.build_graph(metro_data)

    def build_graph(self, metro_data):
        """Построение графа метро из данных"""
        # Сначала создаем все вершины графа
        for line in metro_data["lines"]:
            for station in line["stations"]:
                if station not in self.graph:
                    self.graph[station] = {}

        # Затем добавляем связи между станциями
        for line in metro_data["lines"]:
            stations = line["stations"]
            for i in range(len(stations)):
                station = stations[i]

                # Связь с предыдущей станцией
                if i > 0:
                    prev_station = stations[i - 1]
                    self.graph[station][prev_station] = 2  # 2 минуты между станциями
                    self.graph[prev_station][station] = 2

                # Связь со следующей станцией
                if i < len(stations) - 1:
                    next_station = stations[i + 1]
                    self.graph[station][next_station] = 2
                    self.graph[next_station][station] = 2

        # Добавляем переходы
        for transfer in metro_data.get("transfers", []):
            from_st = transfer["from"]
            to_st = transfer["to"]
            time = transfer.get("time", 5)  # 5 минут на пересадку по умолчанию

            if from_st in self.graph and to_st in self.graph:
                self.graph[from_st][to_st] = time
                self.graph[to_st][from_st] = time

    def find_shortest_path(self, start, end, criterion="time"):
        """Поиск кратчайшего пути с учетом критерия"""
        # Реализация алгоритма Дейкстры
        import heapq

        queue = []
        heapq.heappush(queue, (0, start, []))
        visited = set()

        while queue:
            current_cost, current_node, path = heapq.heappop(queue)

            if current_node in visited:
                continue

            visited.add(current_node)
            new_path = path + [current_node]

            if current_node == end:
                # Расчет характеристик маршрута
                transfers = self.count_transfers(new_path)
                stations = len(new_path) - 1
                time = current_cost

                return {
                    "path": new_path,
                    "time": time,
                    "transfers": transfers,
                    "stations": stations
                }

            for neighbor, weight in self.graph.get(current_node, {}).items():
                if neighbor not in visited:
                    if criterion == "time":
                        new_cost = current_cost + weight
                    elif criterion == "transfers":
                        # Учитываем пересадки как дополнительную стоимость
                        is_transfer = self.is_transfer(current_node, neighbor)
                        new_cost = current_cost + (100 if is_transfer else 1)
                    else:  # stations
                        new_cost = current_cost + 1

                    heapq.heappush(queue, (new_cost, neighbor, new_path))

        return None

    def is_transfer(self, station1, station2):
        """Проверка, является ли связь между станциями пересадкой"""
        # Проверяем, находятся ли станции на разных линиях
        # Это упрощенная проверка - в реальном приложении нужно учитывать фактические переходы
        lines1 = self.get_station_lines(station1)
        lines2 = self.get_station_lines(station2)
        return len(lines1.intersection(lines2)) == 0

    def get_station_lines(self, station):
        """Получение линий, на которых находится станция"""
        lines = set()
        for line in self.metro_data["lines"]:
            if station in line["stations"]:
                lines.add(line["name"])
        return lines

    def count_transfers(self, path):
        """Подсчет количества пересадок в маршруте"""
        if len(path) < 2:
            return 0

        transfers = 0
        prev_lines = self.get_station_lines(path[0])

        for station in path[1:]:
            current_lines = self.get_station_lines(station)
            if not prev_lines.intersection(current_lines):
                transfers += 1
            prev_lines = current_lines

        return transfers



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MetroRoutePlanner()
    window.show()
    sys.exit(app.exec())