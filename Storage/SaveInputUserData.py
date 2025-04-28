class UserInputDataSave:
    """ Класс для хранения пользовательского ввода, для удобства работы """
    __user_data: dict = {
            "ФИО": "",
            "Логин": "",
            "Пароль": "",
            "Почта": "@mail.ru",
            "Телефон": "+7",
            "Пол": "Мужчина",
            "Роль": "Пользователь"
        }

    @staticmethod
    def set_input_data(new_data: dict):
        UserInputDataSave.__user_data = new_data

    @staticmethod
    def get_data() -> dict: return UserInputDataSave.__user_data