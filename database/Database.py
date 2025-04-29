import psycopg

from Storage.StaticDataSaver import StaticDataSaver
from database.config import *
from tools.SQLI_inspector import *

from tools import (SQLI_inspector, CheckData,
                   SystemMessages)


class DatabaseConnection:
    def __init__(self):
        self.connection = self.connect_to_database()

    def connect_to_database(self) -> psycopg.connect:
        """ Метод установки подключения к базе данных на локальном сервере """
        try:
            connection = psycopg.connect(
                host=host_name,
                user=user_name,
                dbname=database_name,
                password=password_data,
                port=port_number
            )
            return connection
        except Exception as error:
            print(f"connect_to_database() ERR: {error}")
            return None

    def create_user_account(self, user_input_data) -> bool:
        """
        Метод создания аккаунта пользователя
        :param user_input_data: данные для создания аккаунта
        :return: bool
        """
        try:
            # Проверка на SQLI
            if not SQLI_inspector.dict_inspector(user_input_data):
                SystemMessages.SystemMessageBox(
                    "Ошибка в введенных значениях! Уберите все символы из списка:\n ' ; -").send_C_messsage()
                return False

            # Проверка корректности данных
            check_event = CheckData.rout(user_input_data)
            if not check_event[0]:  # Если результат проверки отрицательный
                SystemMessages.SystemMessageBox(check_event[1]).send_C_messsage()
                return False
            query = f"""
            INSERT INTO Пользователи(Логин, Пароль, ФИО, Телефон, Пол, Категория_инвалидности, Почта)
            VALUES ('{user_input_data["Логин"]}',
                    '{user_input_data["Пароль"]}',
                    '{user_input_data["ФИО"]}',
                    '{user_input_data["Телефон"]}',
                    '{user_input_data["Пол"]}',
                    '{user_input_data["Степень инвалидности"]}',
                    '{user_input_data["Почта"]}');
            """

            cursor = self.connection.cursor()
            cursor.execute(query)
            self.connection.commit()

            return True
        except IndexError as error:
            print(f"create_user_account() ERR: {error}")
            return False

    def create_worker_account(self, worker_input_data) -> bool:
        """
        Метод создания аккаунта волонтера
        :param worker_input_data: данные для создания аккаунта
        :return: bool
        """
        try:
            # Проверка на SQLI
            if not SQLI_inspector.dict_inspector(worker_input_data):
                SystemMessages.SystemMessageBox(
                    "Ошибка в введенных значениях! Уберите все символы из списка:\n ' ; -").send_C_messsage()
                return False

            # Проверка корректности данных
            check_event = CheckData.rout(worker_input_data)
            if not check_event[0]:  # Если результат проверки отрицательный
                SystemMessages.SystemMessageBox(check_event[1]).send_C_messsage()
                return False
            query = f"""
            INSERT INTO Сотрудник(Логин, Пароль, ФИО, Телефон, Почта, Пол, расписание_fk, Занятость)
            VALUES ('{worker_input_data["Логин"]}',
                    '{worker_input_data["Пароль"]}',
                    '{worker_input_data["ФИО"]}',
                    '{worker_input_data["Телефон"]}',
                    '{worker_input_data["Почта"]}',
                    '{worker_input_data["Пол"]}',
                    {worker_input_data["График работы"]},
                    FALSE);
            """

            cursor = self.connection.cursor()
            cursor.execute(query)
            self.connection.commit()

            return True
        except IndexError as error:
            print(f"create_worker_account() ERR: {error}")
            return False

    def take_all_work_plans_from_table(self) -> list:
        """ Метод получения списков всех графиков работы для волонтера """
        query = "SELECT * FROM График_работы;"
        cursor = self.connection.cursor()
        cursor.execute(query)

        work_plans = []
        plan_and_id: dict = dict()
        for execute_row in cursor.fetchall():
            # Добавление расписания в основной список
            work_plans.append(execute_row[-1])
            plan_and_id[execute_row[-1]] = execute_row[0]
        work_plans.append(plan_and_id)
        # Результатом работы метода является
        # ["Пн|Вт", "Ср|Пт", {"Пн|Вт":1, "Ср|Пт":2}]
        return work_plans

    def take_user_accounts_data(self) -> list:
        """ Получение данных об аккаунтах пользователей и сотрудников
            для проверки дубликатов """
        query_users = "SELECT Логин FROM Пользователи;"
        result_array = []
        cursor = self.connection.cursor()
        cursor.execute(query_users)
        for execute_row in cursor.fetchall():
            result_array.append(execute_row[0])  # Логин

        cursor.close()

        query_users = "SELECT Логин FROM Сотрудник;"
        cursor = self.connection.cursor()
        cursor.execute(query_users)
        for execute_row in cursor.fetchall():
            result_array.append(execute_row[0])  # Логин
        cursor.close()

        # Результатом идет список аккаунтов с паролями, для проверки отсутствия дубликатов
        return result_array

    def take_customer_id(self, customer_login: str, customer_password: str, customer_role: str) -> int:
        """
        Метод получения ID пользователя/сотрудника, для дальнейшей работы
        :param customer_login: Логин, на который будет получен ID
        :param customer_password: Пароль, для которого будет получен ID
        :param customer_role: Роль пользователя, для создания запроса
        :return: int значение id
        """
        try:
            if customer_role == "Пользователь":
                query = f"""
                SELECT id_пользователя
                FROM Пользователи
                WHERE Логин = '{customer_login}'
                    AND
                Пароль = '{customer_password}';"""
            else:
                query = f"""
                SELECT id_сотрудника
                FROM Сотрудник
                WHERE Логин = '{customer_login}'
                    AND
                Пароль = '{customer_password}';"""

            cursor = self.connection.cursor()
            cursor.execute(query)

            # Считывание результата работы запроса
            customer_id = cursor.fetchone()

            # Проверка, что для такого пользователя есть ID
            print(customer_id)
            if customer_id[0] == None:
                return -1
            return customer_id[0]

        except Exception as error:
            print(f"take_customer_id() ERR: {error}")
            return -1

    def take_user_data_by_id(self) -> dict:
        """ Метод получения данных о пользователе по ID """
        # Получение id пользователя
        user_current_id = StaticDataSaver().get_customer_id()

        query = f"""
        SELECT *
        FROM Пользователи
        WHERE id_пользователя = {user_current_id};
        """

        cursor = self.connection.cursor()
        cursor.execute(query)
        user_data_storage: dict = dict()
        for user_data_row in cursor.fetchall():
            user_data_storage = {
                "id": user_data_row[0],
                "Логин": user_data_row[1],
                "Пароль": user_data_row[2],
                "ФИО": user_data_row[3],
                "Телефон": user_data_row[4],
                "Пол": user_data_row[5],
                "Категория_инвалидности": user_data_row[6],
                "Почта": user_data_row[7]
            }
        cursor.close()

        return user_data_storage

    def account_authorization(self, customer_login, customer_password) -> bool:
        """ Метод авторизации аккаунта по Логину и Паролю """
        return_array: dict = dict()

        if not word_inspector(customer_login) or not word_inspector(customer_password):
            return False

        query = f"""
        SELECT id_пользователя
        FROM Пользователи
        WHERE Логин = '{customer_login}'
            AND
        Пароль = '{customer_password}';"""

        cursor = self.connection.cursor()
        cursor.execute(query)

        result = cursor.fetchone()
        cursor.close()
        if result != None:
            print(result, "Пользователь")
            StaticDataSaver().set_customer_id(result[0])
            StaticDataSaver().set_role("Пользователь")
            return True

        query = f"""
                SELECT id_сотрудника
                FROM Сотрудник
                WHERE Логин = '{customer_login}'
                    AND
                Пароль = '{customer_password}';"""

        cursor = self.connection.cursor()
        cursor.execute(query)

        result = cursor.fetchone()
        cursor.close()

        if result != None:
            print(result, "Сотрудник")
            StaticDataSaver().set_customer_id(result[0])
            StaticDataSaver().set_role("Волонтер")
            return True

        return False

    def take_workers_in_group(self, group_people_count: int) -> list:
        """ Получение списка сотрудников для группы """

        week_day = StaticDataSaver().get_req_week_day()
        query = f"""
        SELECT с.id_сотрудника, с.Почта
        FROM Сотрудник с
        JOIN График_работы г ON с.расписание_fk = г.id_расписания
        WHERE г.дни_недели LIKE '%{week_day}%'
        AND с.Занятость = FALSE
        limit {group_people_count};
        """

        cursor = self.connection.cursor()
        cursor.execute(query)

        result = []
        buffer = []
        for worker_id in cursor.fetchall():
            result.append(worker_id[0])
            buffer.append(worker_id[1])
        result.append(buffer)
        cursor.close()
        return result

