import datetime, imaplib, functools, ssl, requests
from PyQt5 import QtWidgets, uic, QtCore, QtGui
from utils import paths, StorageSingleton
from ui.utils import helpers
from .about_dialog import AboutDialog
from .help_dialog import HelpDialog

import logging
logger = logging.getLogger(__name__)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(paths.get_ui_filepath("main_window.ui"), self)
        self.setWindowIcon(QtGui.QIcon(paths.get_art_filepath("icon.png")))

        self.uiAction_about.triggered.connect(self.showActionAbout)
        self.uiAction_help.triggered.connect(self.showActionHelp)
        self.uiAction_close.triggered.connect(self.quit)
        self.uiAction_add.triggered.connect(self.actionTriggeredAddEmail)

        self.uiAction_add.setIcon(QtGui.QIcon(paths.get_art_filepath("actionAdd.png")))

        self.uiItems = []
        #load data
        for entry in StorageSingleton()["data"]:
            try:
                self.uiItems.append(self.createEmailForm())
                logger.info("Create email form for %s" % entry["email"])
                self.uiItems[-1]["email"].setText(entry["email"])
                self.uiItems[-1]["password"].setText(entry["password"])
                self.uiItems[-1]["emailServer"].setText(entry["emailServer"])
                self.uiItems[-1]["port"].setValue(entry["port"])
                self.uiItems[-1]["expiryDate"].setCurrentText(helpers.DateToDateString(entry["expiryDate"]))
                self.uiItems[-1]["startTls"].setChecked(entry["startTls"])
                self.uiItems[-1]["groupBox"].setTitle(entry["email"])
            except Exception as error:
                logger.info("E R R O R while loading email account data & creating uiItems! %s " % str(error))
                self.statusBar.showMessage("E R R O R: %s " % str(error), 2000)
                helpers.createMessageWindow(self, error)

        if len(StorageSingleton()["data"]) == 0:
            self.createEmailForm()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.timerTimoutDeleteEmails)
        self.timer.start(3600000)

    def quit(self):
        self.storeEmailData()
        QtWidgets.QApplication.quit()
    
    def actionTriggeredAddEmail(self):
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
        uiButton_deleteNow          = QtWidgets.QPushButton('Delete emails now', self)
        uiButton_deleteEmail        = QtWidgets.QPushButton(self)

        # Set standart Values
        uiSpinBox_port.setMaximum(99999)
        uiSpinBox_port.setValue(993)
        uiCombobox_expiryDate.addItems(["1 Tag", "4 Tage", "1 Woche", "2 Wochen", "1 Monat", "4 Monate", "6 Monate", "1 Jahr"])
        uiLineEdit_password.setEchoMode(QtWidgets.QLineEdit.Password)
        uiButton_deleteEmail.setIcon(QtGui.QIcon(paths.get_art_filepath("actionRemove.png")))
        uiButton_deleteNow.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_TrashIcon))

        uiLineEdit_email.setPlaceholderText("Email@example.com") 
        uiLineEdit_password.setPlaceholderText("passwort") 
        uiLineEdit_emailServer.setPlaceholderText("imap.mail.com") 
        uiCombobox_expiryDate.setCurrentIndex(uiCombobox_expiryDate.findText("1 Jahr"))

        # Store data onchange
        uiLineEdit_email.textChanged.connect(self.storeEmailData)
        uiLineEdit_password.textChanged.connect(self.storeEmailData)
        uiLineEdit_emailServer.textChanged.connect(self.storeEmailData)
        uiSpinBox_port.valueChanged.connect(self.storeEmailData)
        uiCombobox_expiryDate.currentTextChanged.connect(self.storeEmailData)
        uiCheckbox_startTls.stateChanged.connect(self.storeEmailData)

        logger.info("Create email form")
        # Add items to QForm
        formLayout = QtWidgets.QFormLayout()
        formLayout.addRow(QtWidgets.QLabel("Email"), uiLineEdit_email)
        formLayout.addRow(QtWidgets.QLabel("Passwort"), uiLineEdit_password)
        formLayout.addRow(QtWidgets.QLabel("Emailserver"), uiLineEdit_emailServer)
        formLayout.addRow(QtWidgets.QLabel("Port"), uiSpinBox_port)
        formLayout.addRow(QtWidgets.QLabel("Verfallsdatum"), uiCombobox_expiryDate)
        formLayout.addRow(QtWidgets.QLabel("start_tls"), uiCheckbox_startTls)
        formLayout.addRow(uiButton_deleteEmail, uiButton_deleteNow)

        logger.info("Add items")

        # Create widget
        groupBox = QtWidgets.QGroupBox("Neue Email")
        groupBox.setLayout(formLayout)

        self.uiLayout_emails.addWidget(groupBox)

        uiItems = {
                   "groupBox":        groupBox,
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
        deleteEmails = helpers.createConfirmationWindow(self, "Delete emails now?")
        if deleteEmails:
            logger.info("Delete all emails of %s before date" % str(uiItems["email"].text()))
            self.deleteEmails(helpers.uiItemsToValues(uiItems))
            self.statusBar.showMessage("Gelöscht ✓",2000)

    def deleteEmailAccount(self, items, groupBox):
        deleteEmailAccount = helpers.createConfirmationWindow(self, "Do you really want to delete this Email account from ClOwn-Mails?")
        if deleteEmailAccount:
            logger.info("Delete email form")
            groupBox.hide()
            self.statusBar.showMessage("Email-Konto gelöscht: %s ✓" % items["email"].text(), 2000)
            del self.uiItems[self.uiItems.index(items)]
            self.storeEmailData()

    def timerTimoutDeleteEmails(self):
        self.storeEmailData()
        logger.info("Delete emails from all accounts")
        if len(self.uiItems) != 0:
            for emailAccount in self.uiItems:
                self.deleteEmails(helpers.uiItemsToValues(emailAccount))

    def deleteEmails(self, emailValues):
        if not self.isConnectedToInternet():
            return
        # Check if all credentials were entered
        for data in emailValues.values():
            if data == "":
                helpers.createMessageWindow(self, "Nicht alle Felder wurden korrekt ausgefüllt")
                return
        try:
            if emailValues["startTls"]:
                logger.info("Establishe connection with start_tls...")
                tls_context = ssl.create_default_context()
            
            # Connect to server
            self.statusBar.showMessage("Die Verbindung zum Server wird hergestellt...")
            logger.info("Connecting to server '%s' on port %s..." % (emailValues["emailServer"], emailValues["port"]))
            serverConnection = imaplib.IMAP4_SSL(emailValues["emailServer"], emailValues["port"])
            if emailValues["startTls"]:
                serverConnection.starttls(ssl_context=tls_context)
            self.statusBar.showMessage("Logging in...")
            logger.info("Logging in as '%s'..." % emailValues["email"])
            serverConnection.login(emailValues["email"], emailValues["password"])

            # Search for emails
            serverConnection.select('Inbox')
            beforeDate = (datetime.date.today() - datetime.timedelta(emailValues["expiryDate"])).strftime("%d-%b-%Y")
            logger.info("Deleting everything before %s that is not FLAGGED" % str(beforeDate))

            self.statusBar.showMessage("Löscht...")
            resp, data = serverConnection.uid("search", None, "(NOT FLAGGED) BEFORE {0}".format(beforeDate)) # search and return Uids
            data = [entry.decode() for entry in data]
            uids = data[0].split()    
            logger.info("Deleting %d mails" % len(uids))
            for uid in uids:
                resp,data = serverConnection.uid('fetch', uid, "(BODY[HEADER])")
                serverConnection.uid('STORE', uid, '+FLAGS', '(\\Deleted)')
            serverConnection.expunge()

            logger.info("Close connection")
            serverConnection.close() 
            logger.info("Logout")
            serverConnection.logout()
            self.statusBar.showMessage("Fertig ✓", 2000)
            
            if len(uids) > 0:
                self.tray_icon.showMessage(
                    "ClOwn-Mails",
                    "Es wurden erfolgreich %d Emails gelöscht!" % len(uids),
                    QtWidgets.QSystemTrayIcon.Information,
                    4000
                )

        except Exception as error:
            logger.error("E R R O R while deleting emails! %s " % str(error))
            self.statusBar.showMessage("E R R O R: %s " % str(error), 2000)
            helpers.createMessageWindow(self, error)
            return
        
    def showActionAbout(self, *args):
        logger.info("Showing About Dialog...")
        self.about = AboutDialog()
        self.about.show()
        result = self.about.exec_()

    def showActionHelp(self, *args):
        logger.info("Showing Help Dialog...")
        self.help = HelpDialog()
        self.help.show()
        result = self.help.exec_()

    def storeEmailData(self):
        logger.info("Store data")
        StorageSingleton()["data"] = [helpers.uiItemsToValues(data) for data in self.uiItems]

        # Set groupBox title to email
        for uiItem in self.uiItems:
            uiItem["groupBox"].setTitle(uiItem["email"].text())

    def isConnectedToInternet(self):
        try:
            logger.debug("Checking for internet connection...")
            result = requests.head("https://www.google.com/", timeout=8)
            return True
        except requests.ConnectionError:
            logger.warning("No connection to the Internet!")
            return False