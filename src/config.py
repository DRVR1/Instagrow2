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
import platform

debug_mode = False

#===============|String Values|================:
AppName = 'InstaGrow2'
AppVersion = '0.1'
AutoRun_Script_Name = 'InstaGrow2.bat'
instagrapi_settings_name='settings.json'

console_clear_command = ''

##===============|PATHS|================:
app_data_dir = ''

if platform.system() == 'Windows':
    app_data_dir = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', AppName)
    console_clear_command = 'cls'
elif platform.system() == 'Linux':
    app_data_dir = os.path.join(os.path.expanduser("~"), ".local", "share", AppName)
    console_clear_command = 'clear'
else:
    app_data_dir = AppName+'_appData'
    console_clear_command = 'clear'

if not os.path.exists(app_data_dir):
    os.makedirs(app_data_dir)

# Path where the log file is saved (General log, for every bot)
instagrow_log_path = os.path.join(app_data_dir,'log.txt')

# Path where the scrapped json's will be saved
instagrow_scrapped_path = os.path.join(app_data_dir,'scrapped')
if not os.path.exists(instagrow_scrapped_path):
    os.makedirs(instagrow_scrapped_path)

# Path where the merged json's will be saved
instagrow_merged_path = os.path.join(app_data_dir,'merged')
if not os.path.exists(instagrow_merged_path):
    os.makedirs(instagrow_merged_path)

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
