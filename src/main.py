'''
Author: ian vidmar

Description:
    main menu, run this script to start the app
'''

# Custom modules:
import menuHelper
from bot_class import Bot_Account


helper = menuHelper.Menu_Helper()

def continue_func():
    input('Continue')

def main():
    op = helper.menu_main()

    if op == 0:
        exit()

    elif op == 1:
        helper.mainMenu_add_account()
        main()

    elif op == 2:
        bot = helper.mainMenu_manage_accounts()

        if not bot:
            main()
        
        configure_bot(bot)


def configure_bot(bot:'Bot_Account'):
        op = helper.menu_configure_bot(bot)
        if op == 1:
            helper.configure_username(bot)
            configure_bot(bot)
        elif op == 2:
            helper.configure_password(bot)
            configure_bot(bot)
        elif op == 3:
            print(helper.get_bot_info(bot))
            continue_func()
            configure_bot(bot)
        elif op == 4:
            helper.configure_daily_limit(bot)
            configure_bot(bot)
        elif op == 5:
            helper.configure_wait_time(bot)
            configure_bot(bot)
        elif op == 6:
            configure_bot(bot)
        elif op == 7:
            result = helper.scrape_followers_by_username(bot)
            if not result:
                continue_func()
            configure_bot(bot)
        elif op == 8:
            result = helper.scrape_followings_by_username(bot)
            if not result:
                continue_func()
            configure_bot(bot)
        elif op == 9:
            result = helper.scrape_account_info(bot,single=True)
            if not result:
                continue_func()
            configure_bot(bot)
        elif op == 10:
            helper.mass_follow(bot)
            configure_bot(bot)
        elif op == 11:
            helper.mass_unfollow(bot)
            configure_bot(bot)
        elif op == 99:
            helper.bot_remove(bot.username)
            input('Removed. Continue')
            main()
        elif op == 0:
            main()


if __name__ == '__main__':
    main()