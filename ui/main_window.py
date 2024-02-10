import json, datetime, imaplib, functools
from PyQt5 import QtWidgets, uic
from utils import paths

import logging
logger = logging.getLogger(__name__)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(paths.get_ui_filepath("main_window.ui"), self)

        self.data = []

        self.createNewEmail()
        self.uiButton_add.clicked.connect(self.createNewEmail)
    
    def createNewEmail(self):
        formLayout, uiItems = self.createEmailForm()

        #put it in a widget
        formWidget = QtWidgets.QWidget()
        formWidget.setLayout(formLayout)

        #put it in a qlistwidget item
        listWidgetItem = QtWidgets.QListWidgetItem()
        listWidgetItem.setSizeHint(formWidget.sizeHint())

        # Add everything into the Listwidget
        self.uiWidget_emails.addItem(listWidgetItem)
        self.uiWidget_emails.setItemWidget(listWidgetItem, formWidget)

        self.data.append({"uiItems": uiItems})
        uiItems["deleteNow"].clicked.connect(functools.partial(self.deleteNow, uiItems))
        uiItems["deleteEmail"].clicked.connect(functools.partial(self.deleteEmail, {"uiItems": uiItems}, listWidgetItem))

    def createEmailForm(self):
        uiLineEdit_email        = QtWidgets.QLineEdit()
        uiLineEdit_password     = QtWidgets.QLineEdit()
        uiLineEdit_emailServer  = QtWidgets.QLineEdit()
        uiSpinBox_port          = QtWidgets.QSpinBox()
        uiCombobox_expiryDate   = QtWidgets.QComboBox()
        uiCheckbox_startTls     = QtWidgets.QCheckBox()
        uiButton_deleteNow      = QtWidgets.QPushButton('Delete emails', self)
        uiButton_deleteEmail    = QtWidgets.QPushButton('-', self)

        uiSpinBox_port.setMaximum(99999)
        uiSpinBox_port.setValue(933)
        uiCombobox_expiryDate.addItems(["1 Day", "4 Days", "1 Week", "2 Weeks" "1 Month", "4 Month", "6 Month", "1 Year"])

        # Add items to QForm
        formLayout = QtWidgets.QFormLayout()
        formLayout.addRow(QtWidgets.QLabel("Email"), uiLineEdit_email)
        formLayout.addRow(QtWidgets.QLabel("Password"), uiLineEdit_password)
        formLayout.addRow(QtWidgets.QLabel("Emailserver"), uiLineEdit_emailServer)
        formLayout.addRow(QtWidgets.QLabel("Port"), uiSpinBox_port)
        formLayout.addRow(QtWidgets.QLabel("Expirydate"), uiCombobox_expiryDate)
        formLayout.addRow(QtWidgets.QLabel("start_tls"), uiCheckbox_startTls)
        formLayout.addRow(uiButton_deleteEmail, uiButton_deleteNow)

        uiItems = {"email":         uiLineEdit_email, 
                   "password":      uiLineEdit_password, 
                   "emailServer":   uiLineEdit_emailServer, 
                   "port":          uiSpinBox_port,
                   "expiryDate":    uiCombobox_expiryDate,
                   "startTls":      uiCheckbox_startTls,
                   "deleteNow":     uiButton_deleteNow,
                   "deleteEmail":   uiButton_deleteEmail
                }

        return (formLayout, uiItems)

    def deleteNow(self, uiItems):
        pass

    def deleteEmail(self, items, listWidgetItem):
        listWidgetItem.setHidden(True)
        del self.data[self.data.index(items)]