import datetime, imaplib, functools, ssl
from PyQt5 import QtWidgets, uic, QtCore
from utils import paths, StorageSingleton
from ui.utils import helpers
from .about_dialog import AboutDialog

import logging
logger = logging.getLogger(__name__)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(paths.get_ui_filepath("main_window.ui"), self)
        self.showMinimized()

        self.uiAction_about.triggered.connect(self.actionAbout)

        self.uiItems = []
        #load data
        for index in range(len(StorageSingleton()["data"])):
            self.uiItems.append(self.createEmailForm())
            singletonData = StorageSingleton()["data"][index]
            self.uiItems[index]["email"].setText(singletonData["email"])
            self.uiItems[index]["password"].setText(singletonData["password"])
            self.uiItems[index]["emailServer"].setText(singletonData["emailServer"])
            self.uiItems[index]["port"].setValue(singletonData["port"])
            self.uiItems[index]["expiryDate"].setCurrentText(helpers.DateToDateString(singletonData["expiryDate"]))
            self.uiItems[index]["startTls"].setChecked(singletonData["startTls"])

        if len(self.uiItems) == 0:
            self.uiItems.append(self.createEmailForm())
        self.uiButton_add.clicked.connect(self.addNewEmail)
        self.uiButton_save.clicked.connect(self.store)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.deleteEmailsAllAccounts)
        self.timer.start(36000000)
    
    def addNewEmail(self):
        self.uiItems.append(self.createEmailForm())

    def createEmailForm(self):
        uiLineEdit_email            = QtWidgets.QLineEdit()
        uiLineEdit_password         = QtWidgets.QLineEdit()
        uiLineEdit_emailServer      = QtWidgets.QLineEdit()
        uiSpinBox_port              = QtWidgets.QSpinBox()
        uiCombobox_expiryDate       = QtWidgets.QComboBox()
        uiCheckbox_startTls         = QtWidgets.QCheckBox()
        uiButton_deleteNow          = QtWidgets.QPushButton('Delete emails', self)
        uiButton_deleteEmail        = QtWidgets.QPushButton('-', self)

        uiSpinBox_port.setMaximum(99999)
        uiSpinBox_port.setValue(933)
        uiCombobox_expiryDate.addItems(["1 Day", "4 Days", "1 Week", "2 Weeks", "1 Month", "4 Months", "6 Months", "1 Year"])
        uiLineEdit_password.setEchoMode(QtWidgets.QLineEdit.Password)

        # Add items to QForm
        formLayout = QtWidgets.QFormLayout()
        formLayout.addRow(QtWidgets.QLabel("Email"), uiLineEdit_email)
        formLayout.addRow(QtWidgets.QLabel("Password"), uiLineEdit_password)
        formLayout.addRow(QtWidgets.QLabel("Emailserver"), uiLineEdit_emailServer)
        formLayout.addRow(QtWidgets.QLabel("Port"), uiSpinBox_port)
        formLayout.addRow(QtWidgets.QLabel("Expirydate"), uiCombobox_expiryDate)
        formLayout.addRow(QtWidgets.QLabel("start_tls"), uiCheckbox_startTls)
        formLayout.addRow(uiButton_deleteEmail, uiButton_deleteNow)

        uiItems = {"email":           uiLineEdit_email, 
                   "password":        uiLineEdit_password, 
                   "emailServer":     uiLineEdit_emailServer, 
                   "port":            uiSpinBox_port,
                   "expiryDate":      uiCombobox_expiryDate,
                   "startTls":        uiCheckbox_startTls,
                   "deleteNow":       uiButton_deleteNow,
                   "deleteEmail":     uiButton_deleteEmail,
                }

        # Put QForm in a widget
        formWidget = QtWidgets.QWidget()
        formWidget.setLayout(formLayout)

        # Put widget in a qlistwidget item
        listWidgetItem = QtWidgets.QListWidgetItem()
        listWidgetItem.setSizeHint(formWidget.sizeHint())

        # Add everything into the Listwidget
        self.uiWidget_emails.addItem(listWidgetItem)
        self.uiWidget_emails.setItemWidget(listWidgetItem, formWidget)

        uiItems["deleteNow"].clicked.connect(functools.partial(self.deleteNow, uiItems))
        uiItems["deleteEmail"].clicked.connect(functools.partial(self.deleteEmailAccount, uiItems, listWidgetItem))

        return uiItems

    def deleteNow(self, uiItems):
        self.store()
        self.deleteEmails(helpers.uiItemsToValues(uiItems))
        self.statusBar.showMessage("Deleted ✓",2000)

    def deleteEmailAccount(self, items, listWidgetItem):
        listWidgetItem.setHidden(True)
        self.statusBar.showMessage("Deleted user: %s ✓" % items["email"].text(), 2000)
        del self.uiItems[self.uiItems.index(items)]
        self.store()

    def deleteEmailsAllAccounts(self):
        self.store()
        if len(self.uiItems) != 0:
            for emailAccount in self.uiItems:
                self.deleteEmails(helpers.uiItemsToValues(emailAccount))

    def store(self):
        self.statusBar.showMessage("Saved ✓", 2000)
        StorageSingleton()["data"] = [helpers.uiItemsToValues(data) for data in self.uiItems]

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
            self.statusBar.showMessage("Connecting to server...")
            serverConnection = imaplib.IMAP4_SSL(emailValues["emailServer"], emailValues["port"])
            if emailValues["startTls"]:
                serverConnection.starttls(ssl_context=tls_context)
            self.statusBar.showMessage("Logging in...")
            serverConnection.login(emailValues["email"], emailValues["password"])

            # Search for emails
            serverConnection.select('Inbox')
            beforeDate = (datetime.date.today() - datetime.timedelta(emailValues["expiryDate"])).strftime("%d-%b-%Y")

            self.statusBar.showMessage("Deleting ...")
            resp, data = serverConnection.uid('search',None, '(BEFORE {0})'.format(beforeDate)) # search and return Uids
            uids = data[0].split()    
            for uid in uids:
                resp,data = serverConnection.uid('fetch',uid,"(BODY[HEADER])")             
                serverConnection.uid('STORE',uid, '+FLAGS', '(\\Deleted)')
            serverConnection.expunge()
                
            serverConnection.logout()
            serverConnection.close()
            self.statusBar.showMessage("Complete ✓", 2000)

        except Exception as error:
            self.statusBar.showMessage("E R R O R: %s " % str(error), 2000)
            helpers.createMessageWindow(self, error)
            return
        
    def actionAbout(self, *args):
        logger.info("Showing About Dialog...")
        self.about = AboutDialog()
        self.about.show()
        result = self.about.exec_()