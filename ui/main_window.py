import json, datetime, imaplib, functools, ssl
from PyQt5 import QtWidgets, uic, QtCore
from utils import paths
from ui.utils import helpers

import logging
logger = logging.getLogger(__name__)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(paths.get_ui_filepath("main_window.ui"), self)

        self.data = []

        if len(self.data) == 0:
            self.createNewEmail()
        self.uiButton_add.clicked.connect(self.createNewEmail)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.deleteEmailsAllAccounts)
        self.timer.start(36000000)
    
    def createNewEmail(self):
        formLayout, uiItems = self.createEmailForm()

        # Put QForm in a widget
        formWidget = QtWidgets.QWidget()
        formWidget.setLayout(formLayout)

        # Put widget in a qlistwidget item
        listWidgetItem = QtWidgets.QListWidgetItem()
        listWidgetItem.setSizeHint(formWidget.sizeHint())

        # Add everything into the Listwidget
        self.uiWidget_emails.addItem(listWidgetItem)
        self.uiWidget_emails.setItemWidget(listWidgetItem, formWidget)

        self.data.append({"uiItems": uiItems})
        uiItems["deleteNow"].clicked.connect(functools.partial(self.deleteNow, uiItems))
        uiItems["deleteEmail"].clicked.connect(functools.partial(self.deleteEmailAccount, {"uiItems": uiItems}, listWidgetItem))

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
        uiCombobox_expiryDate.addItems(["1 Day", "4 Days", "1 Week", "2 Weeks", "1 Month", "4 Months", "6 Months", "1 Year"])

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
        self.deleteEmails(helpers.uiItemsToValues(uiItems))

    def deleteEmailAccount(self, items, listWidgetItem):
        listWidgetItem.setHidden(True)
        del self.data[self.data.index(items)]

    def deleteEmailsAllAccounts(self):
        if len(self.data) != 0:
            for emailAccount in self.data:
                self.deleteEmails(helpers.uiItemsToValues(emailAccount["uiItems"]))

    def deleteEmails(self, emailValues):
        # Check if all credentials were entered
        for data in emailValues.values():
            if data == "":
                helpers.createMessageWindow(self, "Not all credentials were entered")
                return
        try:
            if emailValues["startTls"]:
                tls_context = ssl.create_default_context()
            
            # Connect to server
            serverConnection = imaplib.IMAP4_SSL(emailValues["emailServer"], emailValues["port"])
            if emailValues["startTls"]:
                serverConnection.starttls(ssl_context=tls_context)
            serverConnection.login(emailValues["email"], emailValues["password"])

            # Search for emails
            serverConnection.select('Inbox')
            beforeDate = (datetime.date.today() - datetime.timedelta(emailValues["expiryDate"])).strftime("%d-%b-%Y")

            resp, data = serverConnection.uid('search',None, '(BEFORE {0})'.format(beforeDate)) # search and return Uids
            uids = data[0].split()    
            for uid in uids:
                resp,data = serverConnection.uid('fetch',uid,"(BODY[HEADER])")             
                serverConnection.uid('STORE',uid, '+FLAGS', '(\\Deleted)')
            serverConnection.expunge()
                
            serverConnection.close()
            serverConnection.logout()

        except Exception as error:
            helpers.createMessageWindow(self, error)
            return