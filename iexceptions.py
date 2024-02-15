import instalog

'''Handler for instagrapi exceptions (tells the bot what to do with specific exceptions)'''

def loginrequired(bot_object,exception):
    instalog.talk(exception)
    result = bot_object.login()
    return result

def PleaseWaitFewMinutes(bot_object,exception):
    instalog.talk(f'Handled exception: {exception}\ntrying to re-login')
    bot_object.client.logout()
    result = bot_object.login()
    return result

def unhandled(e):
    instalog.talk(f'Unhandled exception: {e}')
    return 1

