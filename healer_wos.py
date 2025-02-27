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
def skip_shit_and_start_game(android:AndroidTouchControl|None, shutdown = True):
    if android is None:
        print('Failed to connect, try reconnecting devie if it has happened before')
        print('I kill this process in 5 seconds')
        time.sleep(5)
        exit()

    if shutdown:
        android._run_adb(*'shell am force-stop com.gof.global'.split())
        time.sleep(2)
    android._run_adb('shell','monkey','-p','com.gof.global','-c','android.intent.category.LAUNCHER','1')
    # android.tap(670,70)
    logging.info('Waiting for game to load up')
    if (n:=android.wait_for_image(os.path.join((os.path.abspath('')),'template_images','Confirm Button.png'),
                           timeout=15)):
        android.tap(*n)
    elif (n:=android.wait_for_image(os.path.join((os.path.abspath('')),'template_images','World.png'),
                           timeout=5)):
        # android.tap(*n)
        pass
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
    skip_shit_and_start_game(android)
# adb shell monkey -p com.gof.global -c android.intent.category.LAUNCHER 1
    # android._run_adb('shell','monkey','-p','com.gof.global','-c','android.intent.category.LAUNCHER','1')
    # android.tap(670,70)
    logging.info('Waiting for game to load up')
    try:
        number = int(input('Enter the number of troops you want to heal: '))
        reset_number = input('Type y if you want to be able to change number in the middle, anything else otherwise: ')
    except ValueError as e:
        print('Bruh you are supposed to add number that I can type in...')
        print('Never mind man I commit seppuku')
        time.sleep(5)
        exit()
    reset_number = reset_number.lower().startswith('y')
    limit, setupnumber = 0, True
    android.click_on_image('template_images\\World.png')
    # android.find_template('template_images\\Heal Frame.png',threshold=0.7)
    # android.find_template('template_images\\Frame Location.png','screen_heal_click.png')
    while True:
        if (m:=android.wait_for_image('template_images\\Quick Heal Btn.png',timeout=3)):
            healer(android, number, m, setupnumber)
            setupnumber = False
            limit+=1
            if limit>10:
                limit=0
                setupnumber = True
                if reset_number:
                    number = input('Reset number: ')
        elif  android.click_on_image(os.path.join((os.path.abspath('')),'template_images','Help.png')):
            if (m:=android.wait_for_image(os.path.join((os.path.abspath('')),'template_images','Back Btn.png'),
                           timeout=3)):
                android.tap(*m)
        else:
            coords = WoS_locations['end_swipe']['x2'], WoS_locations['end_swipe']['y2'], WoS_locations['end_swipe']['x1'], WoS_locations['end_swipe']['y1']
            time.sleep(0.3)
            android.swipe(*coords)
    logging.info('Bruh we done')

def healer(android, number, m, setup_numbers = False):
    logging.info('Need to heal troops')
    android.tap(*m)

    if setup_numbers:
        if (n:=android.wait_for_image('template_images\\Quick Select.png')):
            for i in range(3):
                android.tap(*n)
                time.sleep(0.6)
            coords = WoS_locations['heal_1']['x'],WoS_locations['heal_1']['y']
            android.tap(*coords)
            time.sleep(1)
            android._run_adb('shell','input','text',f'{number}'[0])
            android._run_adb('shell','input','text',f'{number}'[1:])
            android._run_adb('shell','input','keyevent','66')
            time.sleep(1)
            coords = WoS_locations['heal_2']['x'],WoS_locations['heal_2']['y']
            android.tap(*coords)
            time.sleep(0.5)
            android._run_adb('shell','input','text',f'{number}'[0])
            android._run_adb('shell','input','text',f'{number}'[1:])
            android._run_adb('shell','input','keyevent','66')
            time.sleep(1)
            coords = WoS_locations['heal_3']['x'],WoS_locations['heal_3']['y']
            android.tap(*coords)
            time.sleep(1)
            android._run_adb('shell','input','text',f'{number}'[0])
            android._run_adb('shell','input','text',f'{number}'[1:])
            android._run_adb('shell','input','keyevent','66')
            time.sleep(0.5)
        # pdb.set_trace()
    android.click_on_image('template_images\\Heal.png')
    android.click_on_image('template_images\\Ask Help.png')
    coords = WoS_locations['end_swipe']['x1'], WoS_locations['end_swipe']['y1'], WoS_locations['end_swipe']['x2'], WoS_locations['end_swipe']['y2']
    time.sleep(0.3)
    android.swipe(*coords)

if __name__ == '__main__':
    main()
