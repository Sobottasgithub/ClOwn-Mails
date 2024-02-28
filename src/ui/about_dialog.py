from PyQt5 import QtWidgets, uic, QtGui

from utils import paths
from utils.version import VERSION

import logging
logger = logging.getLogger(__name__)

class AboutDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi(paths.get_ui_filepath("about_dialog.ui"), self)
        self.setWindowIcon(QtGui.QIcon(paths.get_art_filepath("icon.png")))
        self.uiLabel_version.setText(VERSION)
        self.uiLabel_configDir.setText(paths.user_data_dir())
