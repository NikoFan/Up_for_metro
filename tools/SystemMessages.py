from PySide6.QtWidgets import QMessageBox


class SystemMessageBox:
    def __init__(self, message_word: str):
        # Создание заготовок
        self.message_box = QMessageBox()
        self.message_box.setText(message_word)

    def send_I_messsage(self):
        """ Метод создания информативного сообщения для пользователя """
        self.message_box.setIcon(QMessageBox.Icon.Information)
        self.message_box.setStandardButtons(QMessageBox.StandardButton.Yes)
        self.message_box.exec()

    def send_C_messsage(self):
        """ Метод создания запрещающего сообщения для пользователя """
        self.message_box.setIcon(QMessageBox.Icon.Critical)
        self.message_box.setStandardButtons(QMessageBox.StandardButton.Yes)
        self.message_box.exec()

    def send_W_messsage(self):
        """ Метод создания предупреждающего сообщения для пользователя """
        self.message_box.setIcon(QMessageBox.Icon.Warning)
        self.message_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        result = self.message_box.exec()
        # Если результат сообщения - ДА, то вернется True (Код кнопки ДА меньше 20 000)
        return result < 20_000
