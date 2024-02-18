'''
Author: ian vidmar

Description:
    Configuration file, contains paths and names that may be used in compilation, or runtime.
'''
# Paths being used (windows):
# - AppData
# - ProgramFiles
# - Microsoft Autostartup folder

# Default modules
import os
import sys

debug_mode = True

#===============|String Values|================:
AppName = 'InstaGrow2'
AppVersion = 'pre-alpha'
AutoRun_Script_Name = 'InstaGrow2.bat'
instagrapi_settings_name='settings.json'
icon_path = "icon.ico"

##===============|WINDOWS PATHS|================:
app_data_dir = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', AppName)
if not os.path.exists(app_data_dir):
    os.makedirs(app_data_dir)

# Path where the log file is saved (General log, for every bot)
instagrow_log_path = os.path.join(app_data_dir,'log.txt')

# Path where the scrapped json's will be saved
instagrow_scrapped_path = os.path.join(app_data_dir,'scrapped')
if not os.path.exists(instagrow_scrapped_path):
    os.makedirs(instagrow_scrapped_path)

#Bots database path (bot_class's database)
db_file_path = os.path.join(app_data_dir, f'{AppName}.UserData.db')

# Path where the scrapped json's will be saved
instagrow_settings_path = os.path.join(app_data_dir,'settings')
if not os.path.exists(instagrow_settings_path):
    os.makedirs(instagrow_settings_path)

# Instagrapi settings path (unique file for each bot) (useragent, device info, etc)
def get_instagrapi_settings_path(bot_name:str)->str:
    return os.path.join(instagrow_settings_path,bot_name+'.'+instagrapi_settings_name)

# Get startup folder where the app settings and databases will be saved
def get_startup_folder():
    appdata_path = os.environ.get('APPDATA')
    startup_folder = os.path.join(appdata_path, 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
    return startup_folder

# Get the path from where the script or .exe is running from. Useful for the autostartup feature.
def get_running_path():
   return sys.executable
