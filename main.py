# Библиотеки
from PySide6.QtWidgets import QMainWindow, QStackedWidget, QApplication
from PySide6.QtCore import QMargins
import sys

from windows import LoginWindow
from database import Database


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Metro-Help")
        # Установка размеров окна
        self.resize(600, 800)
        self.setMinimumWidth(400)

        # Подключение к базе данных
        self.db_connect = Database.DatabaseConnection()

        self.navigator = QStackedWidget()
        main_window = LoginWindow.LoginWindowClass(self)
        self.navigator.addWidget(main_window)

        # Установка окна в приложение
        self.setCentralWidget(self.navigator)

    def switch_window(self, window_name):
        """ Метод переключения между окнами """
        # Объявление класса открываемого окна
        goal_window = window_name(self)
        self.navigator.removeWidget(goal_window)
        self.navigator.addWidget(goal_window)
        self.navigator.setCurrentWidget(goal_window)


# #ed2934
# #f36983
style_sheet = """
QMainWindow {
background: #f36983;
border-radius: 20px;
}

QTimeEdit {
color: black;
background: white;
}

QCalendarWidget QAbstractItemView{
background: black;
color: white;
selection-color: white;
}

QMessageBox {
background: white;
color: black;
}

QLabel {
color: black;
}

QComboBox {
background: white;
color: black;
font-size: 20px;
}

QFrame {
background: white; 
}

QTextEdit {
color: black;
background: white;
font-size: 20px;
padding: 5px;
} 

QLineEdit {
background: white;
color: black;
font-size: 20px;
}

#title_style {
font-size: 35px;
color: #ed2934;
font-weight: bold;
qproperty-alignment: AlignCenter;
}

#hint_text {
color: black;
padding-left: 10px;
font-size: 20px;
}

#verification_mail_style {
color: black;
background: white;
qproperty-alignment: AlignCenter;
font-size: 20px;
}

#small_title_style {
color: black;
font-size: 25px;
qproperty-alignment: AlignCenter;
font-weight: bold;
}

#instruction_label {
font-size: 16px;
qproperty-alignment: AlignCenter;
color: black;
background: none;
}

#account_normal_text {
color: black;
padding: 5px;
background: white;
font-size: 20px;
}

#account_title_text {
color: black;
padding: 5px;
background: white;
font-size: 28px;
qproperty-alignment: AlignCenter;
font-weight: bold;
}

#simple_button {
background: #ed2934;
color: white;
font-size: 20px;
border: none;
padding: 5px;
border-radius: 10px;
}

#simple_button:hover {
background: #ed2934;
color: white;
font-size: 20px;
font-weight: bold;
}

#simple_button:pressed {
background: #ef434d;
color: white;
font-size: 20px;
font-weight: bold;
}

#hide_btn {
border: none;
border-radius: 10px;
background: none;
color: black;
padding: 10px;
font-size: 18px;
}

QRadioButton::indicator:checked {
background: #ed2934;
border-radius: 20px;
}
QRadioButton::indicator {
background: white;
border-radius: 20px;
}

QRadioButton {
color: black;
background: none;
font-size: 20px;

}

#hide_btn:hover {
border: none;
border-radius: 10px;
background: none;
color: black;
font-weight: bold;
font-size: 18px;
}

#hide_btn:pressed {
border: none;
border-radius: 10px;
background: #dfdfdf;
color: black;
font-weight: bold;
font-size: 18px;
}

#small_text {
font-size: 20px;
color: black;
background: none;
}

#level_choose {
height: 40px;
width: 40px;
border: none;
border-radius: 20px;
background: none;
color: black;
font-size: 25px;
font-weight: bold;
}

#level_choose:hover {
height: 40px;
width: 40px;
border: none;
border-radius: 20px;
background: #dfdfdf;
color: black;
font-size: 25px;
font-weight: bold;
}

#level_choose:pressed {
height: 40px;
width: 40px;
border: none;
border-radius: 20px;
background: #ed2934;
color: black;
font-size: 25px;
font-weight: bold;
}


"""

if __name__ == '__main__':
    application = QApplication(sys.argv)
    application.setStyleSheet(style_sheet)
    main_class = Main()
    main_class.show()
    application.exec()
