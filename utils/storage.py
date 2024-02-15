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
    
    def __setitem__(self, key, value):
        self.data[key] = value
        self._store()  

    def __getitem__(self, key):
        if not key in self.data:
            return None
        return self.data[key]
    
    def __delitem__(self, key):
        if not key in self.data:
            return
        del self.data[key]
        self._store()    # automatically save on change
    
    def __len__(self):
        return len(self.data)

    def _load(self):
        logger.info("Loading default'...")
        defaults = {"data": {}}
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
