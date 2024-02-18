'''
Author: ian vidmar

Description:
    Time related functions
'''
# Default modules
import datetime
from datetime import timedelta
import random
from time import sleep

# Custom modules
import instalog


def time_hasPassed(waitUntil,hours=0,seconds=0)->bool:
    '''Specify a Bot object (self), and the time that should have passed from (waitUntil) to return true'''
    previous_timestamp = waitUntil
    
    # Get the current timestamp
    current_timestamp = datetime.datetime.now()

    # Calculate the time difference
    time_difference = current_timestamp - previous_timestamp

    if hours and not seconds:
        if time_difference.total_seconds() >= hours * 3600: 
            return True
        else:
            return False
    elif seconds and not hours:
        if time_difference.total_seconds() >= seconds:  
            return True
        else:
            return False
    else:
        print("newtime: Time error. Used multiple time formats")
        return


def check_avaliable(bot)->bool:
    '''Checks if the bot can work again after running out of tokens by checking how much time has passed since then'''
    if bot.stats_tokens<=0 and bot.config_avaliable:
        bot.config_avaliable=False
        new_time =  datetime.datetime.now() + timedelta(seconds=bot.config_actions_rest_time)
        bot.config_waitUntil = new_time.strftime("%H:%M:%S - %d %B %Y")
        current_timestamp = datetime.datetime.now()
        bot.config_waitUntil = current_timestamp
        bot.saveInstance()
        return False
    if time_hasPassed(bot.config_waitUntil,seconds=bot.config_actions_rest_time) and not bot.config_avaliable:
        bot.stats_tokens=bot.config_actions_per_day
        bot.config_avaliable = True
        bot.saveInstance()
        return True
    if not bot.config_avaliable:
        return False
    return True


def wait(time:float,time2:float,comment:str=False) -> None:
    '''
    Waits a random time interval [time - time2]
    '''
    if(time2):
        time = random.uniform(time,time2)
    txt = "Waiting "+ str(time) + " seconds."
    if comment:
        txt += " Comment: " + comment
    instalog.talk(txt)        
    sleep(float(time))
