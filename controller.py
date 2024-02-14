#manages the bots
import config
from seleniumbase import SB
from time import sleep
import datetime
from bot_class import *
import json
import os
import instalog

class Controller():
    def __init__(self,*args,**kwargs) -> None:
        pass
    def start(self,username,password,option=0,forced:bool=False):
        '''
        (start is the user controller)
        1. mass unfollow
        2. Always Follow (by target)
        3. Unfollow by app

        if forced, it means the bot was started via scheduler
        '''

        #load bot and start instagrapi client
        user = self.add_load_bot(username,password)

        if not hasattr(user,"client"):
            user.startClient()

        #perform actions
        act_result=0
        if forced:
            user.scheduled = True
        if option==1:
            act_result = user.unfollow_mass()
        elif option==2:
            act_result = user.follow_mass_by_target()
        elif option==3:
            act_result = user.unfollow_mass_followed()

        #check outputs
        if(act_result==100):
            instalog.talk('Elements not found, maybe the list is empty?')
        elif(act_result==200):
            instalog.talk('Action limit per day reached. You can change this value in the account configuration (not recomended for new accounts).')
        elif(act_result==15):
            instalog.talk('Task finished. You have unfollowed everyone who were followed by this app.')
        elif(act_result==300):
            instalog.talk('Reached the target scheduled tasks.')
        elif(act_result==404):
            instalog.talk('Error locating elements, please wait for an update')

        input('Continue')

        
    def autoStart(self):
        enabled_bots = session.query(Bot_Account).filter(Bot_Account.scheduled_enabled == True).all()
        if not enabled_bots:
            return 404
        for b in enabled_bots:
            print(self.get_bot_info(b))
            if b.scheduled_follows:
                self.start(b.username,b.password,2,forced=True)
            elif b.scheduled_unfollows:
                self.start(b.username,b.password,3,forced=True)
            else: 
                b.scheduled_enabled=False
                b.saveInstance()

    def enable_autoStart(self,username:str)->bool:
        bot = self.add_load_bot(username)
        if not bot:
            return False
        bot.scheduled_enabled = True
        bot.saveInstance()

    def add_load_bot(self,username,password=None)->'Bot_Account':
        '''Returns user object.'''
        user=session.query(Bot_Account).filter_by(username=username).first()
        if user == None:
            #create new user object
            '''Creates and saves user. Returns user object after created'''
            dic = {}
            user = Bot_Account(
                #account info
                username=username,
                password=password,
                logins=0,
                last_login = None,
                #bot info
                tokens=200,
                waitUntil=datetime.datetime.now(),
                avaliable=True,
                total_followed=0,
                total_unfollowed=0,
                following_list_dic_json=json.dumps(dic),
                targeting_list_dic_json = json.dumps(dic),
                actions_per_day=200,
                actions_rest_time=3600*24,
                wait_after_click = 0.5,
                scheduled_enabled=False,
                scheduled_follows=0,
                scheduled_unfollows=0,
                scheduled_unfollows_everyone= False,
                instagrapi_max_list_query=200
            )
            session.add(user)
            session.commit()
        return user
    
    def get_bot_info(self,bot:Bot_Account)->str:
        info=f'''|-------|Account|-------|
Username: {bot.username}

|-------|Configuration|-------|
Remaining actions: {str(bot.tokens)}
Max Daily actions: {str(bot.actions_per_day)}
Wait time after click: {str(bot.wait_after_click)} (seconds)

|-------|Stats|-------|
Total followed: {str(bot.total_followed)}
Total unfollowed: {str(bot.total_unfollowed)}
Total Logins: {str(bot.logins)}
Following with this app: {str(len(json.loads(bot.following_list_dic_json)))}

|-------|Automatic actions|-------|
Scheduled follows: {str(bot.scheduled_follows)}
Scheduled unfollows: {str(bot.scheduled_unfollows)} 
Scheduler activated: {str(bot.scheduled_enabled)}
        '''
        return info

    def remove_bot(self,username):
        user=session.query(Bot_Account).filter_by(username=username).first()
        if user:
            session.delete(user)
            session.commit()
        else:
            instalog.talk('User ' + username + ' doesn\'t exist')

    def getBots(self) -> list['Bot_Account']:
        '''Return object list'''
        return session.query(Bot_Account).all()

    def talk(self,words:str):
        if not (config.debug_mode):
            print('Controller: ' + words)
        else:
            print('Controller (debug mode): ' + words)

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

