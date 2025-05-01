import psycopg

from datetime import datetime

from Storage.StaticDataSaver import StaticDataSaver
from database.config import *
from tools.SQLI_inspector import *

from tools import (SQLI_inspector, CheckData,
                   SystemMessages, SendMailMessages)


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

    def take_workers_data_by_id(self, worker_current_id: int = None) -> dict:
        """ Метод получения данных о Сотруднике по ID """

        if worker_current_id == None:
            worker_current_id = StaticDataSaver().get_customer_id()

        query = f"""
        SELECT *
        FROM Сотрудник
        WHERE id_сотрудника = {worker_current_id};
        """

        cursor = self.connection.cursor()
        cursor.execute(query)
        workers_data_storage: dict = dict()
        for worker_data_row in cursor.fetchall():
            workers_data_storage = {
                "id": worker_data_row[0],
                "Логин": worker_data_row[1],
                "Пароль": worker_data_row[2],
                "ФИО": worker_data_row[3],
                "Телефон": worker_data_row[4],
                "Почта": worker_data_row[5],
                "Пол": worker_data_row[6],
                "расписание_fk": worker_data_row[7],
                "Занятость": worker_data_row[8]
            }
        cursor.close()

        return workers_data_storage

    def account_authorization(self, customer_login, customer_password) -> bool:
        """ Метод авторизации аккаунта по Логину и Паролю """

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

    def change_workers_job_status(self, workers_id_arr: list) -> bool:
        """ Метод изменения статуса занятости сотрудника """
        try:
            if -1 in workers_id_arr:
                return False
            print(workers_id_arr)
            query = f"""
            UPDATE Сотрудник
            SET Занятость = TRUE
            WHERE id_сотрудника = ANY(ARRAY{workers_id_arr});
            """

            print(query)

            cursor = self.connection.cursor()
            cursor.execute(query)
            self.connection.commit()
            cursor.close()
            return True
        except Exception as error:
            print(f"change_workers_job_status() ERR: {error}")
            return False

    def create_group(self, group_data: dict) -> bool:
        """ Метод создания группы """

        try:
            query = f"""
            INSERT INTO Группа_реагирования(id_группы, Количество_человек, Сотрудники, Готовность,
            Нужность)
            VALUES(
            {group_data['id_группы']},
            {group_data['Количество человек']},
            '{group_data['Сотрудники']}',
            {group_data['Готовность']},
            {group_data['Нужность']}
            );
            """

            cursor = self.connection.cursor()
            cursor.execute(query)
            self.connection.commit()
            cursor.close()

            # После удачного создания группы - записывается ID этой группы
            StaticDataSaver().set_new_group_id(group_data['id_группы'])

            return True
        except Exception as error:
            print(f"create_group() ERR: {error}")
            return False

    def take_group_id_for_new_group(self) -> int:
        """ Метод получения id для новой группы """
        query = """
        SELECT id_группы
        FROM Группа_реагирования;"""
        cursor = self.connection.cursor()
        cursor.execute(query)

        result_id: int = 0

        # Прочитывание всех данных
        for g_id in cursor.fetchall():
            result_id = g_id[0]

        return result_id + 1

    def create_request_in_table(self, req_data: dict) -> bool:
        """ Метод создания заявки для пользователя """
        try:
            query = f"""
            INSERT INTO Заявки(
                пользователь_fk,
                группа_сотрудников_fk,
                Начальная_станция,
                Конечная_станция,
                Дата_создания,
                Дата_начала,
                Статус_заявки,
                Маршрут)
            VALUES(
            {req_data['Пользователь FK']},
            {req_data['Группа FK']},
            '{req_data['Станция отправки']}',
            '{req_data['Конечная станция']}',
            '{req_data['Дата регистрации заявки']}',
            '{req_data['Дата_начала']}',
            '{req_data['Статус заявки']}',
            '{req_data['Маршрут']}'
            );
            """
            cursor = self.connection.cursor()
            cursor.execute(query)
            self.connection.commit()
            cursor.close()

            return True
        except Exception as error:
            print(f"create_request_in_table() ERR: {error}")
            return False

    def take_user_active_request_by_id(self) -> dict:
        """ Метод получения активной заявки пользователя по ID """
        user_current_id: int = StaticDataSaver().get_customer_id()
        query = f"""
        SELECT группа_сотрудников_fk, Начальная_станция, Конечная_станция,
                Дата_начала, Статус_заявки, id_заявки
        FROM Заявки
        WHERE пользователь_fk = {user_current_id}
            AND
            Статус_заявки != 'Завершена'
            AND
            Статус_заявки != 'Отменена';
        """

        request_data: dict = dict()

        cursor = self.connection.cursor()
        cursor.execute(query)
        for req_data in cursor.fetchall():
            request_data = {
                "Группа": req_data[0],
                "Начало": req_data[1],
                "Конец": req_data[2],
                "Дата": req_data[3],
                "Статус": req_data[4],
                "id": req_data[5]
            }
        cursor.close()

        return request_data

    def cancel_active_req_in_table(self, new_req_status: str, request_id_number: int, comment_text: str = None) -> bool:
        """
        Метод отмены / завершения поездки
        :param new_req_status: Передается новый статус - Завершена или Отменена
        :param request_id_number: Номер заявки, с которой ведется работа
        :param comment_text: Текст комментария от сотрудника при завершении поездки
        :return: bool
        """

        try:
            end_date = f"'{datetime.now()}'"
            avg_date = "NULL"
            if new_req_status == "Завершена":
                avg_date = (f"""(select ('{datetime.now()}' - Дата_начала)
                            from Заявки
                            WHERE id_заявки = {request_id_number}),
                            
                            Комментарий_группы = '{comment_text}'
                            """)


                print(avg_date)
            query = f"""
            UPDATE Заявки
            SET Статус_заявки = '{new_req_status}',
            Дата_окончания = {end_date},
            Общее_время = {avg_date}
            WHERE id_заявки = {request_id_number};
            """

            print(query)

            cursor = self.connection.cursor()
            cursor.execute(query)
            self.connection.commit()
            cursor.close()

            take_group_id_query = f"""
            SELECT группа_сотрудников_fk
            FROM Заявки
            WHERE id_заявки = {request_id_number};
            """
            cursor = self.connection.cursor()
            cursor.execute(take_group_id_query)
            group_id = cursor.fetchone()
            cursor.close()

            # Изменение статуса нужности группы на отрицательный (Группа больше не нужна)
            group_status_update_query = f"""
            UPDATE Группа_реагирования
            SET Нужность = FALSE
            WHERE id_группы = {group_id[0]};
            """

            cursor = self.connection.cursor()
            cursor.execute(group_status_update_query)
            self.connection.commit()
            cursor.close()

            # После того как изменился статус Заявки -> Меняется занятость у сотрудников
            # Получение списка сотрудников
            second_query = f"""
            SELECT Группа_реагирования.Сотрудники
            FROM Заявки
            JOIN Группа_реагирования ON Заявки.группа_сотрудников_fk = Группа_реагирования.id_группы
            WHERE Заявки.id_заявки = {request_id_number};
            """

            cursor = self.connection.cursor()
            cursor.execute(second_query)
            workers_array = cursor.fetchone()
            print(workers_array[0])
            cursor.close()

            # Также необходимо уведомить сотрудников об отмене поездки
            take_workers_mails_query = f"""
            select Почта
            from Сотрудник
            WHERE id_сотрудника = ANY(ARRAY[{workers_array[0]}]);
            """

            cursor = self.connection.cursor()
            cursor.execute(take_workers_mails_query)

            for mail_address in cursor.fetchall():
                # Формирование письма
                title = "Уведомление об отмене поездки"
                send_to = mail_address[0]
                message = ("Добрый день!\nЗапланированная поездка отменилась! "
                           "Ожидайте следующего письма с приглашением!\n\n"
                           "Спасибо за отклик!")

                SendMailMessages.send_mail_message(send_to, title, message)

            cursor.close()

            # После уведомления - Изменить Занятость у сотрудников
            change_worker_status_query = f"""
            UPDATE Сотрудник
            SET Занятость = FALSE
            WHERE id_сотрудника = ANY(ARRAY[{workers_array[0]}]);
            """

            cursor = self.connection.cursor()
            cursor.execute(change_worker_status_query)
            self.connection.commit()
            cursor.close()

            # После проведенных действий - Сохранить id заявки в Историю
            insert_history_query = f"""
            INSERT INTO История (Заявка_fk)
            VALUES({request_id_number});
            """
            cursor = self.connection.cursor()
            cursor.execute(insert_history_query)
            self.connection.commit()
            cursor.close()

            return True
        except Exception as error:
            print(f"cancel_active_req_in_table() ERR: {error}")
            return False

    def take_requests_from_history(self) -> list:
        """ Метод получения записей из истории """

        user_id_number: int = StaticDataSaver().get_customer_id()

        query = f"""
        select з.Начальная_станция, з.Конечная_станция, з.Дата_окончания, з.Комментарий_пользователя,
        з.id_заявки
        from История и
        join Заявки з
        on и.Заявка_fk = з.id_заявки
        where з.пользователь_fk = {user_id_number}
        """

        cursor = self.connection.cursor()
        cursor.execute(query)

        result_arr: list = list()

        for data in cursor.fetchall():
            result_arr.append(
                {
                    "Start": data[0],
                    "End": data[1],
                    "Last": data[2],
                    "Comment": data[3],
                    "Req_Id": data[4]
                }
            )

        return result_arr

    def update_request_comment(self, comment_message: str, req_active_id: int):
        """ Метод обновления комментария в таблице заявки """
        try:
            query = f"""
            UPDATE Заявки
            SET Комментарий_пользователя = {comment_message}
            WHERE id_заявки = {req_active_id};
            """

            cursor = self.connection.cursor()
            cursor.execute(query)

            self.connection.commit()
            cursor.close()

            return True
        except Exception as error:
            print(f"update_request_comment() ERR: {error}")
            return False

    def take_active_request_information_for_worker(self) -> dict:
        """ Метод получения активной заявки для сотрудника """
        try:
            # Получение ID Группы, в которой состоит сотрудник
            worker_id_number: int = StaticDataSaver().get_customer_id()
            take_group_id_number_query = f"""
            select id_группы
            from Группа_реагирования
            where Нужность = TRUE
            AND {worker_id_number} = ANY(Сотрудники);
            """

            cursor = self.connection.cursor()
            cursor.execute(take_group_id_number_query)

            group_id_number = cursor.fetchone()[0]

            cursor.close()

            if group_id_number == None:
                return dict()

            # Получение данных из записи
            take_req_data_query = f"""
            select id_заявки, Начальная_станция, Конечная_станция, Дата_начала, Маршрут, Статус_заявки
            from Заявки
            where группа_сотрудников_fk = {group_id_number}
                AND
                Статус_заявки != 'Завершена'
                AND
                Статус_заявки != 'Отменена';
            """

            cursor = self.connection.cursor()
            cursor.execute(take_req_data_query)

            req_data: dict = dict()
            for execute_answer in cursor.fetchall():
                req_data = {
                    "id": execute_answer[0],
                    "Начальная_станция": execute_answer[1],
                    "Конечная_станция": execute_answer[2],
                    "Дата_начала": execute_answer[3],
                    "Маршрут": execute_answer[4],
                    "Статус_заявки": execute_answer[5]

                }

            return req_data
        except Exception as error:
            print(f"take_active_request_information_for_worker() ERR: {error}")
            return dict()

    def start_request_action(self, req_id: int):
        """ Метод изменения статуса заявки на В процессе """

        try:
            query = f"""
            UPDATE Заявки
            SET Статус_заявки = 'В процессе'
            WHERE id_заявки = {req_id};
            """

            cursor = self.connection.cursor()
            cursor.execute(query)
            self.connection.commit()
            cursor.close()
            return True
        except Exception as error:
            print(f"start_request_action() ERR: {error}")
            return False
