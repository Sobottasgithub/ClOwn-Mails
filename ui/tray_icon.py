from PyQt5 import QtWidgets, QtGui
from utils import paths

import logging
logger = logging.getLogger(__name__)

class TrayIcon(QtWidgets.QSystemTrayIcon):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        # Set icon
        self.setIcon(QtGui.QIcon(paths.get_art_filepath("clownLogo.png")))
        self.setVisible(True) 

        # Create trayMenu
        trayMenu = QtWidgets.QMenu()

        self.actionToggleWindowVisibility = QtWidgets.QAction("Show", self) 
        self.actionClose = QtWidgets.QAction(self.main_window.style().standardIcon(QtWidgets.QStyle.SP_TitleBarCloseButton), "Close", self) 
        trayMenu.addAction(self.actionToggleWindowVisibility) 
        trayMenu.addAction(self.actionClose) 

        self.actionToggleWindowVisibility.triggered.connect(self.toggleWindowVisibility)
        self.actionClose.triggered.connect(self.close)

        self.activated.connect(self.toggleWindowVisibility)

        self.setToolTip("ClOwn-Mails")

        self.setContextMenu(trayMenu)

        self.showMessage(
            "ClOwn-Mails",
            "ClOwn-Mails now actively deletes emails",
            QtWidgets.QSystemTrayIcon.Information,
            4000
        )

    def toggleWindowVisibility(self):
        if self.main_window.isVisible():
            logger.info("Closing main window...")
            self.main_window.hide()
            self.actionToggleWindowVisibility.setText("Show")
            self.setVisible(True)
        else:
            logger.info("Showing main window...")
            self.main_window.showNormal()
            self.actionToggleWindowVisibility.setText("Hide")
            self.setVisible(True)

    def close(self):
        self.main_window.quit()
