'''
Author: ian vidmar

Description:
    middle-level module that works
    as the main menu helper and bot scheduler
'''

# Default modules
import os
import sys

# Custom modules
import config
from bot_class import *

# Downloaded modules
import json
import instalog
from PyQt5.QtWidgets import QApplication, QFileDialog

class Menu_Helper():
    
    def __init__(self,*args,**kwargs) -> None:
        pass


    def get_input(self)->int:
        '''Gets user input'''
        while True:
            try:
                prompt = input('\nInput: ')
                op = abs(int(prompt))
                if op==0:
                    return False
                return op
            except ValueError:
                print("Invalid input. Please enter a valid integer.")


    def _menu_wrap(func):
        '''A wrapper that clears the console before every menu section'''
        @functools.wraps(func) 
        def wrapper(self:'Menu_Helper',*args,**kwargs):
            os.system("cls")
            return func(self,*args,**kwargs)
        return wrapper
    

    @_menu_wrap
    def menu_main(self) -> int:
        '''Returns selected option'''
        '''
        if len(sys.argv)>1:
            print(f'Parameter: {str(sys.argv[1])}')
            while(True):
                result = controller.autoStart()
                if(result==404):
                    print('Autostart enabled. Waiting for user configuration.')
                sleep(3)
        '''
        if config.debug_mode:
            print(f'Startup folder: {config.get_startup_folder()}')
            print(f'Executing from: {config.get_running_path()}\n')
            print(f'All your data and scrapped info will be saved in: \n{config.app_data_dir}\n')
        print("Welcome.")
        print('Remember: your account must be verified with phone number to avoid blocking. Also 2FA (two factor autentication) has to be disabled in order for this script to work.')
        
        
        text='''          
        1. Add account
        2. Manage accounts
        0. Exit'''
        print(text)

        return self.get_input()
    

    @_menu_wrap
    def mainMenu_add_account(self) -> 'Bot_Account':
        '''Returns added bot object'''
        username = str(input("\nUsername: @"))
        password = str(input("\nPassword: "))
        bot = Bot_Account().create_load_bot(username,password)
        print("\nAdded.\n")
        input('Continue')
        return bot


    @_menu_wrap
    def mainMenu_manage_accounts(self) -> 'Bot_Account':
        '''Returns selected bot object'''
        print('Select an account: \n')

        tupleList = [''] # [ '' , [ int , Bot_Account ] , [int , Bot_Account ]... ] 
        i=0

        try:
            for bot in self.bot_getBots():
                    i+=1
                    username=bot.username
                    scheduled = False
                    if bot.scheduled_enabled:
                        scheduled=True
                    print(f'{str(i)}. scheduled: [{str(scheduled)}] Username: @{username}')
                    tuple = (i,bot) 
                    tupleList.append(tuple)
        except:
            print("Error reading users, try adding users first.")
            return
        
        selection = self.get_input()
        if selection==0:
            return False
        try:
            return tupleList[selection][1] # Returns Bot object
        except:
            return False
    

    @_menu_wrap
    def menu_configure_bot(self,bot:'Bot_Account') -> int:
        '''
            - Displays menu option
            - Returns selected option for the bot
        '''
        text = f'''          
|-------|Account Data|-------|
1. Change username ({bot.username})
2. Change password\n
|-------|Statistics|-------|
3. View bot info\n
|-------|Configuration|-------|
4. Change daily limit (current: [{str(bot.config_actions_per_day)}] (recomended: 200)
5. Change wait time after clicking buttons [{self.bot_get_action_wait_range(bot)}]
6. Configure automatic actions [{str(bot.scheduled_enabled)}] (coming soon)\n
|-------|Scrapping|-------|
7. Scrape followers by username
8. Scrape followings by username
9. Scrape account info\n
|-------|Actions|-------|
10. Mass follow (must provide scrapped user list)
11. Mass unfollow (must provide scrapped user list)
12. Who is unfollowing me? (coming soon)\n
|-------|Configuration (Warning)|-------|
99. Delete\n'''
        text9='0. Back'

        print(text)
        print(text9)
        
        op = self.get_input()
        if op==0:
            return False
        else:
            return op

 
    @_menu_wrap
    def configure_username(self,bot:'Bot_Account') -> bool:
        new_username = str(input(f'[{bot.username}] New username: @'))
        if new_username == '0':
            return False
        bot.username=new_username
        bot.saveInstance()

 
    @_menu_wrap
    def configure_password(self,bot:'Bot_Account') -> bool:
        new_password = str(input(f'[{bot.username}] New password: '))
        if new_password == '0':
            return False
        bot.password=new_password
        bot.saveInstance()

  
    @_menu_wrap
    def get_bot_info(self,bot:Bot_Account)->str:
        info=f'''|-------|Account|-------|
Username: {bot.username}

|-------|Configuration|-------|
Remaining actions: {str(bot.stats_tokens)}
Max Daily actions: {str(bot.config_actions_per_day)}
Wait time after click: random range in {str(bot.config_wait_range_1)}s to {str(bot.config_wait_range_2)}s (seconds)

|-------|Stats|-------|
Total followed: {str(bot.stats_total_followed)}
Total unfollowed: {str(bot.stats_total_unfollowed)}
Total Logins: {str(bot.stats_logins)}
Following with this app: {str(len(json.loads(bot.automated_followings_ids)))}
Last login: {bot.stats_last_login.strftime("%H:%M:%S - %d %B %Y")}

|-------|Automatic actions|-------|
Scheduled follows: {str(bot.scheduled_follows)}
Scheduled unfollows: {str(bot.scheduled_unfollows)} 
Scheduler activated: {str(bot.scheduled_enabled)}
        '''
        return info


    @_menu_wrap
    def configure_daily_limit(self,bot:'Bot_Account') -> bool:
        print('Your daily limit is ' + str(bot.config_actions_per_day) + ' and your currently avaliable actions are ' + str(bot.stats_tokens))
        print('Enter new limit (0 for cancel): ')
        lim = self.get_input()
        if not lim:
            return False
        bot.config_actions_per_day = lim
        bot.stats_tokens = lim
        bot.saveInstance()
        input('Daily limit changed to ' + str(lim) + ' actions. Continue?')
        return True


    @_menu_wrap
    def configure_wait_time(self,bot:'Bot_Account') -> bool:
        print(f'Current wait range: {self.bot_get_action_wait_range(bot)}')        
        lim = float(input('Enter range start (0 for cancel): '))
        if lim <= 0:
            return False
        lim2 = float(input('Enter range end (0 for cancel): '))
        if lim2 <= 0:
            return False
        bot.config_wait_range_1=lim
        bot.config_wait_range_2=lim2
        bot.saveInstance()
        print(f'Current wait range: {self.bot_get_action_wait_range(bot)}')       


    def _scrapper_wrap(func):
        '''A wrapper for scrapping activities'''
        @functools.wraps(func) 
        def wrapper(self:'Menu_Helper',bot:'Bot_Account',*args,**kwargs):
            os.system("cls")
            # Check if the function was called for User (single) or list[UserShort]
            single = kwargs.get('single')
            # Login and option selection
            print("WARNING: It's not recomended to scrape foreign data with your personal account (can get you banned). Please use a trash account.\n")
            if single:
                pass
            else:
                print("How much followers (max) do you want to scrape? (the less, the safer, and faster)")
                max = self.get_input()
                if not max:
                    return False
            uname = str(input("Instagram account: @"))
            if uname == '0':
                return False
            if not bot.login():
                return False
            # Get user object
            instalog.talk('Getting user object...')
            userObj = bot.scrape_account_data(uname)
            if not userObj:
                return False
            uId = userObj.pk

            if single:
                filename = func(self,bot,*args,_uname=uname,_uId=uId,**kwargs)
            else:
                filename, shortlist = func(self,bot,*args,_uname=uname,_uId=uId,_max=max,**kwargs)
                if not shortlist:
                    return False

            savePath = os.path.join(config.instagrow_scrapped_path,filename)

            if single:
                bot.dump_user_obj_to_json(userObj,save_path=savePath)
            else:
                bot.dump_userList_to_json(shortlist,save_path=savePath)

            input(f'Json saved in {savePath}.\nContinue')
            return True
        return wrapper
    

    @_scrapper_wrap
    def scrape_followers_by_username(self,bot:'Bot_Account',_uname=False,_uId=False,_max=False) -> tuple[str,list[UserShort]]:
        uname = _uname
        uId = _uId
        max = _max
        # Scrape followers from user ID
        instalog.talk('Scrapping...')
        shortlist = bot.scrape_followers(user_id=uId,max_followers=max)

        # Save scraped followers into a file
        filename = uname + '.followers.' + uId + '.json'

        return filename, shortlist


    @_scrapper_wrap
    def scrape_followings_by_username(self,bot:'Bot_Account',_uname=False,_uId=False,_max=False) -> tuple[str,list[UserShort]]:
        uname = _uname
        uId = _uId
        max = _max
        # Scrape followings from user ID
        shortlist = bot.scrape_following(user_id=uId,max_following=max)

        # Save scraped followings into a file
        filename = uname + '.followings.' + uId + '.json'

        return filename, shortlist


    @_scrapper_wrap
    def scrape_account_info(self,bot:'Bot_Account',_uname=False,_uId=False,_max=False,single=True) -> str:
        uname = _uname
        uId = _uId

        # Save scraped followings into a file
        filename = uname + '.FullData.' + uId + '.json'

        return filename


    def _mass_wrap(func):
        '''A wrapper for mass actions'''
        @functools.wraps(func) 
        def wrapper(self:'Menu_Helper',bot:'Bot_Account',*args,**kwargs):
            # Asks for json file
            app = QApplication([])
            file_path, _ = QFileDialog.getOpenFileName(None, "Select the .json user list", config.instagrow_scrapped_path)
            instalog.talk(f"Selected File: {file_path}")
            # Convert json file to UserShort list
            shortList = bot.retrieve_json_UserShortList(save_path=file_path)
            instalog.talk(f"Warning: {str(len(shortList))} accounts are selected. Do you wish to continue?")
            print('Input 0 for cancel. Input anything to continue.')
            if not self.get_input():
                return False
            if not bot.login():
                return False
            result = func(self,bot,*args,_shortlist=shortList,**kwargs)
            input('Continue')
            return result
        return wrapper
    

    @_mass_wrap
    def mass_follow(self,bot:'Bot_Account',_shortlist=False):
        shortList = _shortlist 
        bot.follow_mass(shortList)
        

    @_mass_wrap
    def mass_unfollow(self,bot:'Bot_Account',_shortlist=False):
        shortList = _shortlist 
        bot.unfollow_mass(shortList)


    def bot_get_action_wait_range(self,bot:'Bot_Account') -> str:
        return f"{str(bot.config_wait_range_1)}s to {str(bot.config_wait_range_2)}s (seconds)"
    

    def bot_remove(self,username):
        Bot_Account().delete_bot(username)


    def bot_getBots(self) -> list['Bot_Account']:
        '''Return object list'''
        return session.query(Bot_Account).all()
    

    def bot_enable_autoStart(self,username:str)->bool:
        '''Enables the autostartup of a providen bot'''
        bot = Bot_Account().create_load_bot(username)
        if not bot:
            return False
        bot.scheduled_enabled = True
        bot.saveInstance()


    def windows_autoStarted(self):
        '''Function that get executed only if the program was autostarted'''
        enabled_bots = session.query(Bot_Account).filter(Bot_Account.scheduled_enabled == True).all()
        if not enabled_bots:
            return False
        for b in enabled_bots:
            print(self.get_bot_info(b))
            if b.scheduled_follows:
                pass
            elif b.scheduled_unfollows:
                pass
            else: 
                b.scheduled_enabled=False
                b.saveInstance()


    def windows_create_autostartup(self):
        '''Creates an autostartup batch file in the windows startup folder.'''
        
        script=f"start /min \"\" \"{config.get_running_path()}\" auto"
        script_path = os.path.join(config.get_startup_folder(),config.AutoRun_Script_Name)
        instalog.talk(f'Creating startup file...\nPath:{script_path}')
        try:
            with open(script_path, "w") as file:
                file.write(script)
                file.close()
                instalog.talk('Autostartup is now enabled.')
        except:
            print(f'Error writing the script path. AutoStartup was not enabled. \nPath: {script_path}')
            input('return')
    

    def windows_remove_autostartup(self):
        script_path = os.path.join(config.get_startup_folder(),config.AutoRun_Script_Name)
        instalog.talk(f'Removing startup file...\nPath:{script_path}')
        try:
            os.remove(script_path)
            instalog.talk('Autostartup is now disabled.')
        except:
            instalog.talk(f'Startup file was not found')

