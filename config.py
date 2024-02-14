#config file, accesed by most of the modules

#dropping files in:
#appData
#programFiles
#autorun

import os
import sys

debug_mode = True

#===============|String Values|================:
AppName = 'InstaGrow2'
AppVersion = 'pre-alpha'
AutoRun_Script_Name = 'InstaGrow2.bat'
instagrapi_settings_name='settings.json'
icon_path = "icon.ico"

##===============|Proxy|================:
proxy='unknown'

##===============|WINDOWS PATHS|================:
app_data_dir = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', AppName)
if not os.path.exists(app_data_dir):
    os.makedirs(app_data_dir)
    
instagrow_log_path = os.path.join(app_data_dir,'log.txt')
db_file_path = os.path.join(app_data_dir, f'{AppName}.UserData.db')
instagrapi_settings_path = os.path.join(app_data_dir,instagrapi_settings_name)

def get_startup_folder():
    appdata_path = os.environ.get('APPDATA')
    startup_folder = os.path.join(appdata_path, 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
    return startup_folder

def get_running_path():
   return sys.executable
