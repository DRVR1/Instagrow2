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
import instalog
import filehelper
import art

# Downloaded modules
import json
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
        print(art.app_title)
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
12. Who is unfollowing me? (must provide scrapped followers and followings)
13. Merge lists of followers / followings\n
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


    def _scrapper_login_handler(self,bot:'Bot_Account', single):
        '''Login and select target user'''
        os.system("cls")        
        print("WARNING: It's not recomended to scrape foreign data with your personal account (can get you banned). Please use a trash account.\n")
        
        max = None

        # If mass scrapping
        if not single:
            print("How much users (max) do you want to scrape? (the less, the safer, and faster)")
            max = self.get_input()
            if not max:
                return False
            
        # Both cases (mass and single scrapping)
        uname = str(input("Instagram account: @"))
        if uname == '0':
            return False
    
        # Ask for cursor if user has it
        cursor = ''
        if not single:
            cursor_input = str(input("Last saved cursor (default leave blank): "))
            if cursor_input:
                cursor = cursor_input

        if not bot.login(disable_wait=True):
            return False
        
        return max, uname, cursor
    

    def _scrapper_wrap(func):
        '''A wrapper for scrapping activities'''
        @functools.wraps(func) 
        def wrapper(self:'Menu_Helper',bot:'Bot_Account',*args,**kwargs):
            single = kwargs.get('single')

            # Login and ask the user max ammount of users, and target user
            max_followers, uname, input_cursor = self._scrapper_login_handler(bot,single)

            # Get target user object
            instalog.talk('Getting user object...')
            userObj = bot.scrape_account_data(uname)
            if not userObj:
                return False
            
            # Retrieve userID from user object in order to scrape
            uId = userObj.pk

            # Retrieve total followers and followings count.
            follower_count = userObj.follower_count
            following_count = userObj.following_count
                        
            # Define possible outputs outside the conditional structure
            shortlist = None
            cursor = None
            filename = None
            # Scrape single account
            if single:
                filename = func(self,bot,*args,_uname=uname,_uId=uId,**kwargs)
            # Scrape multiple accounts
            else:
                returned = func(self,bot,*args,_uname=uname,_uId=uId,_follower_count=follower_count,_following_count=following_count,_max_followers=max_followers,_cursor=input_cursor,**kwargs)
                # Scrapping fully completed
                if len(returned) == 2:
                    filename, shortlist = returned
                # Instagram interrupted scrapping
                elif len(returned) == 3:
                    filename, shortlist, cursor = returned

                # Checks if shortlist is actually a list and contains users
                if not isinstance(shortlist,list):
                    instalog.error(f"Scrapping didn't return a list. Try again")
                    return False
                elif not isinstance(shortlist[0],UserShort):
                    instalog.error(f"Scrapped list doesn't contain user objects. Try again")
                    return False

            _savePath = os.path.join(config.instagrow_scrapped_path,filename)

            savePath = filehelper.rename_file(_savePath)


            if single:
                bot.dump_user_obj_to_json(userObj,save_path=savePath)
            else:
                bot.dump_userList_to_json(shortlist,save_path=savePath)


            instalog.talk(f'Json saved in {savePath}\n')
            input(f'Continue')
            return True
        return wrapper
    

    @_scrapper_wrap
    def scrape_followers_by_username(self,bot:'Bot_Account',_uname=False,_uId=False,_follower_count=False,_following_count=False,_max_followers=False,_cursor=False) -> Union[tuple[str,list],list]:
        uname = _uname
        uId = _uId
        follower_count = _follower_count
        max_followers = _max_followers
        cursor = _cursor

        filename = uname + '.followers.' + uId + '.json'

        instalog.talk('Scrapping...')
        # Scrape followers from user ID
        shortlist = bot.scrape_followers(uId,follower_count,max_followers=max_followers,cursor=cursor)
        
        # Instagram exception (returned tuple)
        if isinstance(shortlist,tuple):
            shortlist, cursor =  shortlist
            return filename, shortlist, cursor

        # No exception (returned shortlist)
        return filename, shortlist


    @_scrapper_wrap
    def scrape_followings_by_username(self,bot:'Bot_Account',_uname=False,_uId=False,_follower_count=False,_following_count=False,_max_followers=False,_cursor=False) -> Union[tuple[str,list],list]:
        uname = _uname
        uId = _uId
        following_count = _following_count
        max_followers = _max_followers
        cursor = _cursor

        # Save scraped followings into a file
        filename = uname + '.followings.' + uId + '.json'
        
        instalog.talk('Scrapping...')
        # Scrape followings from user ID
        shortlist = bot.scrape_following(uId,following_count,max_followers=max_followers,cursor=cursor)

        # Instagram exception (returned tuple)
        if isinstance(shortlist,tuple):
            shortlist, cursor =  shortlist
            return filename, shortlist, cursor

        # No exception (returned shortlist)
        return filename, shortlist


    @_scrapper_wrap
    def scrape_account_info(self,bot:'Bot_Account',_uname=False,_uId=False,_max=False,single=True) -> str:
        uname = _uname
        uId = _uId

        # Save scraped followings into a file
        filename = uname + '.FullData.' + uId + '.json'

        return filename
    

    def get_path_popup(self,title:str):
        app = QApplication([])
        file_path, _ = QFileDialog.getOpenFileName(None, title, config.instagrow_scrapped_path)
        app.exit()
        return file_path
    
    def get_paths_popup(self,title:str) -> list[str]:
        app = QApplication([])
        file_paths, _ = QFileDialog.getOpenFileNames(None, title, config.instagrow_scrapped_path)
        app.exit()
        return file_paths

    def _mass_wrap(func):
        '''A wrapper for mass actions'''
        @functools.wraps(func) 
        def wrapper(self:'Menu_Helper',bot:'Bot_Account',*args,**kwargs):
            # Asks for json file 
            file_path = self.get_path_popup("Select the .json user list")
            instalog.talk(f"Selected File: {file_path}")
            # Convert json file to UserShort list
            shortList = bot.retrieve_json_UserShortList(save_path=file_path)
            instalog.talk(f"Warning: {str(len(shortList))} accounts are selected. Do you wish to continue?")
            print('Input 0 for cancel. Input any number to continue.')
            if not self.get_input():
                return False
            if not bot.login(disable_wait=True):
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


    def compare_unfollowers(self,bot:'Bot_Account'): 
        follower_path = self.get_path_popup("Select a FOLLOWERS list")
        folllowing_path = self.get_path_popup("Select a FOLLOWINGS list")
        follower_set = set(bot.retrieve_json_UserShortList(follower_path))
        following_set = set(bot.retrieve_json_UserShortList(folllowing_path))
        # Compare sets: 
        unfollowers_set = following_set - follower_set
        unfollowers_list = list(unfollowers_set)
        for unfollower in unfollowers_list:
            instalog.talk(f"Unfollower: @{unfollower.username} id: {unfollower.pk}")
        instalog.talk(f"You have a total of {str(len(unfollowers_list))} unfollowers. WARNING: Data may be inaccurate. Please check before taking any actions.")
        # Save unfollowers
        path =  bot.username + '.unfollowers'+'.json'
        final_path = os.path.join(config.instagrow_scrapped_path,path)
        final_path = filehelper.rename_file(final_path)
        bot.dump_userList_to_json(unfollowers_list,save_path=final_path)
        instalog.talk(f"File saved in: {final_path}")


    def merge_followers_lists(self,bot:'Bot_Account'): 
        paths = self.get_paths_popup('Select user lists of the same type (example: two followers lists the same user)')
        final_path = config.instagrow_merged_path +'\\'+ os.path.basename(paths[0])
        final_path = filehelper.rename_file(final_path)
        instalog.talk(f"Are you sure you want to merge this {str(len(paths))} lists? they won't be deleted after the process. (0 for cancel)")
        val = self.get_input()
        if not val: 
            return False
        instalog.talk("Merging...")
        bot.merge_user_list(paths,save_path=final_path)
        instalog.talk(f"Merged file saved in {final_path}")


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

