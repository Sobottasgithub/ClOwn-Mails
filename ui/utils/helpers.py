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
    dateStrings = {"1 Day": 1, "4 Days": 4, "1 Week": 7, "2 Weeks": 14, "1 Month": 31, "4 Months": 122, "6 Months": 183, "1 Year": 365}
    return dateStrings[dateString]

def DateToDateString(date):
    dateStrings = {1: "1 Day", 4: "4 Days", 7: "1 Week", 14: "2 Weeks", 31: "1 Month", 122: "4 Months", 183: "6 Months", 365: "1 Year"}
    return dateStrings[date]