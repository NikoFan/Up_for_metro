import psycopg
from database.config import *

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
        print(user_input_data["Пол"])
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
