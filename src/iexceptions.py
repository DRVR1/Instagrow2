'''
Author: ian vidmar

Description:
    Handler for instagrapi exceptions (tells the bot what to do with specific exceptions)
'''

# Custom modules
import instalog

# Functions returns false when the execution should not continue.

def loginrequired(bot_object,exception):
    instalog.error(exception)
    result = bot_object.login()
    return result


def PleaseWaitFewMinutes(bot_object,exception):
    instalog.error(f'i. Handled exception: {exception}\ni. trying to re-login')
    bot_object.client.logout()
    result = bot_object.login()
    return result


def ChallengeRequired(bot_object,exception):
    instalog.error(f'i. Handled exception: {exception}\ni. Solution: login and solve the captcha.)')
    bot_object.client.logout()
    return False


def FeedbackRequired(bot_object,exception):
    instalog.error(f"i. Handled exception: {exception}\ni. Solution: take a rest, instagram is blocking your actions")
    bot_object.client.logout()
    return False


def ClientNotFoundError(bot_object,exception):
    instalog.error(f"i. Handled exception: {exception}\ni. User not found.")
    return True


def unhandled(e):
    instalog.error(f'i. Unhandled exception: {e}')
    return False

