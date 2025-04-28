def dict_inspector(data: dict) -> bool:
    """ Функция проверки элементов словаря на SQLI"""
    for data_key, data_value in data.items():
        if (
                "'" in str(data_value) or
                "-" in str(data_value) or
                ";" in str(data_value)
        ):
            return False
    return True


def word_inspector(word: str) -> bool:
    """ Функция проверки отдельных слов на SQLI """
    return not ("'" in word or
                "-" in word or
                ";" in word)
