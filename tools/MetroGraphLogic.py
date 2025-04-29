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
