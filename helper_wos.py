# from ..ChefLive.minitouch import AndroidTouchControl
import pdb
from Android_control.minitouch import AndroidTouchControl

import logging
import logging.config

import pandas as pd
import requests
import zipfile
import io
import pandas as pd
import requests
import os
logging.config.fileConfig(os.path.join(os.path.abspath(''),'Logger','logger_config.ini'))
# import importlib.util

# file_path = "/path/to/your/script.py"  # Update with your actual path
# module_name = "your_script"

# spec = importlib.util.spec_from_file_location(module_name, file_path)
# module = importlib.util.module_from_spec(spec)
# spec.loader.exec_module(module)


def main():
    print('-'*50)
    logging.info('Info')

    logging.info('Connecting to game')
    pdb.set_trace()
    
    # AndroidTouchControl.find_devices()
    android = AndroidTouchControl.connect_to_first_device(verify=False)

    # android.get_device_architecture()  # Automatically detects device architecture
    # android.push_minitouch()  # Pushes the appropriate binary to the device
    # android.start_minitouch()  # Starts the minitouch service
    logging.info('Starting WoS')
# adb shell monkey -p com.gof.global -c android.intent.category.LAUNCHER 1
    android._run_adb('shell','monkey','-p','com.gof.global','-c','android.intent.category.LAUNCHER','1')
    # android.tap(700,100)
    
    android.click_on_image(os.path.join((os.path.abspath('')),'template_images','Help.png'))
    logging.info('Bruh we done')

if __name__ == '__main__':
    main()