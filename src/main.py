#!/usr/bin/env python3

import sys, os, argparse
from PyQt5 import QtWidgets
from ui import MainWindow
from utils import paths

# parse commandline
parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description="ClOwn-Mails")
parser.add_argument("--log", metavar='LOGLEVEL', help="Loglevel to log", default="DEBUG")
args = parser.parse_args()

os.makedirs(paths.user_data_dir(), exist_ok=True)
os.makedirs(paths.user_log_dir(), exist_ok=True)
os.makedirs(paths.user_cache_dir(), exist_ok=True)

import json, logging, logging.config
try:
    with open(paths.get_conf_filepath("logger.json"), 'r') as logging_configuration_file:
        logger_config = json.load(logging_configuration_file)
except:
    with open(paths.get_default_conf_filepath("logger.json"), 'rb') as fp:
        logger_config = json.load(fp)
    with open(paths.get_conf_filepath("logger.json"), 'w+') as fp:
        json.dump(logger_config, fp)
logger_config["handlers"]["stderr"]["level"] = args.log
logging.config.dictConfig(logger_config)
logger = logging.getLogger(__name__)
logger.info('Logger configured...')

app = QtWidgets.QApplication(sys.argv)

# initialize gui
from ui import TrayIcon, MainWindow
window = MainWindow()
tray_icon = TrayIcon(window)
window.tray_icon = tray_icon
tray_icon.show()
# show and hide again to properly initialize it (we sometimes get an empty window otherwise)
window.show()
window.hide()

# run qt mainloop
app.exec_()