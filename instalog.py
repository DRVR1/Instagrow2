#just a log

import config
import datetime


def talk(words):
    print(words)
    try:
        with open(config.instagrow_log_path,'a') as f:
            f.write(f'Talk: ({str(datetime.datetime.now().replace(second=0, microsecond=0).strftime("%d-%B-%Y %H:%M"))}) {words}\n')
            f.close()
    except:
        print('Error saving log')

def error(words):
    print(words)
    try:
        with open(config.instagrow_log_path,'a') as f:
            f.write(f'ERROR: ({str(datetime.datetime.now().replace(second=0, microsecond=0).strftime("%d-%B-%Y %H:%M"))}) {words}\n')
            f.close()
    except:
        print('Error saving log')