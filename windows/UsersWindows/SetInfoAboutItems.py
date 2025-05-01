import datetime

from PySide6.QtWidgets import (QLabel, QTextEdit, QGroupBox, QCalendarWidget,
                               QTimeEdit,
                               QRadioButton, QFrame, QPushButton, QLineEdit,
                               QVBoxLayout, QWidget, QHBoxLayout, QComboBox)
from PySide6.QtCore import QLocale

from windows.UsersWindows import SetRequestOtherData, MainPage

from tools.MetroGraphLogic import MetroGraph
from Storage.SaveInputUserData import UserInputDataSave
from Storage.StaticDataSaver import StaticDataSaver
from tools.SystemMessages import SystemMessageBox
from tools.AlertMessage import *
from tools.SendMailMessages import send_mail_message
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
        if user_disabled_level == "Вторая":
            workers_count = 2
        elif user_disabled_level == "Третья":
            workers_count = 4

        if is_luggage:
            workers_count += 1

        # Набор сотрудников.
        """ В процессе отбора сотрудников смотрится их занятость и график """
        workers_id_and_mails: list = self.database.take_workers_in_group(workers_count)
        # После добавления сотрудников в группу - им следует изменить занятость и выслать письмо на почту
        workers_id_array: list = workers_id_and_mails[:-1] # В массиве хранятся только id пользователей
        print(workers_id_array, "0000")
        workers_mails_to_mailing: list = workers_id_and_mails[-1] # В массиве хранятся почты для рассылки

        is_group_ready: bool = False
        # Если не нашлось достаточное количество человек
        if len(workers_id_array) < workers_count:
            show_critical_alert_simple(self, "Мы нашли только часть сотрудников! "
                                             "Постараемся дополнить группу в дальнейшем!")
            if len(workers_id_array) == 0:
                workers_id_array.append(0)
        else:
            # Если все люди найдены
            is_group_ready = True

        # Изменение показателя занятости
        if self.database.change_workers_job_status(workers_id_array):

            # После того как я изменил статус работников Необходимо добавить их в группу

            # Получение ID для новой группы
            group_new_id = self.database.take_group_id_for_new_group()
            group_create_data: dict = {
                "id_группы": group_new_id,
                "Количество человек": workers_count,
                "Сотрудники": "{"+f"{','.join(list(map(str, workers_id_array)))}" + "}",
                "Готовность": is_group_ready,
                "Нужность": 'TRUE'
            }

            # Создание группы
            if self.database.create_group(group_create_data):
                # После создания группы -> создается заявка
                # Данные для Заявки
                user_request_data: dict = {
                    "Пользователь FK": StaticDataSaver().get_customer_id(),
                    "Группа FK": group_new_id,
                    "Станция отправки": StaticDataSaver().get_start_station(),
                    "Конечная станция": StaticDataSaver().get_end_station(),
                    "Дата регистрации заявки": datetime.datetime.now(), # Получение времени СЕЙЧАС
                    "Дата_начала": f"{StaticDataSaver().get_req_date()} {StaticDataSaver().get_req_time()}",
                    "Статус заявки": "Не начата",
                    "Маршрут": StaticDataSaver().get_route()
                }
                if self.database.create_request_in_table(user_request_data):
                    SystemMessageBox("Группа создана! Прибудьте в запланированную дату на станцию отправления!\n"
                                     "Иначе ваш рейтинг будет понижен!").send_I_messsage()

                    # После создания заявки - необходимо оповестить сотрудников о работе
                    self.mailing_workers(workers_mails_to_mailing,
                                         workers_id_array,
                                         workers_count)
                    show_alert_simple(self, "Группа для поездки уведомлена!")
                    self.controller.switch_window(MainPage.MainUserPage)
                    return
        # Если произошли проблемы в запросах
        show_critical_alert_simple(self, "Ошибка на сервере!")


    def mailing_workers(self, workers_mail_array: list, workers_id_array: list,
                        workers_count: int, ):
        """ Метод рассылки уведомлений на почты волонтеров """
        print(workers_mail_array)
        print(workers_id_array)
        if -1 in workers_id_array:
            return
        title = "Уведомление о зачислении в группу сопровождения!"
        for data_index in range(len(workers_id_array)):
            # Получение информации о работнике из группы
            information_about_workers: dict = self.database.take_workers_data_by_id(
                worker_current_id=workers_id_array[data_index]
            )
            message = f"""
Добрый день, {information_about_workers['ФИО']}!

Вы были добавлены в группу сопровождения, состоящую из {workers_count} человек.
Поездка состоится в {StaticDataSaver().get_req_week_day()}.

Точная дата - {StaticDataSaver().get_req_date()} {StaticDataSaver().get_req_time()}

Маршрут следования от станции {StaticDataSaver().get_start_station()} до станции {StaticDataSaver().get_end_station()}:

{StaticDataSaver().get_route()}.

Ожидаемое время поездки: {StaticDataSaver().get_route_time()} минут!

Просьба быть на станции отправки в указанное время!
В случае отсутствия на станции - ваш рейтинг будет понижен!

Спасибо за участие!
            """

            send_to = workers_mail_array[data_index]

            # Отправка письма
            send_mail_message(send_to, title, message)



