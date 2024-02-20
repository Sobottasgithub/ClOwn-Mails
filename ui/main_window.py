import datetime, imaplib, functools, ssl, sys
from PyQt5 import QtWidgets, uic, QtCore, QtGui
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

        self.uiAction_about.triggered.connect(self.showActionAbout)
        self.uiAction_close.triggered.connect(self.quit)

        self.uiItems = []
        #load data
        for index in range(len(StorageSingleton()["data"])):
            self.uiItems.append(self.createEmailForm())
            singletonData = StorageSingleton()["data"][index]
            logger.info("Create email form for %s" % singletonData["email"])
            self.uiItems[index]["email"].setText(singletonData["email"])
            self.uiItems[index]["password"].setText(singletonData["password"])
            self.uiItems[index]["emailServer"].setText(singletonData["emailServer"])
            self.uiItems[index]["port"].setValue(singletonData["port"])
            self.uiItems[index]["expiryDate"].setCurrentText(helpers.DateToDateString(singletonData["expiryDate"]))
            self.uiItems[index]["startTls"].setChecked(singletonData["startTls"])
            self.uiItems[index]["groupBox"].setTitle(singletonData["email"])

        if len(self.uiItems) == 0:
            self.uiItems.append(self.createEmailForm())
        self.uiButton_add.clicked.connect(self.buttonClickedAddEmail)
        self.uiButton_save.clicked.connect(self.storeEmailData)

        self.uiButton_save.setIcon(QtGui.QIcon(paths.get_art_filepath("actionOk.png")))
        self.uiButton_add.setIcon(QtGui.QIcon(paths.get_art_filepath("actionAdd.png")))

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.timerTimoutDeleteEmails)
        self.timer.start(36000000)

    def closeEvent(self, event):
        self.quit()

    def quit(self):
        self.storeEmailData()
        sys.exit()
    
    def buttonClickedAddEmail(self):
        logger.info("Add new Email")
        self.uiItems.append(self.createEmailForm())

    def createEmailForm(self):
        logger.info("Create ui Items")

        # Create uiItems
        uiLineEdit_email            = QtWidgets.QLineEdit()
        uiLineEdit_password         = QtWidgets.QLineEdit()
        uiLineEdit_emailServer      = QtWidgets.QLineEdit()
        uiSpinBox_port              = QtWidgets.QSpinBox()
        uiCombobox_expiryDate       = QtWidgets.QComboBox()
        uiCheckbox_startTls         = QtWidgets.QCheckBox()
        uiButton_deleteNow          = QtWidgets.QPushButton('Delete emails', self)
        uiButton_deleteEmail        = QtWidgets.QPushButton(self)

        # Set standart Values
        uiSpinBox_port.setMaximum(99999)
        uiSpinBox_port.setValue(933)
        uiCombobox_expiryDate.addItems(["1 Day", "4 Days", "1 Week", "2 Weeks", "1 Month", "4 Months", "6 Months", "1 Year"])
        uiLineEdit_password.setEchoMode(QtWidgets.QLineEdit.Password)
        uiButton_deleteEmail.setIcon(QtGui.QIcon(paths.get_art_filepath("actionRemove.png")))
        uiButton_deleteNow.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_TrashIcon))

        uiLineEdit_email.setPlaceholderText("Email@example.com") 
        uiLineEdit_password.setPlaceholderText("password") 
        uiLineEdit_emailServer.setPlaceholderText("imap.mail.com") 

        logger.info("Create email form")
        # Add items to QForm
        formLayout = QtWidgets.QFormLayout()
        formLayout.addRow(QtWidgets.QLabel("Email"), uiLineEdit_email)
        formLayout.addRow(QtWidgets.QLabel("Password"), uiLineEdit_password)
        formLayout.addRow(QtWidgets.QLabel("Emailserver"), uiLineEdit_emailServer)
        formLayout.addRow(QtWidgets.QLabel("Port"), uiSpinBox_port)
        formLayout.addRow(QtWidgets.QLabel("Expirydate"), uiCombobox_expiryDate)
        formLayout.addRow(QtWidgets.QLabel("start_tls"), uiCheckbox_startTls)
        formLayout.addRow(uiButton_deleteEmail, uiButton_deleteNow)


        logger.info("Add items")
        groupBox = QtWidgets.QGroupBox("New Email")
        groupBox.setLayout(formLayout)

        self.uiLayout_emails.addWidget(groupBox)

        uiItems = {
                   "groupBox": groupBox,
                   "email":           uiLineEdit_email, 
                   "password":        uiLineEdit_password, 
                   "emailServer":     uiLineEdit_emailServer, 
                   "port":            uiSpinBox_port,
                   "expiryDate":      uiCombobox_expiryDate,
                   "startTls":        uiCheckbox_startTls,
                   "deleteNow":       uiButton_deleteNow,
                   "deleteEmail":     uiButton_deleteEmail,
                }

        logger.info("Connect buttons")
        uiItems["deleteNow"].clicked.connect(functools.partial(self.buttonClickedDeleteNow, uiItems))
        uiItems["deleteEmail"].clicked.connect(functools.partial(self.deleteEmailAccount, uiItems, groupBox))

        return uiItems

    def buttonClickedDeleteNow(self, uiItems):
        self.storeEmailData()
        logger.info("Delete all emails of %s before date" % str(uiItems["email"].text()))
        self.deleteEmails(helpers.uiItemsToValues(uiItems))
        self.statusBar.showMessage("Deleted ✓",2000)

    def deleteEmailAccount(self, items, groupBox):
        logger.info("Delete email form")
        groupBox.hide()
        self.statusBar.showMessage("Deleted user: %s ✓" % items["email"].text(), 2000)
        del self.uiItems[self.uiItems.index(items)]
        self.storeEmailData()

    def timerTimoutDeleteEmails(self):
        self.storeEmailData()
        logger.info("Delete emails from all accounts")
        if len(self.uiItems) != 0:
            for emailAccount in self.uiItems:
                self.deleteEmails(helpers.uiItemsToValues(emailAccount))

    def deleteEmails(self, emailValues):
        # Check if all credentials were entered
        for data in emailValues.values():
            if data == "":
                helpers.createMessageWindow(self, "Not all credentials were entered")
                return
        try:
            if emailValues["startTls"]:
                logger.info("establishe connection with start_tls")
                tls_context = ssl.create_default_context()
            
            # Connect to server
            self.statusBar.showMessage("Connecting to server...")
            logger.info("Connecting to server...")
            serverConnection = imaplib.IMAP4_SSL(emailValues["emailServer"], emailValues["port"])
            if emailValues["startTls"]:
                serverConnection.starttls(ssl_context=tls_context)
            self.statusBar.showMessage("Logging in...")
            logger.info("Logging in...")
            serverConnection.login(emailValues["email"], emailValues["password"])

            # Search for emails
            serverConnection.select('Inbox')
            beforeDate = (datetime.date.today() - datetime.timedelta(emailValues["expiryDate"])).strftime("%d-%b-%Y")
            logger.info("Deleting everything before %s " % str(beforeDate))

            self.statusBar.showMessage("Deleting ...")
            resp, data = serverConnection.uid('search',None, '(BEFORE {0})'.format(beforeDate)) # search and return Uids
            uids = data[0].split()    
            logger.info("Deleting %d mails" % len(uids))
            for uid in uids:
                resp,data = serverConnection.uid('fetch',uid,"(BODY[HEADER])")             
                serverConnection.uid('STORE',uid, '+FLAGS', '(\\Deleted)')
            serverConnection.expunge()

            logger.info("Close connection")
            serverConnection.close() 
            logger.info("Logout")
            serverConnection.logout()
            self.statusBar.showMessage("Complete ✓", 2000)

        except Exception as error:
            logger.info("E R R O R while deleting emails! %s " % str(error))
            self.statusBar.showMessage("E R R O R: %s " % str(error), 2000)
            helpers.createMessageWindow(self, error)
            return
        
    def showActionAbout(self, *args):
        logger.info("Showing About Dialog...")
        self.about = AboutDialog()
        self.about.show()
        result = self.about.exec_()

    def storeEmailData(self):
        logger.info("Store data")
        self.statusBar.showMessage("Saved ✓", 2000)
        StorageSingleton()["data"] = [helpers.uiItemsToValues(data) for data in self.uiItems]

        # Set groupBox title to email
        for uiItem in self.uiItems:
            uiItem["groupBox"].setTitle(uiItem["email"].text())