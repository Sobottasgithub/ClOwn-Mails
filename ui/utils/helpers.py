from PyQt5 import QtWidgets

def createMessageWindow(window, message):
    msgBox = QtWidgets.QMessageBox.question(
        window,
        "ClOwn-Mails | WARNING", 
        str(message),
        QtWidgets.QMessageBox.Ok
    )
    return msgBox

def uiItemsToValues(uiItems):
    data = {}
    data["emailServer"] =  uiItems["emailServer"].text()
    data["port"] = uiItems["port"].value()
    data["email"] = uiItems["email"].text()
    data["password"] = uiItems["password"].text()
    data["expiryDate"] = dateStringToDate(uiItems["expiryDate"].currentText())
    data["startTls"] = uiItems["startTls"].isChecked()
    return data

def dateStringToDate(dateString):
    dateStrings = {"1 Tag": 1, "4 Tage": 4, "1 Woche": 7, "2 Wochen": 14, "1 Monat": 31, "4 Monate": 122, "6 Monate": 183, "1 Jahr": 365}
    return dateStrings[dateString]

def DateToDateString(date):
    dateStrings = {1: "1 Tag", 4: "4 Tage", 7: "1 Woche", 14: "2 Wochen", 31: "1 Monat", 122: "4 Monate", 183: "6 Monate", 365: "1 Jahr"}
    return dateStrings[date]