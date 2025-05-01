import random


class StaticDataSaver:
    """ Класс для хранения промежуточных значений """

    __verification_code: int = None
    __active_role: str = None
    __customer_id: int = None

    # данные для заявки
    __start_station: str = None
    __end_station: str = None
    __type_of_request: str = None

    __user_route: str = None
    __route_time: int = None
    __req_time: str = None
    __req_date: str = None
    __week_day: str = None

    # Группы
    __group_current_id: int = None

    @staticmethod
    def get_code() -> int: return StaticDataSaver.__verification_code

    @staticmethod
    def generate_code():
        """ Метод генерации кода ХХХХХХ """
        code: str = ""
        for _ in range(6):
            code += str(random.randint(0, 9))

        StaticDataSaver.__verification_code = int(code)

    @staticmethod
    def set_role(role_name: str):
        """ Метод установки роли, для дальнейшего разграничения прав """
        StaticDataSaver.__active_role = role_name

    @staticmethod
    def get_role() -> str: return StaticDataSaver.__active_role

    @staticmethod
    def set_customer_id(id_number: int):
        """ Метод записи активного id пользователя программы (Пользователь/сотрудник)"""
        StaticDataSaver.__customer_id = id_number

    @staticmethod
    def get_customer_id() -> int: return StaticDataSaver.__customer_id

    @staticmethod
    def set_start_station(station_name: str):
        """ Метод установки станции отправления """
        StaticDataSaver.__start_station = station_name

    @staticmethod
    def set_end_station(station_name: str):
        """ Метод установки последней станции """
        StaticDataSaver.__end_station = station_name

    @staticmethod
    def get_start_station() -> str: return StaticDataSaver.__start_station

    @staticmethod
    def get_end_station() -> str: return StaticDataSaver.__end_station

    @staticmethod
    def set_type_of_request(req_type: str):
        """ Метод критерия построения маршрута (на что делать упор) типа создаваемой заявки """
        StaticDataSaver.__type_of_request = req_type

    @staticmethod
    def get_req_type() -> str: return StaticDataSaver.__type_of_request


    @staticmethod
    def set_route(route_data: str):
        """ Метод записи маршрута от станции к станции """
        StaticDataSaver.__user_route = route_data

    @staticmethod
    def get_route() -> str: return StaticDataSaver.__user_route

    @staticmethod
    def set_route_time(time: int):
        """ Метод записи среднего времени для маршрута """
        StaticDataSaver.__route_time = time

    @staticmethod
    def get_route_time() -> int: return StaticDataSaver.__route_time


    @staticmethod
    def set_req_time(time: str):
        """ Метод установки запланированного времени """
        StaticDataSaver.__req_time = time

    @staticmethod
    def set_req_date(date: str):
        """ Метод установки даты для дальнейшего считывания и записи"""
        StaticDataSaver.__req_date = date

    @staticmethod
    def get_req_time() -> str: return StaticDataSaver.__req_time

    @staticmethod
    def get_req_date() -> str: return StaticDataSaver.__req_date

    @staticmethod
    def set_req_week_day(day_name: str):
        """ Метод установки дня недели, на который планируется поездка """
        StaticDataSaver.__week_day = day_name

    @staticmethod
    def get_req_week_day() -> str: return StaticDataSaver.__week_day


    @staticmethod
    def set_new_group_id(new_id: int):
        """ Метод записи id для обрабатываемой группы """
        StaticDataSaver.__group_current_id = new_id

    @staticmethod
    def get__new_group_id() -> int: return StaticDataSaver.__group_current_id

