#!/usr/bin/env python3

import sys, os
from PyQt5 import QtWidgets
from ui import MainWindow
from utils import paths

import logging
logger = logging.getLogger(__name__)
logger.info('Logger configured...')

os.makedirs(paths.user_data_dir(), exist_ok=True)

app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()