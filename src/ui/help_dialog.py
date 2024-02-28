from PyQt5 import QtWidgets, uic, QtGui

from utils import paths

import logging
logger = logging.getLogger(__name__)

class HelpDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi(paths.get_ui_filepath("help_dialog.ui"), self)
        self.setWindowIcon(QtGui.QIcon(paths.get_art_filepath("icon.png")))