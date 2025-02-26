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
WoS_locations = {
    'heal_1': {
        'type':'tap',
        'recorded_max_x':720,
        'recorded_max_y':1520,
        'x':550,
        'y':650,
    },
    'heal_2': {
        'type':'tap',
        'recorded_max_x':720,
        'recorded_max_y':1520,
        'x':550,
        'y':780,
    },
    'heal_3': {
        'type':'tap',
        'recorded_max_x':720,
        'recorded_max_y':1520,
        'x':550,
        'y':930,
    },
    'end_swipe': {
        'type':'swipe',
        'recorded_max_x':720,
        'recorded_max_y':1520,
        'x1':360,
        'y1':330,
        'x2':360,
        'y2':300,
    },
}


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
    # android._run_adb('shell','monkey','-p','com.gof.global','-c','android.intent.category.LAUNCHER','1')
    # android.tap(670,70)
    logging.info('Waiting for game to load up')
    android.find_template('template_images\\Heal Frame.png',threshold=0.7)
    # android.find_template('template_images\\Frame Location.png','screen_heal_click.png')
    if (m:=android.wait_for_image('template_images\\Quick Heal Btn.png')):
        logging.info('Need to heal troops')
        android.tap(*m)
        if (n:=android.wait_for_image('template_images\\Quick Select.png')):
            for i in range(3):
                android.tap(*n)
                time.sleep(0.6)
            coords = WoS_locations['heal_1']['x'],WoS_locations['heal_1']['y']
            android.tap(*coords)
            time.sleep(1)
            android._run_adb('shell','input','text','1')
            android._run_adb('shell','input','keyevent','66')
            time.sleep(1)
            coords = WoS_locations['heal_2']['x'],WoS_locations['heal_2']['y']
            android.tap(*coords)
            time.sleep(1)
            android._run_adb('shell','input','text','1')
            android._run_adb('shell','input','keyevent','66')
            time.sleep(1)
            coords = WoS_locations['heal_3']['x'],WoS_locations['heal_3']['y']
            android.tap(*coords)
            time.sleep(1)
            android._run_adb('shell','input','text','1')
            android._run_adb('shell','input','keyevent','66')
            time.sleep(1)
            android.click_on_image('template_images\\Heal.png')
            android.click_on_image('template_images\\Ask Help.png')
            coords = WoS_locations['end_swipe']['x1'], WoS_locations['end_swipe']['y1'], WoS_locations['end_swipe']['x2'], WoS_locations['end_swipe']['y2']
            time.sleep(0.3)
            android.swipe(*coords)
            
    logging.info('Bruh we done')

if __name__ == '__main__':
    main()
