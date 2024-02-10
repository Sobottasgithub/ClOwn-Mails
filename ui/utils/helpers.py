from PyQt5 import QtWidgets

def createMessageWindow(window, message):
    msgBox = QtWidgets.QMessageBox.question(
        window,
        "ClOwn-Mails | WARNING", 
        str(message),
        QtWidgets.QMessageBox.Ok
    )
    return msgBox
