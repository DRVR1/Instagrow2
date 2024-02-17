'''
Description:
    Handler for instagrapi exceptions (tells the bot what to do with specific exceptions)
'''


import instalog


def loginrequired(bot_object,exception):
    instalog.error(exception)
    result = bot_object.login()
    return result


def PleaseWaitFewMinutes(bot_object,exception):
    instalog.error(f'i. Handled exception: {exception}\ntrying to re-login')
    bot_object.client.logout()
    result = bot_object.login()
    return result


def ChallengeRequired(bot_object,exception):
    instalog.error(f'i. Handled exception: {exception}\n Solution: login and solve the captcha.)')
    bot_object.client.logout()
    return False


def FeedbackRequired(bot_object,exception):
    instalog.error(f"i. Handled exception: {exception}\ni. Solution: take a rest, instagram is blocking your actions")
    bot_object.client.logout()
    return False


def unhandled(e):
    instalog.error(f'i. Unhandled exception: {e}')
    return False

