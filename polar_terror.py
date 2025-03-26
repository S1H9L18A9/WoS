# from ..ChefLive.minitouch import AndroidTouchControl
from datetime import datetime
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
            'dpi':420,
            'back': (45,100),
            
        }
    },}
static_paths={
        'world': path_for(['template_images','World.png']),
        'exploration': path_for(['template_images','Exploration.png']),
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
        
        'search': path_for(['template_images','Search']),
        'magnifyer': path_for(['template_images','Search','Magnifyer New.png']),
        'polar': path_for(['template_images','Search','Polar Terror.png']),
        'search_btn': path_for(['template_images','Search','Search.png']),
        'rally': path_for(['template_images','Search','Rally.png']),
        'hold_rally': path_for(['template_images','Search','Hold Rally.png']),

        'hero': path_for(['template_images','Hero List']),
        'hero_infantry': path_for(['template_images','Hero List','Infantry']),
        'hero_lancer': path_for(['template_images','Hero List','Lancer']),
        'hero_marksman': path_for(['template_images','Hero List','Marksman']),
        'gina': path_for(['template_images','Hero List','Marksman','Gina.png']),
        
        'mer_folder': path_for(['template_images','Mercenary Prestige']),
        'merc_icon': path_for(['template_images','Mercenary Prestige','Merc Prestige Quick Btn.png']),
        'merc_icon2': path_for(['template_images','Mercenary Prestige','Quick.png']),
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

    pdb.set_trace()
    
    skip_shit_and_start_game(android, shutdown = False)
    logging.info('Ideally now I am in game')
    #switch to the world map
    func_dict = {
        # 'merc':{'func':mercenary,'args':[android],'kwargs':{},'cooldown':150,'last_run':None},
        'help':{'func':helper, 'args':[android],'kwargs':{'default_timeout':2},'cooldown':0,'last_run':None},
        'tuna_eater':{'func':tuna_eater, 'args':[android],'kwargs':{},'cooldown':200,'last_run':None},
        # 'help':{'func':helper, 'args':[android],'kwargs':{'default_timeout':2},'cooldown':0,'last_run':0},
    }

    logging.info('Helping perpetually')
    while True:
        # pdb.set_trace()
        # hero_selector(android)
        # tuna_eater(android)
        # hunter(android)
        for task in func_dict.items():
            if (not task[1]['last_run']) or ((datetime.now() - task[1]['last_run']).total_seconds() > task[1]['cooldown']):
                if not task[0].lower().startswith('help'):
                    logging.info(f'Doing task: {task[0]}')
                try:
                    result = task[1]['func'](*task[1]['args'],**task[1]['kwargs'])
                    if  type(result) is tuple:
                        task[1].update(result[1])
                    task[1]['last_run'] = datetime.now()
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    logging.info(f'Error on {task[0]} : {e}')
            else:
                # logging.info(f'Skipping {task[0]}')
                pass
            
        # for i in range(30):
            # helper(android)
            # time.sleep(1)
    logging.info('Bruh we done')


def mercenary(android:AndroidTouchControl):
    # pdb.set_trace()
    if (icon:=android.wait_for_image(static_paths['merc_icon2'])):
        android.tap(*icon)
        time.sleep(1)
        android.click_on_image(path_for([static_paths['mer_folder'],'Scout.png']),)
        if (m:=android.wait_for_image(path_for([static_paths['mer_folder'],'Attack.png']),10)):
            android.tap(*m)
            time.sleep(1)
            hero_selector(android,select_gina=True)
            if android.wait_for_image(static_paths['likely'], 5):
                logging.info('Deployment likely to succeed')
                # hero_selector(android,select_gina=True)
                #possibly add code here for hero selection
                android.click_on_image(static_paths['deploy'])
                #need to write code here for when deployment fails, due to no stamina maybe
                time.sleep(0.5)
                #Reset back to intel page
                # android.click_on_image(static_paths['intel_button'])
                time.sleep(0.5)
                # break
                return 0
            else:
                pdb.set_trace()
                logging.info('Deployment not likely to succeed. Let us rally')
                android._run_adb('shell','input','keyevent','4')
                # android.tap(*static_points['points']['recorded_at_720x1520']['back'])
                time.sleep(1)
                android.tap(*icon)

                if (m:=android.wait_for_image(static_paths['rally'],timeout=10)):#convert to wait if statement coz maybe you don't find any 
                    android.tap(*m)
                    time.sleep(1)
                    #add rally time stuff here, I guess
                    android.click_on_image(static_paths['hold_rally'])
                    #probably add the hero selection here
                    hero_selector(android,select_gina=True)
                    
                    if (m:=android.wait_for_image(static_paths['deploy'],timeout=10)):
                    #wait for exploration here coz there maybe someone else is marching towards the target. 
                        # Key press 4 puts you back. Better than 
                        # android._run_adb('shell','input','keyevent','4')
                    # Wait 10 sec, then back button till exploration visible
                        android.tap(*m)
                        if (m:=android.wait_for_image(static_paths['exploration'],5)):
                            return 0
                        else:
                            logging.info('Looks like there is no tuna, or something else went wrong')
                            logging.info('Something is the best you have, I am lazy')
                            logging.info('Trying to go back')
                            for i in range(4):
                                android._run_adb('shell','input','keyevent','4')
                                if (m:=android.wait_for_image(static_paths['exploration'],1)):
                                    return 1
                            else:
                                logging.info('Backing up failed. Reset-game time')
                                skip_shit_and_start_game(shutdown=True)
#         (555, 1088)
# (Pdb) android.wait_for_image(path_for([static_paths['mer_folder'],'Attack.png']))
# (460, 1201)
# (Pdb) android.tap(460,1201)
# (Pdb) back_btn
# *** NameError: name 'back_btn' is not defined
# (Pdb) android.tap(555,1088)
# (Pdb) android.wait_for_image(path_for([static_paths['mer_folder'],'Rally.png']))
# (259, 1200)
# (Pdb) android.tap(259,1200)
# (Pdb) hold rally{}
    else:
        logging.info('Merc icon not found, remember you need the quick btn to use this')


def hero_selector(android:AndroidTouchControl, select_gina = False, select_bokhan = False, select_meat = False, select_wood = False , select_iron = False,**kwargs):
    current_heroes = {}
    for type in ('infantry','lancer','marksman'):
        results = find_images_in_screenshot(static_paths[f'hero_{type}'],[android.take_screenshot()],0.9,True)['screen.png']
        if len(results):
            current_heroes[type] = results
    if select_gina:
        if 'gina' not in current_heroes['marksman'][0]['seed_path'].lower():
            android.tap(*current_heroes['marksman'][0]['position'])
            time.sleep(1)
            # android.tap(510,1150)
            time.sleep(1)
            android.click_on_image(static_paths['gina'])
            android.tap(510,1150)
            time.sleep(1)
            android.tap(550,1450)
            time.sleep(0.5)
        return


def tuna_eater_wrapper(android:AndroidTouchControl,**kwargs):
    func_list = [
        {'name':'tuna_eater','func':tuna_eater, 'args':[android],'kwargs':{},'cooldown':200,},
        {'name':'mercenary','func':mercenary, 'args':[android],'kwargs':{},'cooldown':100,},
        {'name':'hunter','func':hunter, 'args':[android],'kwargs':{},'cooldown':200,},
        # 'merc':{'func':mercenary,'args':[android],'kwargs':{},'cooldown':150,'last_run':None},
    ]
    if not (index:=kwargs.get('task')):
        task = func_list[index]
    else:
        task = func_list[0]
    # logging.info('Helping perpetually')
    # while True:
    #     # pdb.set_trace()
    #     # hero_selector(android)
    #     # tuna_eater(android)
    #     # hunter(android)
        # for task in func_dict.items():
        #     if (not task[1]['last_run']) or ((datetime.now() - task[1]['last_run']).total_seconds() > task[1]['cooldown']):
        #         if not task[0].lower().startswith('help'):
        #             logging.info(f'Doing task: {task[0]}')
    result = task['func'](*task['args'],**task['kwargs'])
    if type(result) is int:
        if result:
            if result == 2: 
                #I decided result 2 will be when no images found in intel
                if (counter:= kwargs.get('found_no_intel_counter')):
                    if counter >2:
                        return 0, {'kwargs':{**kwargs,'task':1}}
                    return 0, {'kwargs':{'found_no_intel_counter':counter+1},'cooldown': 60}
                else:
                    return 0, {'kwargs':{**kwargs},'cooldown': task['cooldown']}
        else:
            return 0,{'cooldown':task['cooldown']}

def tuna_eater(android:AndroidTouchControl, **kwargs):
    if (intel_button:=android.wait_for_image(os.path.join((os.path.abspath('')),'template_images','Intel Button.png'),
                           timeout=2)):
        logging.info('found intel, going there')
        android.tap(*intel_button)
        time.sleep(1)
        if (android.wait_for_image(path_for(['template_images','Intel cans.png']),5)):
            # results = find_images_in_screenshot('template_images\\Intel',[android.take_screenshot()],0.9,True)
            results = find_images_in_screenshot(static_paths['intel'],[android.take_screenshot()],0.9,True,21)
            results = results['screen.png']
            #if results are 0, need to go to polar terror section
            if len(results):
                # pdb.set_trace()
                results.sort(key=lambda x: x['probability'], reverse = True)
                # results.sort(key=lambda x: x['seed_path'])
                backtrack_index = 0
                for intel in results:
                    android.tap(*intel['position'])
                    if (m:=android.wait_for_image(static_paths['view'],5)):
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
                            logging.info('Most likely no tuna')
                            for i in range(4):
                                android._run_adb('shell','input','keyevent','4')
                                if (m:=android.wait_for_image(static_paths['exploration'],1)):
                                    return 1
                            else:
                                skip_shit_and_start_game(android)
                                return 1
                        elif (m:=android.wait_for_image(static_paths['attack'],2)):
                            android.tap(*m)
                            time.sleep(0.5)
                            if android.wait_for_image(static_paths['likely'], 5):
                                logging.info('Deployment likely to succeed')
                                hero_selector(android,select_gina=True)
                                #possibly add code here for hero selection
                                android.click_on_image(static_paths['deploy'])
                                if (m:=android.wait_for_image(static_paths['exploration'],3)):
                                    logging.info('Deployment successful')
                                    return 0
                                else:
                                    logging.info('Looks like there is issue in deploying')
                                    for i in range(4):
                                        android._run_adb('shell','input','keyevent','4')
                                        if (m:=android.wait_for_image(static_paths['exploration'],1)):
                                            return 1
                                    else:
                                        skip_shit_and_start_game(android)
                                        return 1

                                #need to write code here for when deployment fails, due to no stamina maybe
                                time.sleep(0.5)
                                #Reset back to intel page
                                # android.click_on_image(static_paths['intel_button'])
                                time.sleep(0.5)
                                # break
                                return 0
                    elif (m:=android.wait_for_image(static_paths['anywhere_skip'],2)):
                        logging.info('A completed intel, claiming rewards and keep going')
                        android.tap(*m)
                        backtrack_index += 1
                    elif 'check' in intel['seed_path'].lower():
                        logging.info('A check mark detected, ideally this was after anywhere skip. Continuing')
                    else:
                        logging.info('Did not fit any criteria. Maybe a completed intel?')
                        if backtrack_index:
                            backtrack_index -= 1
                        else:
                            print('Program has crashed, it should not be here')
                            logging.info('Program should not be here. Or it is a manifestation on laziness on the part of the coder')
                            logging.info('Edge cases are hard')
                            # break
                            return 1
                            # pdb.set_trace()

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
                else:
                    pdb.set_trace()
                    logging.info('Looks like intel is done, time for polar terror')
                    android.tap(*static_points['points']['recorded_at_720x1520']['back'])
                    hunter(android)
                    return 0#, {'func':hunter}
                
            #375, 1050 to click view - image name View.png
            #360, 800 to click attack, save
            #540, 1460 to deploy, need to check if I still have tuna
            else:
                pdb.set_trace()
                logging.info('No intel found, going for polar')
                android.tap(*static_points['points']['recorded_at_720x1520']['back'])
                if (m:=kwargs.get('nothing_found_count')):
                    if m >3: # type: ignore
                        return 0, {'func':hunter, 'cooldown':360}
                    return 0,{'kwargs':{'nothing_found_count':m+1}} # type: ignore
                else:
                    return 0, {'kwargs':{'nothing_found_count':1}}
        else:
            logging.info('Tried clicking on intel button, did not work')
            return 1
        
    else:
        logging.info('Cannot find the Intel button, maybe I am not on the World page')
        return 1


def hunter(android:AndroidTouchControl|None,number = 4, **kwargs):
    pdb.set_trace()
    if (m:=android.wait_for_image(static_paths['magnifyer']),2):
        android.tap(*m)
        time.sleep(0.5)
        if (m:=android.wait_for_image(static_paths['polar']),2):
            android.tap(*m)
        else:
            # points
            android.swipe(250,1150,600,1150)
            android.click_on_image(static_paths['polar'])
            logging.info('Done man mb')
        android.tap(600,1300)
        android._run_adb('shell','input','keyevent','67')
        android._run_adb('shell','input','keyevent','67')
        android._run_adb('shell','input','text',f'{number}'[0])
        android._run_adb('shell','input','text',f'{number}'[1:])
        android._run_adb('shell','input','keyevent','66')
        android.click_on_image(static_paths['search_btn'])
        time.sleep(1)
        if (m:=android.wait_for_image(static_paths['rally'],timeout=10)):#convert to wait if statement coz maybe you don't find any 
            android.tap(*m)
            time.sleep(1)
            #add rally time stuff here, I guess
            android.click_on_image(static_paths['hold_rally'])
            #probably add the hero selection here
            hero_selector(android,select_gina=True)
            
            if (m:=android.wait_for_image(static_paths['deploy'],timeout=10)):
            #wait for exploration here coz there maybe someone else is marching towards the target. 
            # Wait 10 sec, then back button till exploration visible
                android.tap(*m)
            else:
                logging.info('Looks like there is something else, like another rally marching towards the target')
                logging.info('Trying to go back to world page')
                for i in range(5):
                    android.tap(*static_points['points']['recorded_at_720x1520']['back'])
                    # time.sleep(1)
                    if android.wait_for_image(static_paths['exploration'],timeout=3):
                        break
                else:
                    logging.info('Need to reset I guess')
                    skip_shit_and_start_game(android,shutdown=True)
                    if (m:=android.wait_for_image(os.path.join((os.path.abspath('')),'template_images','World.png'),
                                        timeout=5)):
                        logging.info('Not on World map, going there')
                        android.tap(*m)
        else:
            logging.info('Looks like no polar terror found, skipping')

    else:
        logging.info('Cannot find the polar thing')


def helper(android:AndroidTouchControl|None, default_timeout = 2, **kwargs):
    if  android.click_on_image(os.path.join((os.path.abspath('')),'template_images','Help.png')):
        if (m:=android.wait_for_image(os.path.join((os.path.abspath('')),'template_images','Back Btn.png'),
                           timeout = default_timeout)):
            print(f'back button: {m}')
            android.tap(*m)
    return 0

def skip_shit_and_start_game(android:AndroidTouchControl|None, shutdown = True, go_to_world = True):
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
    for _ in range(12):
        if (n:=android.wait_for_image(path_for(['template_images','Confirm Button.png']),
                            timeout=2)):
            logging.info('Found confirm button, game open')
            android.tap(*n)
            break

        elif (n:=android.find_template(path_for(['template_images','Exploration.png']),'screen.png')):
            # android.tap(*n)
            logging.info('Looks like I loaded straight in. Did I crash?')
            break
    else:
        logging.info('I am being sold some random junk, need to get out')
        for i in range(3):
            # android.tap(670+i*10,70)
            
            android._run_adb('shell','input','keyevent','4')
            if (m:=android.wait_for_image(path_for(['template_images','Confirm Button.png']),
                           timeout=3)):
                android.tap(*m)
                break
            elif (m:=android.wait_for_image(path_for(['template_images','Exploration.png']),timeout=3)):
                break
        else:
            if (m:=android.wait_for_image(os.path.join((os.path.abspath('')),'template_images','Exploration.png'),
                           timeout=3)):
                logging.info('Finally in game....I think')
            else:
                logging.info('Game blocked me, gege')
                time.sleep(5)
                exit()
        
    if go_to_world:
        if (m:=android.wait_for_image(os.path.join((os.path.abspath('')),'template_images','World.png'),
                            timeout=5)):
            logging.info('Not on World map, going there')
            android.tap(*m)

if __name__ == '__main__':
    main()
