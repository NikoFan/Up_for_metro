from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QLabel

def show_alert_simple(parent, message, timeout=2000):
    """Простая версия toast без анимации"""
    toast = QLabel(parent)
    toast.setMaximumWidth(350)
    toast.setWordWrap(True)
    toast.setText(message)
    toast.setStyleSheet("""
        QLabel {
            color: white;
            background: black;
            padding: 10px;
            font-size: 18px;
            border-radius: 5px;
            qproperty-alignment: AlignCenter;
        }
    """)
    toast.adjustSize()
    toast.move(parent.rect().center() - toast.rect().center())
    toast.show()

    # Удаляем через timeout миллисекунд
    QTimer.singleShot(timeout, toast.deleteLater)

def show_critical_alert_simple(parent, message, timeout=2000):
    """Простая версия toast без анимации"""
    toast = QLabel(parent)
    toast.setMaximumWidth(350)
    toast.setWordWrap(True)
    toast.setText(message)
    toast.setStyleSheet("""
        QLabel {
            color: white;
            background: #df241f;
            padding: 10px;
            font-size: 18px;
            border-radius: 5px;
            qproperty-alignment: AlignCenter;
        }
    """)
    toast.adjustSize()
    toast.move(parent.rect().center() - toast.rect().center())
    toast.show()

    # Удаляем через timeout миллисекунд
    QTimer.singleShot(timeout, toast.deleteLater)