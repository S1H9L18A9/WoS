# from ..ChefLive.minitouch import AndroidTouchControl
import pdb
from Android_control.minitouch import AndroidTouchControl

import logging
import logging.config
import time
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
    # android.tap(670,70)
    logging.info('Waiting for game to load up')
    if (n:=android.wait_for_image(os.path.join((os.path.abspath('')),'template_images','Confirm Button.png'),
                           timeout=15)):
        android.tap(*n)
    else:
        logging.info('I am being sold some random junk, need to get out')
        for i in range(3):
            android.tap(670+i*10,70)
            if (m:=android.wait_for_image(os.path.join((os.path.abspath('')),'template_images','Confirm Button.png'),
                           timeout=3)):
                      
                android.tap(*m)
                break
            elif (m:=android.wait_for_image(os.path.join((os.path.abspath('')),'template_images','World.png'),
                           timeout=3)):
                break
        else:
            if (m:=android.wait_for_image(os.path.join((os.path.abspath('')),'template_images','World.png'),
                           timeout=3)):
                logging.info('Finally in game....I think')
            else:
                logging.info('Game blocked me, gege')
                time.sleep(5)
                exit()
    logging.info('Ideally now I am in game')
    logging.info('Helping perpetually')
    while True:
        if  android.click_on_image(os.path.join((os.path.abspath('')),'template_images','Help.png')):
            if (m:=android.wait_for_image(os.path.join((os.path.abspath('')),'template_images','Back btn.png'),
                           timeout=3)):
                android.tap(*m)
    logging.info('Bruh we done')

if __name__ == '__main__':
    main()
