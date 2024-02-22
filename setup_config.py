#Description
#This script will use pyInstaller and Inno Setup Compiler to create an installation file for the software.
#Both pyinstaller and Inno, are required in order to run this script. 
#output: an executable file for the program, and an installer.

#IMPORTANT BEFORE PACKING
# - Inno Setup 6 must be installed in your windows computer


import os
import shutil
import subprocess
from src import config

if config.debug_mode:
    os.system('cls')
    os.system('color C')
    print('WARNING: DEBUG MODE IS ENABLED')
    input('continue?')

# General
appName = config.AppName
folder_resources = 'res'

# Pyinstaller
main_file = "\"src/main.py\""
icon_path = "\"res/InstaGrow2.ico\""

# Inno setup
icon_name='InstaGrow2.ico'
setup_compiler_path = r"C:\\Program Files (x86)\\Inno Setup 6\\ISCC.exe" 
script_path = f"{folder_resources}\\setup_script.iss"  
output_dir = 'Windows_Setup_Output'

#clean after packing
foldersToDelete = ['build','__pycache__']
filesToDelete = [f'{appName}.spec']

def pyInstaller():
    os.system('cls')
    print(f'{appName} windows package setup\n')
    print('This setup will install the python requirements, pack the code and create an installation file.\n')
    print(f'WARNING: you should have Inno Setup Compiler installed in the following path:\n\nPATH: {setup_compiler_path}\n\nIf the path doesn\'t match, change it in this script.\n')
    input('Continue?')

    if not os.path.exists(setup_compiler_path):
        print(f'The following path was not found, please check your installation or change the path in this same script: {setup_compiler_path}')
        input('exit')
        exit()

    print('Installing requirements...')
    os.system('pip install -r requirements.txt')
    print('Exporting .exe file')
    os.system(f"pyinstaller --noconfirm --onefile --console --clean --icon={icon_path} --name {appName} --distpath {folder_resources} {main_file}")

    try:
        for folder in foldersToDelete:
            shutil.rmtree(folder)
        for file in filesToDelete:
            os.remove(file)
    except:
        pass

    print('\nFinished.')
    print('Output file located in dist/ folder')
    print('Creating setup file')

def innoSetup():
    os.system(f"icoextract {folder_resources}\\{config.AppName}.exe {folder_resources}\\{icon_name}")

    script=f'''
[Setup]
AppName={config.AppName}
AppVersion={config.AppVersion}
DefaultDirName={{pf}}\{config.AppName}
DefaultGroupName={config.AppName}
OutputDir={output_dir}
OutputBaseFilename={config.AppName} Installer
Compression=lzma
SolidCompression=yes
UninstallDisplayIcon={{app}}\\{icon_name}
UninstallDisplayName={config.AppName} ({config.AppVersion})

[Files]
Source: "{config.AppName}.exe"; DestDir: "{{app}}\{config.AppName}"
Source: "{icon_name}"; DestDir: "{{app}}"

[Icons]
Name: "{{group}}\\{config.AppName}"; Filename: "{{app}}\\{config.AppName}\\{config.AppName}.exe"
Name: "{{commondesktop}}\\{config.AppName}"; Filename: "{{app}}\\{config.AppName}\\{config.AppName}.exe"
'''
    # Write the script content to a file
    try:
        with open(script_path, "w") as file:
            file.write(script)
            file.close()
    except:
        print(f'Error writing the script path. Please execute this script from its root foler\nPath: {script_path}')
        input('exit')
        exit()

    subprocess.run([setup_compiler_path, script_path])
    input('Press a key to exit')

pyInstaller()
innoSetup()