import ctypes
import hashlib
import logging
import os
import requests
import shutil
import sys
import time
import winreg
from zipfile import ZipFile

APPDIR = os.path.join(os.environ['PROGRAMFILES'], 'image-resize')
PACKAGE_URL = "https://rcl-published.s3-eu-west-1.amazonaws.com/image_resize.zip"
PACKAGE_FILE = os.path.join(os.environ['TEMP'], "image-resize.zip")
PACKAGE_SHA256 = "69bd74abcccec5ea3a009f4c75e0cc39503f0535dde758ceda748033049ca459"

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if __name__ == "__main__":
    # Make sure code is run as admin
    if not is_admin():
        # Create install directory and set up logging
        try:
            os.mkdir(APPDIR)
            logging.basicConfig(level=logging.DEBUG, filename=os.path.join(APPDIR, "resize.log"))
        except Exception:
            # If creation of directory fails then just log to stdout
            logging.basicConfig(level=logging.DEBUG)
        # Download package
        with requests.get(PACKAGE_URL, stream=True) as r:
            with open(PACKAGE_FILE, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
        # Validate package
        package_hash = hashlib.sha256()
        with open(PACKAGE_FILE, 'rb') as f:
            while True:
                data = f.read(6400)  # SHA256 has 64 bit chunk size of which we read 100 at a time
                if not data:
                    break
                package_hash.update(data)
        logging.info(f"package hash is {package_hash.hexdigest()}")
        if package_hash.hexdigest() != PACKAGE_SHA256:
            logging.critical(f"Package hash does not match expected value {PACKAGE_SHA256}, Aborting installation")
            sys.exit(1)
        # Put files in right place
        with ZipFile(PACKAGE_FILE) as zf:
            zf.extractall(path=APPDIR)
        # clean up downloads
        os.remove(PACKAGE_FILE)
        # Add registry key for context menu
        winreg.SetValue(
            winreg.HKEY_CLASSES_ROOT, r"*\shellex\ContextMenuHandlers\resize", 
            winreg.REG_SZ, 
            "{} %1".format(os.join(APPDIR, 'resize.exe'))
        )
    else:
        # Run this script as admin
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
