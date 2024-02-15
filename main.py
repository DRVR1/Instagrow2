#menu, manages the controller
from bot_class import *
import config
from controller import Controller
import os
import sys

controller = Controller()

def get_input(prompt):
    while True:
        try:
            op = abs(int(input(prompt)))
            return op
        except ValueError:
            print("Invalid input. Please enter a valid integer.")

def menu_delete_account(accname):
    controller.remove_bot(accname)
    
def menu_add_account():         
    username = str(input("\nUsername: @"))
    password = str(input("\nPassword: "))
    controller.add_load_bot(username,password)
    print("\nAdded.\n")
    menu_manage_accounts()

def menu_manage_accounts(back_username:str=False,back_username_op:int=False):
    tupleList = [''] 
    print('\nSelect an account: \n')
    stuser=''
    i=0
    if not back_username:
        try:
            for bot in controller.getBots():
                    username=bot.username
                    i+=1
                    scheduled = False
                    if bot.scheduled_enabled:
                        scheduled=True
                    print(f'{str(i)}. scheduled:{str(scheduled)} username: @{username}')
                    tup = (i,username) 
                    tupleList.append(tup)
        except:
            print("Error reading users, try adding users first.")
            input("Continue")
            menu()
        op = get_input('\nOption: ')

        if op==0:
            menu()
        try:
            stuser = tupleList[op][1] #gather selected username from tuple list
        except:
            print('Invalid user.')
            menu_manage_accounts()
    else:
        stuser=back_username
    os.system("cls")
    user = controller.add_load_bot(stuser) 
    if not user:
        print('error')
        menu()

    text=f'''          
    |-------|Account Data|-------|
    1. Change username ({user.username})
    2. Change password\n
    |-------|Statistics|-------|
    3. View stats
    4. View following ({str(len(json.loads(user.following_list_dic_json)))})\n
    |-------|Configuration|-------|
    5. Configure targets ({str(len(json.loads(user.targeting_list_dic_json)))} targets configured).
    6. Change daily limit (current: {str(user.actions_per_day)}) [recomended: 200]
    7. Change wait time after clicking buttons ({str(user.wait_after_click)}s)
    8. Change following/followers lists requests max size (current: {str(user.instagrapi_max_list_query)}) [recomended: 200]\n
    |-------|Actions|-------|
    9. Mass unfollow everyone, including your friends  
    10. Mass follow (by target)
    11. Mass unfollow (followed by using this app)
    12. Configure automatic actions [{str(user.scheduled_enabled)}]\n
    |-------|Configuration (Warning)|-------|
    99. Delete'''
    text9='    0. Back'


    print(text)
    print(text9)

    if back_username_op:
        op = back_username_op
    else:
        op = get_input('\nOption: ')
    os.system('cls')    

    if op == 1:
        print("Note that this changes are NOT applied to your instagram account.")
        print("Current username: " + user.username)
        op = str(input("\nNew username: @"))
        user.username = op
        user.saveInstance()
        input("\nContinue?\n")
        menu_manage_accounts(user.username)
    elif op==2:
        print("Note that this changes are NOT applied to your instagram account.")
        op = str(input("\nNew password: "))
        user.password = op
        user.saveInstance()
        input("\nContinue?\n")
        menu_manage_accounts(back_username=user.username)
    elif op==3:
        info = controller.get_bot_info(user)
        print(info)
        input("\nContinue?\n")
        menu_manage_accounts(user.username)
    elif op == 4:
        following_dic: dict = json.loads(user.following_list_dic_json)
        if not following_dic:
            print("\nYou don't follow anyone with this app")
            input("\nContinue?\n")
            menu_manage_accounts(user.username)
        print('Accounts you follow using this app:\n')
        i=0
        keys = following_dic.keys()
        for key in keys:
            i+=1
            print(str(i)+'. '+'@'  + following_dic[key])
        input("\nContinue?\n")
        menu_manage_accounts(user.username)
    elif op == 5:        
        text = '''A target account is an instagram account whose followers will be followed. If you have more than one target, they will be selected randomly.
        
        1. Add target
        2. Remove target
        3. Display targets
        0. Back'''
        print(text)
        op = get_input('\nOption: ')
        os.system('cls')
        
        if(op == 1):
            tar = input("Enter target to add: @")
            if(tar=='0'):
                menu_manage_accounts(user.username,5)
            user.target_add(tar)
            input("Continue")
            menu_manage_accounts(user.username,5)
        if(op == 2):
            print('Select wich target to remove:\n')
            user_targets_dict: dict = json.loads(user.targeting_list_dic_json)
            if not user_targets_dict:
                print('You have no targets selected.')
                input('Continue')
                menu_manage_accounts(user.username,5)
            iterator=1
            asociacion=[]
            ids = user_targets_dict.keys()
            for target_id in ids:
                text = f'{str(iterator)}. @{user_targets_dict.get(target_id)}'
                print(text)
                asociacion.append((iterator,target_id))
                iterator+=1
            selected = get_input('\nOption: ')
            if selected==0:
                menu_manage_accounts(user.username,5)
            selected-=1
            target_id = asociacion[selected][1]
            
            user.target_remove(target_id)

            input("Continue")
            menu_manage_accounts(user.username,5)
        if(op == 3):
            print("\nTarget list:\n")
            targets_list=json.loads(user.targeting_list_dic_json)
            i=0
            for target in targets_list:
                i+=1
                print(str(i)+'. @'+targets_list[target])
            input("\nAll targets listed. Continue?")
            menu_manage_accounts(user.username,5)
        if(op ==0):
            menu_manage_accounts(user.username)
        user.saveInstance()

        menu_manage_accounts(user.username)

    elif op==6:
        print('Your daily limit is ' + str(user.actions_per_day) + ' and your currently avaliable actions are ' + str(user.tokens))
        lim = get_input('Enter new limit (0 for cancel): ')
        if lim<=0:
            menu_manage_accounts(user.username)
        user.actions_per_day = lim
        user.tokens = lim
        user.saveInstance()
        print('\nDaily limit changed.\n')
        input("Continue")
        menu_manage_accounts(user.username)

    elif op==7:
        print('\nCurrent waiting time is: ' + str(user.wait_after_click) + ' seconds.')
        lim = float(input('Enter new time (0 for cancel): '))
        if lim<=0:
            menu_manage_accounts(user.username)
        user.wait_after_click=lim
        user.saveInstance()
        input('waiting changed to ' + str(lim) + ' seconds. Continue?')
        menu_manage_accounts(user.username)
    elif op==8:
        print('\nCurrent max list size if: ' + str(user.instagrapi_max_list_query))
        lim = int(input('Enter new ammount (0 for cancel): '))
        if lim<=0:
            menu_manage_accounts(user.username)
        user.instagrapi_max_list_query=lim
        user.saveInstance()
        input('Max list size changed to ' + str(lim) + ' continue?')
        menu_manage_accounts(user.username)
    elif op == 9:#2 mass unfollow
        controller.start(user.username, user.password, 1)
        menu_manage_accounts(user.username)

    elif op == 10: #Follow by target
        if len(json.loads(user.targeting_list_dic_json))<=0:
            print('No targets were configured. Please add at least one.')
            input('Continue')
            return
        controller.start(user.username, user.password, 2)
        menu_manage_accounts(user.username)

    elif op == 11: #unfollow by followed in app
        controller.start(user.username, user.password, 3)
        menu_manage_accounts(user.username)

    elif op == 12: #configure automatic actions
        print('Automatic actions configuration.')
        info=f'''
Account info:
    name: {user.username}
    scheduled enabled: {str(user.scheduled_enabled)}
    pending follows: {str(user.scheduled_follows)}
    pending unfollows: {str(user.scheduled_unfollows)}
    daily limit: {str(user.actions_per_day)}
    remaining tokens: {str(user.tokens)}'''
        print(info)
        options=f'''
Options:
    1. Set total follows
    2. Set total unfollows
    3. Enable scheduled actions (the program will also run when you start windows)
    4. Disable scheduled actions
    5. Help
    0. Back
        '''
        print(options)
        op = get_input('Option: ')
                
        if(op==1):
            print('Remember, you need to set at least one target account, for more info select option 5 (help)\n')
            n = get_input('Input how much people will be followed in total (example: 300): ')
            user.scheduled_follows = n
            user.saveInstance()
            target_list = json.loads(user.targeting_list_dic_json)
            if (len(target_list) <= 0 ):
                os.system('cls')
                print('WARNING. No targets selected, you need to set at least one target account. For more info select option 5 (help)')
                input('Continue')
            menu_manage_accounts(user.username,12)
        elif op==2:
            n = get_input('Input how much people will be unfollowed in total (example: 300): ')
            user.scheduled_unfollows = n
            user.saveInstance()
            menu_manage_accounts(user.username,12)
        elif op==3:
            user.scheduled_enabled = True
            controller.windows_create_autostartup()
            user.saveInstance()
            menu_manage_accounts(user.username,12)
        elif op==4:
            user.scheduled_enabled = False
            user.saveInstance()
            menu_manage_accounts(user.username,12)
        elif op==5:
            os.system('cls')
            text=f'''
When activating scheduled actions, this app will automatically start when you start Windows. Then it will perform the desired actions.
For example, if you set the total follows to 400 and total unfollows to 200, the app will prioritize the follows. So, respecting the configured token limit (you can change it in settings, and by default is 200 every 24 hours), it will take 2 days to complete the follow requests (200 and 200) and one more day to complete the unfollow requests. Note that the program only starts unfollowing when all the follow requests are completed.

For the following, there must be a target configured (the target is a user whose followers will be followed, so it's recommended to choose an account with a lot of followers. Also, check that the followers list is not partially limited, since this will generate errors).

For the unfollowing, it just unfollows the people who have been followed by this app, excluding the rest.

If you want to schedule the unfollow of everyone indiscriminately, you can turn on the scheduled_unfollows_everyone option in Automatic actions configuration.
            '''
            print(text)
            input('Continue')
            menu_manage_accounts(user.username,12)
        else:
            menu_manage_accounts(user.username)

    elif op == 99:
        op = get_input('\nThis will get the data of your account deleted from this program. \n\n1. Delete\n2. Cancel\nInput: ')
        if op==1:
            controller.remove_bot(user.username)
            menu()
        else:
            menu_manage_accounts(user.username)

    else:
        menu_manage_accounts()

firstTime = True
def menu():
    os.system('cls')
    if len(sys.argv)>1:
        print(f'Parameter: {str(sys.argv[1])}')
        while(True):
            result = controller.autoStart()
            if(result==404):
                print('Autostart enabled. Waiting for user configuration.')
            sleep(3)
    if config.debug_mode:
        print(f'Startup folder: {config.get_startup_folder()}')
        print(f'Executing from: {config.get_running_path()}')
    print("Welcome.")
    print('Remember: your account must be verified with phone number to avoid blocking. Also 2FA (two factor autentication) has to be disabled in order for this script to work.')
    print(f'All your data will be saved in: \n{config.db_file_path}')
    
    text='''          
    1. Add account
    2. Manage accounts
    3. Enable autostartup
    4. Disable autostartup
    0. Exit'''
    print(text)
    op=0

    op = get_input('\nOption: ')
    os.system('cls')
    
    if (op == 1):
        menu_add_account()
    if (op == 2):
        menu_manage_accounts()
    if (op==3):
        controller.windows_create_autostartup()
        input('continue')
        menu()
    if (op==4):
        controller.windows_remove_autostartup()
        input('continue')
        menu()
    if (op ==0):
        exit()

menu()

