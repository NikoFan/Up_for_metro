import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from TOKEN import *

def send_mail_message(send_to: str, title: str, mail_message: str):
    """ Функция отправки сообщения на почту """

    # Порт для отправки сообщения
    send_message_tool = smtplib.SMTP('smtp.mail.ru', 587)
    # Настройка шифрования
    send_message_tool.starttls()

    # Настройка письма для отправки
    message = MIMEMultipart()
    message["From"] = mail_address  # Адрес из файла TOKEN.py
    message["To"] = send_to  # Адрес из ввода пользователя
    message['Subject'] = title
    body = f"{mail_message}"
    message.attach(MIMEText(body, 'plain'))
    # Отправка письма
    send_message_tool.login(mail_address, mail_token)
    send_message_tool.send_message(message)
    send_message_tool.quit()