from PySide6.QtWidgets import (QLabel, QFrame, QPushButton, QLineEdit,
                               QVBoxLayout, QWidget, QHBoxLayout, QComboBox)

from windows import RegistrationWindow
from Storage.SaveInputUserData import UserInputDataSave
from Storage.StaticDataSaver import StaticDataSaver
from tools.SystemMessages import SystemMessageBox
from tools.AlertMessage import *
from windows.WorkersWindows.WorkerMainPage import MainWorkerPage


class SelectWorkPlanClass(QFrame):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.database = controller.db_connect
        self.old_form_data = UserInputDataSave().get_data()
        self.frame_layout = QHBoxLayout(self)
        self.setup_ui()

    def setup_ui(self):
        """ Генерация интерфейса """
        widget = QWidget()
        widget.setFixedSize(350, 500)
        widget_layout = QVBoxLayout(widget)
        # Добавление Виджета с формой в центр окна
        self.frame_layout.addWidget(widget)

        # Создание интерфейса формы
        title = QLabel("Выберите график работы")
        title.setWordWrap(True)
        title.setObjectName("title_style")
        widget_layout.addWidget(title)
        widget_layout.addStretch()

        instruction = QLabel("В дальнейшем будет доступна функция изменения графика")
        instruction.setWordWrap(True)
        instruction.setObjectName("instruction_label")
        widget_layout.addWidget(instruction)

        # Список графиков
        self.plans = QComboBox()
        self.plans_list: list = self.database.take_all_work_plans_from_table()
        self.plans.addItems(self.plans_list[:-1])
        widget_layout.addWidget(self.plans)

        # Кнопка отправки письма
        accept_plan = QPushButton("Подтвердить график")
        accept_plan.setObjectName("simple_button")
        accept_plan.clicked.connect(
            self.accept_chosen_plan
        )
        widget_layout.addWidget(accept_plan)

        widget_layout.addStretch()

        back_btn = QPushButton("<- Назад")
        back_btn.setObjectName("hide_btn")
        back_btn.clicked.connect(
            lambda: self.controller.switch_window(RegistrationWindow.RegistrationWindowClass)
        )

        widget_layout.addWidget(back_btn)

    def accept_chosen_plan(self):
        """ Метод добавления ID графика в данные """
        # Вычисление ID графика из словаря в конце списка
        plan_id = self.plans_list[-1][self.plans.currentText()]
        self.old_form_data["График работы"] = plan_id

        # Создание аккаунта
        if SystemMessageBox("Вы проверили данные?").send_W_messsage():
            if self.old_form_data["Логин"] not in self.database.take_user_accounts_data():
                if self.database.create_worker_account(self.old_form_data):
                    SystemMessageBox("Аккаунт создан!").send_I_messsage()
                    # Получение ID сотрудника
                    worker_id = self.database.take_customer_id(
                        customer_login=self.old_form_data["Логин"],
                        customer_password=self.old_form_data["Пароль"],
                        customer_role="Волонтер"
                    )

                    if worker_id == -1:
                        # Если аккаунт по каким-то причинам не найден (Такое ток от сервера сломаться может)
                        show_critical_alert_simple(self, "Ошибка входа в аккаунт! Попробуйте позже!")
                        return
                    # Запись ID сотрудника в статический файл
                    StaticDataSaver().set_customer_id(worker_id)
                    # Запись роли в статический файл
                    StaticDataSaver().set_role(self.old_form_data["Роль"])

                    # Открытие окна пользователя
                    self.controller.switch_window(MainWorkerPage)
                    return
                show_critical_alert_simple(self, "Ошибка создания аккаунта!")
                return
            show_critical_alert_simple(self, "Сотрудник с похожими данными уже существует!")
