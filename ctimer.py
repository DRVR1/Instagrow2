#time related functions

import datetime
from datetime import timedelta
import random
import instalog
from time import sleep

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
    if bot.tokens<=0 and bot.avaliable:
        bot.avaliable=False
        new_time =  datetime.datetime.now() + timedelta(seconds=bot.actions_rest_time)
        bot.waitUntil = new_time.strftime("%H:%M:%S - %d %B %Y")
        current_timestamp = datetime.datetime.now()
        bot.waitUntil = current_timestamp
        bot.saveInstance()
        return False
    if time_hasPassed(bot.waitUntil,seconds=bot.actions_rest_time) and not bot.avaliable:
        bot.tokens=bot.actions_per_day
        bot.avaliable = True
        bot.saveInstance()
        return True
    if not bot.avaliable:
        return False
    return True

def wait(bot,time,time2=False,reason:str=False) -> None:
    '''
    Waits a random time interval [time - time2]
    '''
    if reason:
        instalog.talk("Waiting "+ str(time) + " seconds. Reason: " + reason)
    if(time2):
        time = random.randint(time,time2)
    sleep(float(time))
