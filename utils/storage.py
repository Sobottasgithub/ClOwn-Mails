import json
from utils import paths

import logging
logger = logging.getLogger(__name__)

class StorageSingleton():
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StorageSingleton, cls).__new__(cls)
            cls._instance.path = paths.get_conf_filepath("preferences.json")
            cls._instance._load()
            logger.debug("Instanciated SettingsSingleton...")
        return cls._instance

    def getListSize(self):
        return len(self.data)
    
    def setData(self, data):
        self.data.clear()
        self.data = data
        self._store()

    def getDataAtIndex(self, index):
        return self.data[index]

    def _load(self):
        logger.info("Loading default'...")
        defaults = []
        try:
            logger.info("Loading storage from '%s'..." % self.path)
            with open(self.path, 'rb') as fp:
                self.data = json.load(fp)

        except:
            logger.info("File not loadable or does not exist: '%s', loading default list." % self.path)
            self.data = defaults
            with open(self.path, 'w+') as fp:
                json.dump(self.data, fp)

    def _store(self):
        with open(self.path, 'w') as fp:
            json.dump(self.data, fp)
