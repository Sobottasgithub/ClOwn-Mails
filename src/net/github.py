import os, sys
import platform
import shutil
import subprocess
import requests
from packaging import version
from collections import defaultdict

from utils import paths
from utils.version import VERSION, GITHUB_USER, GITHUB_PROJECT

import logging
logger = logging.getLogger(__name__)

class Github():
    def __init__(self):
        super().__init__()

    def hasUpdate(self):
        if VERSION == "Bleeding edge (master branch)":
            return False
        
        # Get current version
        logger.info("Get current version")
        currentVersion = version.parse(VERSION)

        # Get latest version
        logger.info("Get latest version")
        latestVersion = self.fetchRelease().json()["tag_name"]

        # return if update is available
        logger.info("Return state")
        if version.parse(latestVersion) == currentVersion:
            return False
        return True
    
    def downloadUpdate(self):
        # Get right application format
        system2filename = defaultdict(lambda: "ClOwn-Mails", {
            "Windows": "ClOwn-Mails.exe",
            "Darwin": "ClOwn-Mails.dmg",
            "Linux": "ClOwn-Mails",
        })
        systemName = system2filename[platform.system()]
        asset = [asset for asset in self.fetchRelease().json()["assets"] if asset["name"] == systemName][0]

        # Download new executable
        path = os.path.join(paths.user_cache_dir(), asset["name"])
        url = asset["browser_download_url"]

        logger.info("Downloading executable...")
        with requests.get(url, stream=True, timeout=2) as response:
            response.raise_for_status()
            with open(path, 'wb') as folder:
                for chunk in response.iter_content(chunk_size=None):
                    if chunk: 
                        folder.write(chunk)
        logger.info("Download complete...")

        # don't auto-replace if not using packaged executable
        if not (getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')):
            raise Exception("Bitte Update manuell von hier installieren: %s" % path)

        # auto-replace executable, if possible (on darwin only open dmg file)
        if platform.system() == "Windows":
            logger.info("Renaming currently running executable to '%s.bak' and spawn newly downloaded executable at '%s'..." % (sys.executable, sys.executable))
            os.replace(sys.executable, "%s.bak" % sys.executable)
            shutil.copy2(path, sys.executable)
            cmds = [sys.executable] + sys.argv + ["--replace"]
            subprocess.Popen(cmds, start_new_session=True)
            logger.info("Spawned newly downloaded executable at '%s' with '--replace'..." % sys.executable)
        elif platform.system() == "Darwin":
            logger.info("Opening newly downloaded dmg file at '%s' and showing alert to user..." % path)
            os.system("open %s" % path)
            raise Exception("Bitte Update manuell von hier installieren: %s" % path)
        else:
            logger.info("Replacing currently running executable at '%s' and respawning..." % sys.executable)
            shutil.copy2(path, sys.executable)
            cmds = [sys.executable] + sys.argv + ["--replace"]
            logger.info("CMDs: %s" % str(cmds))
            subprocess.Popen(cmds, start_new_session=True)

    def fetchRelease(self):
        response = requests.get("https://api.github.com/repos/%s/%s/releases/latest" % (GITHUB_USER, GITHUB_PROJECT), timeout=2)
        if response.status_code != 200:
            logger.error("Failed to fetch latest release metadata from github", response.status_code)
        return response

