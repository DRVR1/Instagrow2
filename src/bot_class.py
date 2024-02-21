'''
Author: ian vidmar

Description:
    Bot methods and attributes.
    The bot wraps instagrapi functions,
    handles exceptions, and stores its own
    attributes in a database.
'''

# Default modules
import datetime
import functools
from math import ceil
from typing import Union
import os
import json

# Downloaded modules
import instagrapi
from sqlalchemy import create_engine, Column, Integer, String, Float,Column, DateTime, Integer,Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from instagrapi.exceptions import LoginRequired, PleaseWaitFewMinutes, ChallengeRequired, FeedbackRequired, ClientNotFoundError, SubmitPhoneNumberForm, ChallengeUnknownStep
from instagrapi.types import User, UserShort

# Custom modules
import config
import ctimer
import instalog
import iexceptions
from default_settings import default


# Define paths/strings
dataBase_path = config.db_file_path # Example: somefolder/myDatabase.db


# Define database instance
Base = declarative_base()


#Bot class definition (attributes and methods)
class Bot_Account(Base):

    __tablename__='bots'

    '''Attributes section'''
    id = Column(Integer, primary_key=True)
    # Instagram account
    username = Column(String)
    password = Column(String)
    # Stats 
    stats_logins = Column(Integer)
    stats_last_login = Column(DateTime)
    stats_tokens = Column(Integer)#remaining actions in the defined time interval. 
    stats_total_followed = Column(Integer)#stats
    stats_total_unfollowed = Column(Integer)#stats
    # Bot configuration
    config_waitUntil = Column(DateTime)#The date when the tokens will be restored to actions_per_day value and 'avaliable' will be set to true
    config_avaliable = Column(Boolean)#defines if the bot is waiting that time interval.
    config_actions_per_day=Column(Integer) #how much actions per time interval are allowed
    config_actions_rest_time=Column(Integer)#wait time interval since you run out of tokens
    config_wait_range_1 = Column(Float) # Range start for actions cooldown
    config_wait_range_2 = Column(Float) # Range end for actions cooldown
    # Scheduler configuration
    scheduled_enabled = Column(Boolean)#sets automatic actions flag (act when the program starts)
    scheduled_follows = Column(Integer)#sets the total number of account that must be followed
    scheduled_unfollows = Column(Integer)#sets the total number of account that must be unfollowed
    scheduled_unfollows_everyone = Column(Boolean)#a bool that defines wether the scheduled unfollow should look at the following_list_json, or just unfollow everyone
    # Instagrapi configuration
    instagrapi_max_list_query = Column(Integer) # Limit the followers/following ammount retrieved from instagram (for safety)
    #instagrapi_scrapper_chunk_size = Column(Integer) # Ammount of scrapped followers per api request
    # Instagram interactions
    automated_followings_ids = Column(String) # List of users id's (serialized json)
    all_followings_shorts = Column(String) # List of userShort (serialized json)
    all_followers_shorts = Column(String) # List of userShort (serialized json)


    '''Methods section'''
    def create_load_bot(self,username,password=None)->'Bot_Account':
        '''Loads selected bot by username. If the bot doesn't exist, then it will be created and saved as a new bot.'''
        user=session.query(Bot_Account).filter_by(username=username).first()
        if user == None:
            # Create new user object
            '''Creates and saves user. Returns user object after created'''
            user = Bot_Account(
                # Instagram account
                username = username,
                password = password,

                # Stats 
                stats_logins = 0,
                stats_last_login = datetime.datetime.min,
                stats_tokens = 200,
                stats_total_followed = 0,
                stats_total_unfollowed = 0,

                # Bot configuration
                config_waitUntil = datetime.datetime.now(),
                config_avaliable = True,
                config_actions_per_day = 200,
                config_actions_rest_time = 3600*24,
                config_wait_range_1 = 2,
                config_wait_range_2 = 4,

                # Scheduler configuration
                scheduled_enabled = False,
                scheduled_follows = 0,
                scheduled_unfollows = 0,
                scheduled_unfollows_everyone = False,

                # Instagrapi configuration
                instagrapi_max_list_query = 200,
                #instagrapi_scrapper_chunk_size = 30,

                # Instagram interactions
                automated_followings_ids = json.dumps([]),
                all_followings_shorts = json.dumps([]),
                all_followers_shorts = json.dumps([])
            )
            session.add(user)
            session.commit()
        return user
    
    
    def delete_bot(self,username:str):
        '''Deletes bot from database'''
        user=session.query(Bot_Account).filter_by(username=username).first()
        if user:
            session.delete(user)
            session.commit()
        else:
            instalog.error('Error deleting: User ' + username + ' doesn\'t exist')


    def saveInstance(self):
        '''Saves the bot's attributes into the database'''
        session.commit()


    def _startClient(self):
        '''Starts instagrapi client'''
        instalog.talk('Starting client...')
        self.client = instagrapi.Client()
        instalog.talk(f'Client is {self.client}')
    

    def follow_mass(self,accounts:list[Union[User,UserShort]])->bool:
        '''
            - Input: list of User/Usershort
            
            - Logic: Follows everyone on the list

            - Output: status code
        '''
        for user in accounts:
            followed = self.follow(user_id=user.pk)
            if not followed:
                pass
            

    def unfollow_mass(self,accounts:list[Union[User,UserShort]])->bool:
        '''
            - Input: list of User/Usershort
            
            - Logic: Unfollows everyone on the list

            - Output: status code
        '''
        for user in accounts:
            unfollowed = self.unfollow(user_id=user.pk)
            if not unfollowed:
                pass


    def _dump_json_wrap(action):
        @functools.wraps(action)  
        def wrapper(self:'Bot_Account',*args,**kwargs):
            dic_or_diclist = action(self,*args,**kwargs)

            # Debug:
            if config.debug_mode:
                pks = []
                repeated = 0
                diclist_size = str(len(dic_or_diclist))
                instalog.debug(f'dict list size is {diclist_size}')
                for item in dic_or_diclist:
                    pk = item['pk']
                    instalog.debug(f"pk is: {pk}")
                    if not pk in pks:
                        pks.append(pk)
                    else:
                        instalog.debug(f'pk: {pk} was already in list!')
                        repeated+=1
                instalog.debug(f"Repeated users: {str(repeated)}")

            jsonStr = json.dumps(dic_or_diclist,indent=4,default=str)
            save_path = kwargs.get('save_path')
            if save_path:
                with open(save_path, 'w') as json_file:
                    json_file.write(jsonStr)
                    json_file.close()
            else:
                return jsonStr
        return wrapper  


    @_dump_json_wrap
    def dump_user_obj_to_json(self,user:Union[User,UserShort],save_path:str=False) -> dict:
        '''Converts User or UserShort instagrapi Object into a formatted json string'''
        return user.model_dump()


    @_dump_json_wrap
    def dump_userList_to_json(self,UserList:list[Union[User,UserShort]],save_path:str=False) -> list[dict]:
        '''Converts User or UserShort LIST into a formatted json string'''
        return [short.model_dump() for short in UserList]
    

    @_dump_json_wrap
    def merge_user_list(self,pathlist:str,save_path:str=False) -> list[UserShort]:
        '''
           Input: two paths of dumped json userList
           Output: one json with the merged follower lists

           if save_path is not provided, returns formated json string
           else, saves the json in the provided path
        '''

        final_set = set({})

        # O(len(pathlist) * len(a_set))
        for path in pathlist:
            a_set = set(self.retrieve_json_UserShortList(path))
            final_set.update(a_set) # o(m)

        final_list = list(final_set)
        return [short.model_dump() for short in final_list]


    def _retrieve_json_wrap(action):
        @functools.wraps(action)  
        def wrapper(self:'Bot_Account',save_path:str,*args,**kwargs):
            retrieved = ''
            with open(save_path, 'r') as json_file:
                retrieved = json.load(json_file)
                json_file.close()
            return action(self,save_path,*args,_retrieved=retrieved,**kwargs)
        return wrapper  
    
    
    @_retrieve_json_wrap
    def retrieve_json_UserShortList(self,save_path:str,_retrieved=False)->list[UserShort]:
        '''retrieve a dumped userlist json (only for UserShort)'''

        diclist = _retrieved
        
        shortlist = []
        for dic in diclist:
            short = UserShort(**dic)
            shortlist.append(short)
        return shortlist


    @_retrieve_json_wrap
    def retrieve_json_User(self,save_path:str,_retrieved=False)->User:
        '''retrieve a dumped User json (only for single User)'''

        dic = _retrieved
        user = User(**dic)
        return user


    def _action_wrap(action):
        '''
           Wrapper for bot actions that can result in an exception, for example instagram blocking you into solving a captcha.
           Serious exceptions will cause the wrapped function to return False.
        '''
        @functools.wraps(action)  
        def wrapper(self:'Bot_Account',*args,**kwargs):
            #check if bot is avaliable
            if not ctimer.check_avaliable(self):
                return 200
            #try to perform action trough instagrapi
            try:
                result = action(self,*args,**kwargs)
                if not kwargs.get('disable_wait'):
                    instalog.talk(f'Action finished. Remaining tokens: [{str(self.stats_tokens)}]')
                    ctimer.wait(self.config_wait_range_1,self.config_wait_range_2)
            except LoginRequired as e:
                return iexceptions.loginrequired(self,e)
            except PleaseWaitFewMinutes as e:
                return iexceptions.PleaseWaitFewMinutes(self,e)
            except ChallengeRequired as e:
                return iexceptions.ChallengeRequired(self,e)
            except FeedbackRequired as e:
                return iexceptions.FeedbackRequired(self,e)
            except ClientNotFoundError as e:
                return iexceptions.ClientNotFoundError(self,e)
            except SubmitPhoneNumberForm as e:
                return iexceptions.SubmitPhoneNumberForm(self,e)
            except ChallengeUnknownStep as e:
                return iexceptions.ChallengeUnknownStep(self,e)
            except Exception as e:
                return iexceptions.unhandled(e)
            if result:
                return result
            else:
                return False
        return wrapper
    

    def print_final_scrapped(self, final_user_list:list, cursor_max:str)->None:
        instalog.talk(f'Total followers retrieved: {str(len(final_user_list))}, last cursor: {cursor_max}')


    def _mass_scrape_wrap(action):
        @functools.wraps(action)  
        def wrapper(self:'Bot_Account',*args,**kwargs):

            user_id = args[0]
            follower_count = args[1]

            final_user_list = []
            cursors = []
            cursor_errors = 0
            cursor_max = ''

            max_followers = kwargs.get('max_followers')
            if not max_followers:
                max_followers=400

            # Adjust total requested followers if it exceeds the original follower count
            if max_followers > follower_count:
                max_followers = follower_count

            chunk_size = kwargs.get('chunk_size')
            if not chunk_size:
                chunk_size=20

            # Adjust chunk size if requested followers are under the chunk size
            if max_followers < chunk_size:
                chunk_size = max_followers

            cursor = kwargs.get('cursor')
            if not cursor:
                cursor=''

            # Ceil: round up
            chunk_ammount = ceil(max_followers/chunk_size)

            i = 0

            debt = 0
            while i < chunk_ammount:
                instalog.talk(f'Total chunks: {str(chunk_ammount)}, size of each: {str(chunk_size)}, follower/ing count: {str(follower_count)}, user id: {user_id}')
                instalog.talk(f'Chunk number: [{str(i)}] Chunk Size: [{str(chunk_size)}] Scrapping...')
                try:
                    userlist, cursor_max = action(self,user_id,follower_count,chunk_size=chunk_size,cursor=cursor,max_followers=max_followers)
                except PleaseWaitFewMinutes as e:
                        instalog.talk(f"Instagram says: {e}")
                        ctimer.wait(60,120,"Cooldown")
                        self.client.logout()
                        self.login(disable_wait=True)
                        continue
                except Exception as e:
                    # If at least one chunk was retrieved, return it, and the cursor
                    if i>=1:
                        instalog.error(f'An exception has occurred: {e}')
                        self.print_final_scrapped(final_user_list,cursor_max)
                        return final_user_list, cursor
                    # If no chunk was retrieved, pass exception to the exception handler 
                    else:
                        raise

                instalog.debug(f'followers got: [{str(len(userlist))}], returned cursor: [{str(cursor_max)}]')

                # Cursor fix (Experimental)
                if cursor_max in cursors:
                    instalog.debug(f'Cursor was the same. Repeating request...')
                    cursor_errors += 1
                    if cursor_errors >= 3:
                        instalog.debug(f'3 Cursor errors. Breaking loop')
                        break
                    continue
                cursors.append(cursor_max)
                cursor = cursor_max

                # Loop iteration
                i+=1

                # Add obtained followers (UserShort) to the existing list
                final_user_list+=userlist 

                # Instagram sabottaging our userlist (length varies randomly)
                total_retrieved_users_len = len(final_user_list)
                remaining_users = max_followers - total_retrieved_users_len

                # Calculate debt (Extra followers)
                if not userlist == chunk_size:
                    diff = len(userlist) - chunk_size 
                    debt += diff
                    instalog.debug(f"Debt: {str(debt)}")

                # Case 1 (less): add chunks if debt is less than negative chunk size
                if debt < -chunk_size:
                    add = debt // -chunk_size
                    chunk_ammount += add
                    instalog.debug(f"Chunk size is not enough to cover user ammount. Adding a new chunk. Chunk ammount: {str(chunk_ammount)}")
                    debt += add * chunk_size

                # Case 2 (extra): remove chunks if required (if debt reached a chunk size, remove a chunk)
                if debt >= chunk_size:
                    subs = debt // chunk_size
                    chunk_ammount -= subs
                    instalog.debug(f'Debt of {str(debt)} reached a chunk size. Removing {str(subs)} chunks')
                    debt -= subs * chunk_size

                # Special case: add a chunk at the end if debt is pending
                if debt < 0 and chunk_ammount == i:
                    chunk_ammount +=1
                    
                # Sleep for every iteration
                ctimer.wait(self.config_wait_range_1,self.config_wait_range_2)


            # Clear repeated followers (experimental). Time complexity: o(n)
            final_user_list = set(final_user_list)
            final_user_list = list(final_user_list)

            # Clean exceded followers (old)
            '''
            total = len(final_user_list)
            if total > max_followers:
                diff = total - max_followers
                instalog.debug(f'Cleaning exceded (removing last {str(diff)} users)')
                del final_user_list[-diff:]
            '''
            
            # Print scrapped info
            self.print_final_scrapped(final_user_list,cursor_max)

            # Return the requested userlist when loop ends
            return final_user_list
        return wrapper


    @_action_wrap
    @_mass_scrape_wrap
    def scrape_followers(self,user_id:str,follower_count:int,*args,chunk_size=50,cursor='',max_followers=400,**kwargs) -> Union[list[UserShort],tuple]:
        '''
            - user_id: the user id whose followers will be extracted
            - follower_count: total follower ammount of the target (required, otherwise the loop wont stop requesting
              chunks
            - chunk_size: ammount of followers to receive per request (default and recomended: 190)
            - cursor: position in the follower list, so you don't request always the same chunk of followers (default: empty string)
            - max_followers: total ammount of followers you request to get (default: 400)

            If worked as expected, returns list[UserShort]

            If instagram interrupts the process, returns the tuple: (list[UserShort], cursor) so you can save the cursor and continue
            scrapping where you left it.

            Note: in this particular case, "followers" means followers or followings.
        '''
        userlist, cursor_max = self.client.user_followers_v1_chunk(user_id,max_amount=chunk_size,max_id=cursor)
        return userlist, cursor_max
    

    @_action_wrap
    @_mass_scrape_wrap
    def scrape_following(self,user_id:str,follower_count:int,*args,chunk_size=50,cursor='',max_followers=400,**kwargs) -> Union[list[UserShort],tuple]:
        '''
            - user_id: the user id whose followers will be extracted
            - follower_count: total follower ammount of the target (required, otherwise the loop wont stop requesting
              chunks
            - chunk_size: ammount of followers to receive per request (default and recomended: 190)
            - cursor: position in the follower list, so you don't request always the same chunk of followers (default: empty string)
            - max_followers: total ammount of followers you request to get (default: 400)

            If worked as expected, returns list[UserShort]

            If instagram interrupts the process, returns the tuple: (list[UserShort], cursor) so you can save the cursor and continue
            scrapping where you left it.

            Note: in this particular case, "followers" means followers or followings.
        '''
        userlist, cursor_max = self.client.user_following_v1_chunk(user_id,max_amount=chunk_size,max_id=cursor)
        return userlist, cursor_max


    @_action_wrap
    def scrape_account_data(self,username:str)->User:
        '''
           - If Fjson = False (default), returns User object
           - If Fjson = True, returns formated json string
        '''
        return self.client.user_info_by_username_v1(username)


    @_action_wrap
    def follow(self,*args,user_id:str,**kwargs)->bool:
        '''Follows provided userId'''
        followed = self.client.user_follow(user_id)
        if followed:
            self._register_followed(userId=user_id)
            return True


    @_action_wrap
    def unfollow(self,*args,user_id:str,**kwargs)->bool:
        '''Unfollows provided userId'''
        unfollowed = self.client.user_unfollow(user_id)
        if unfollowed:
            self._register_unfollowed(userId=user_id)
            return True


    def _action_stats_wrap(func):
        @functools.wraps(func) 
        def wrapper(self:'Bot_Account',*args,**kwargs):
            self.stats_tokens-=1
            result = func(self,*args,**kwargs)
            self.saveInstance()
        return wrapper
    

    @_action_stats_wrap
    def _register_followed(self,*args,**kwargs):
        '''KWARG_required: (userId:str)'''
        '''Adds @user to the local following list'''
        self.stats_total_followed+=1
        userId=kwargs.get('userId')
        try:
            followings_list = list(json.loads(self.automated_followings_ids))
            followings_list.append(userId)
            self.automated_followings_ids = json.dumps(followings_list)
        except:
            instalog.error(f"Error adding user [{str(userId)}] to automated following list")


    @_action_stats_wrap
    def _register_unfollowed(self,*args,**kwargs):
        '''KWARG_required: (userId:str)'''
        '''Removes @user from the local following list'''
        self.stats_total_unfollowed+=1
        userId=kwargs.get('userId')
        try:
            followings_list = list(json.loads(self.automated_followings_ids))
            followings_list.remove(userId)
            self.automated_followings_ids = json.dumps(followings_list)
        except:
            instalog.error(f"Error removing user [{str(userId)}] from automated following list")


    def check_login(self)->bool:
        '''Check if self is logged in'''
        instalog.talk('Checking login...')
        logedin = False
        if not hasattr(self,"client"):
            instalog.talk('No client was started..')
            return logedin
        try:
            self.client.get_timeline_feed()
            instalog.talk('Login confirmed...')
            logedin = True
        except:
            instalog.talk('Not loged in...')
            logedin = False

        return logedin
    

    def _default_settings(self):
        '''Reset bot's settings, keeping the same
           random UUIDS and default device info
        '''
        # Keep old random UuIDs before resseting
        old_phone_id = self.client.phone_id
        old_uuid = self.client.uuid
        old_client_session_id = self.client.client_session_id
        old_advertising_id = self.client.advertising_id
        old_android_device_id = self.client.android_device_id
        old_request_id = self.client.request_id
        old_tray_session_id = self.client.tray_session_id
        device = default.device_settings
        agent = default.user_agent
        country = default.country
        country_code = default.country_code
        locale = default.locale
        timezone_offset = default.timezone_offset

        self.client.set_settings({})

        self.client.device_settings = device
        self.client.user_agent = agent
        self.client.country = country
        self.client.country_code = country_code
        self.client.locale = locale
        self.client.timezone_offset = timezone_offset

        self.client.phone_id = old_phone_id
        self.client.uuid = old_uuid
        self.client.client_session_id = old_client_session_id
        self.client.advertising_id = old_advertising_id
        self.client.android_device_id = old_android_device_id
        self.client.request_id = old_request_id
        self.client.tray_session_id = old_tray_session_id


    @_action_wrap
    def login(self,disable_wait:bool=False) -> bool:
        """
            - Attempts to login to Instagram using either the provided session information
              or the provided username and password.
        """

        if not hasattr(self,"client"):
            self._startClient()
        else:
            if self.check_login():
                return True
            
        instalog.talk(f'Trying to login into {self.username}')

        session=''
        try:
            session = self.client.load_settings(config.get_instagrapi_settings_path(self.username))
            instalog.talk('Stored session found, reusing session...')
        except:
            instalog.talk('No stored session found, trying via username and password.')
            if not os.path.exists(config.get_instagrapi_settings_path(self.username)):
                instalog.talk("Loading custom default settings from 'default_settings.py'")
                self._default_settings()

                
        login_via_session = False
        login_via_pw = False

        if session:
            try:
                self.client.set_settings(session)
                self.client.login(self.username,self.password)

                # Check if session is valid
                if not self.check_login():
                    instalog.talk("Session is invalid, need to login via username and password")
                    
                    self._default_settings()

                    self.client.login(self.username, self.password)
                    self.check_login()
                    login_via_session = True
                login_via_session = True
            except Exception as e:
                instalog.talk("Couldn't login user using session information: %s" % e)

        if not login_via_session:
            instalog.talk("Attempting to login via username and password. username: %s" % self.username)
            if self.client.login(self.username, self.password):
                self.check_login()
                login_via_pw = True

        if not login_via_pw and not login_via_session:
            instalog.error("Couldn't login user with either password or session")
            return False
        
        self.client.dump_settings(config.get_instagrapi_settings_path(self.username))
        now = datetime.datetime.now()
        self.stats_last_login = now
        self.stats_logins+=1
        self.saveInstance()
        return True


# Create the SQLAlchemy engine
engine = create_engine(f'sqlite:///{dataBase_path}')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()