def check_fio(user_name_data: str) -> list:
    """ Метод проверки ФИО на корректность """
    if len(user_name_data.split(" ")) in range(2, 4):
        return [True]
    return [False, "ФИО состоит из 3х значений: Фамилия Имя Отчество!"]


def check_phone(phone_data: str) -> list:
    """ Метод проверки телефона на корректность """
    if (
            len(phone_data) == 12 and
            phone_data[2] == "9" and
            phone_data[1:].isdigit()

    ):
        return [True]
    print(phone_data)
    return [False, "Длина телефона должна быть 12 символов\n"
                   "Номер телефона начинается с 9\n"
                   "В телефоне должны быть только целочисленные значения!"]


def check_mail(mail_address: str) -> list:
    """ Метод проверки почтового адреса на корректность """
    if (
            len(mail_address) > 0 and
            len(mail_address.split("@")) == 2 and
            mail_address.count("mail.ru") == 1
    ):
        return [True]

    return [False, "Неверно введенная почта!"]


def check_password(password_data: str) -> list:
    """ Метод проверки пароля на корректность """
    if len(password_data) >= 8:
        return [True]
    return [False, "Длина пароля меньше 8 символов!"]


def check_login(login_data: str) -> list:
    """ Метод проверки логина на корректность """
    if len(login_data) != 0:
        return [True]
    return [False, "Логин не может быть пустым полем!"]


# Словарь с готовыми вызовами проверок
const_data = {
    "Логин": check_login,
    "Пароль": check_password,
    "ФИО": check_fio,
    "Телефон": check_phone,
    "Почта": check_mail,

}


def rout(dict_to_check: dict) -> list:
    for dict_key, dict_value in dict_to_check.items():
        try:
            check_action_result = const_data[dict_key](dict_value)
            # из функции возвращается список с результатом и сообщением
            if check_action_result[0] == False:
                return [False, check_action_result[1]]
        except Exception:
            ...
    return [True]


from datetime import datetime
def is_date_valid(input_date_str, date_format="%Y-%m-%d"):
    try:
        # Преобразуем строку в объект datetime
        input_date = datetime.strptime(input_date_str, date_format).date()
        today = datetime.now().date()

        if input_date <= today:
            print("Ошибка: Дата не может быть раньше сегодняшней!")
            return False
        else:
            print("Дата корректна!")
            return True
    except ValueError:
        print("Ошибка: Неверный формат даты!")
        return False
