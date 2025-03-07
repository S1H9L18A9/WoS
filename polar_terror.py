# from ..ChefLive.minitouch import AndroidTouchControl
import pdb
from Android_control.minitouch import AndroidTouchControl
from Android_control.visualize_matches import find_images_in_screenshot
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
current_dir = os.path.abspath('')
join_path = os.path.join
path_for = lambda x:((join_path(current_dir,*x)) if type(x) is list else (join_path(current_dir,x)))

static_points = {
    'points':{
        'recorded_at_720x1520':{
            'recorded': (720,1520),
            
        }
    },}
static_paths={
        'world': path_for(['template_images','World.png']),
        'intel_button': path_for(['template_images','Intel Button.png']),
        'attack': path_for(['template_images','Attack.png']),
        'likely': path_for(['template_images','deploy_likely.png']),
        'anywhere_skip': path_for(['template_images','Tap Anywhere.png']),
        'deploy': path_for(['template_images','Deploy.png']),
        'intel': path_for(['template_images','Intel']),
        'rescue': path_for(['template_images','Intel','Intel Rescue.png']),
        'explore': path_for(['template_images','Intel','Intel Explore.png']),
        'view': path_for(['template_images','Intel','Intel View.png']),
        'fight': path_for(['template_images','Intel','Squad Fight.png']),
        'fight_skip': path_for(['template_images','Intel','Squad Tap Anywhere to Exit.png']),
    }

def main():
    print('-'*50)
    logging.info('Info')

    logging.info('Connecting to game')
    
    # AndroidTouchControl.find_devices()
    android = AndroidTouchControl.connect_to_first_device(verify=False)
    # android.find_template('template_images\\Frame Location.png','screen_help_avail.png')

    # android.get_device_architecture()  # Automatically detects device architecture
    # android.push_minitouch()  # Pushes the appropriate binary to the device
    # android.start_minitouch()  # Starts the minitouch service
    logging.info('Starting WoS')
# adb shell monkey -p com.gof.global -c android.intent.category.LAUNCHER 1
# adb shell am force-stop com.gof.global

    skip_shit_and_start_game(android, shutdown = False)
    logging.info('Ideally now I am in game')
    # pdb.set_trace()
    #switch to the world map
    if (m:=android.wait_for_image(os.path.join((os.path.abspath('')),'template_images','World.png'),
                           timeout=5)):
        logging.info('Not on World map, going there')
        android.tap(*m)

    if (intel_button:=android.wait_for_image(os.path.join((os.path.abspath('')),'template_images','Intel Button.png'),
                           timeout=2)):
        logging.info('found intel, going there')
        android.tap(*intel_button)
        time.sleep(1)
        # results = find_images_in_screenshot('template_images\\Intel',[android.take_screenshot()],0.9,True)
        results = find_images_in_screenshot(static_paths['intel'],[android.take_screenshot()],0.9,True,21)
        results = results['screen.png']
        pdb.set_trace()
        results.sort(key=lambda x: x['probability'], reverse = True)
        # results.sort(key=lambda x: x['seed_path'])

        for intel in results:
            android.tap(*intel['position'])
            if (m:=android.wait_for_image(static_paths['view'],2)):
                logging.info('Active intel')
                android.tap(*m)
                if (m:=android.wait_for_image(static_paths['rescue'],5)):
                    logging.info('Rescue mission, no need to pause')
                    android.tap(*m)
                    time.sleep(1)
                    android.tap(*intel_button)
                    time.sleep(0.5)
                elif (m:=android.wait_for_image(static_paths['explore'],2)):
                    logging.info('Explore mission, no need to pause')
                    android.tap(*m)
                    if (m:=android.wait_for_image(static_paths['fight'],5)):
                        android.tap(*m)
                        if (m:=android.wait_for_image(static_paths['fight_skip'],15)):
                            android.tap(*m)
                            logging.info('Exploration complete')
                            time.sleep(1)
                            android.tap(*intel_button)
                            time.sleep(0.5)
                            continue
                    logging.info('Something went wrong, aborting')
                    break
                elif (m:=android.wait_for_image(static_paths['attack'],2)):
                    android.tap(*m)
                    time.sleep(0.5)
                    if android.wait_for_image(static_paths['likely'], 5):
                        logging.info('Deployment likely to succeed')
                        #possibly add code here for hero selection
                        android.click_on_image(static_paths['deploy'])
                        #need to write code here for when deployment fails, due to no stamina maybe
                        time.sleep(0.5)
                        #Reset back to intel page
                        android.click_on_image(static_paths['intel_button'])
                        time.sleep(0.5)
                        break
            elif (m:=android.wait_for_image(static_paths['anywhere_skip'],2)):
                android.tap(*m)
            else:
                print('Program has crashed, it should not be here')
                logging.info('Program should not be here. Or it is a manifestation on laziness on the part of the coder')
                logging.info('Edge cases are hard')
                pdb.set_trace()

            # if 'hunting' in intel['seed_path'].lower():
            #     time.sleep(0.5)
            #     android.click_on_image(static_paths['view'])
            #     time.sleep(0.5)
            #     android.click_on_image(static_paths['attack'])
            #     time.sleep(0.5)
            #     if android.wait_for_image(static_paths['likely'], 5):
            #         logging.info('Deployment likely to succeed')
            #         #possibly add code here for hero selection
            #         android.click_on_image(static_paths['deploy'])
            #         #need to write code here for when deployment fails, due to no stamina maybe
            #         time.sleep(0.5)
            #         #Reset back to intel page
            #         android.click_on_image(static_paths['intel_button'])
            #         time.sleep(0.5)
            # elif 'check' in intel['seed_path'].lower():
            #     android.tap(*intel['position'])
            #     if (m:=android.wait_for_image(static_paths['anywhere_skip'])):
            #         android.tap(*m)
            # else:
            #     android.tap(*intel['position'])
            #     time.sleep(0.5)
            #     android.tap(375,1050)
            #     time.sleep(1)
            #     android.tap(360,800)
            #     time.sleep(1)
            #     android.tap(540,1460)
            #     time.sleep(1)
            #     android.tap(*intel_button)
            #     time.sleep(1)
        #375, 1050 to click view - image name View.png
        #360, 800 to click attack, save
        #540, 1460 to deploy, need to check if I still have tuna

    logging.info('Helping perpetually')
    while True:
        if  android.click_on_image(os.path.join((os.path.abspath('')),'template_images','Help.png')):
            if (m:=android.wait_for_image(os.path.join((os.path.abspath('')),'template_images','Back Btn.png'),
                           timeout=3)):
                android.tap(*m)
    logging.info('Bruh we done')

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
    elif (n:=android.wait_for_image(os.path.join((os.path.abspath('')),'template_images','Exploration.png'),
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
            elif (m:=android.wait_for_image(os.path.join((os.path.abspath('')),'template_images','Exploration.png'),
                           timeout=3)):
                break
        else:
            if (m:=android.wait_for_image(os.path.join((os.path.abspath('')),'template_images','Exploration.png'),
                           timeout=3)):
                logging.info('Finally in game....I think')
            else:
                logging.info('Game blocked me, gege')
                time.sleep(5)
                exit()

if __name__ == '__main__':
    main()
