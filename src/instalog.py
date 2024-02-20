'''
Author: ian vidmar

Description:
    Simple logger module
'''

# Default modules
import datetime
import functools

# Custom modules
import config


def _print_wrapper(func):
    @functools.wraps(func) 
    def wrapper(*args,**kwargs):
        func(*args,**kwargs)
        words = args[0]
        str_date = str(datetime.datetime.now().replace(second=0, microsecond=0).strftime("%d-%B-%Y %H:%M"))
        name = ''
        if func.__name__ == "talk":
            name = f'TALK '
        if func.__name__ == "error":
            name = f'ERROR'
        if func.__name__ == "debug":
            name = f'DEBUG'

        final = f'{name} - ({str_date}): {words}'
        
        try:
            with open(config.instagrow_log_path,'a') as f:
                f.write(final+'\n')
                f.close()
        except Exception as e:
            print(f'ERROR saving log: {e}')

    return wrapper


@_print_wrapper
def talk(words):
    print(words)
    
@_print_wrapper
def error(words):
    print(words)

@_print_wrapper
def debug(words):
    pass
    #print(words)
