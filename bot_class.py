#bot class
from time import sleep
import instagrapi
import random
from instagrapi.exceptions import LoginRequired
import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float,Column, DateTime, Integer,Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import config
import json
import ctimer
import instalog


Base = declarative_base()

class Bot_Account(Base):
    __tablename__='bots'
    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)
    logins = Column(Integer)
    last_login = Column(DateTime)
    tokens = Column(Integer)#remaining actions in the defined time interval. 
    waitUntil = Column(DateTime)#The date when the tokens will be restored to actions_per_day value and 'avaliable' will be set to true
    avaliable = Column(Boolean)#defines if the bot is waiting that time interval.
    total_followed = Column(Integer)#stats
    total_unfollowed = Column(Integer)#stats
    following_list_dic_json = Column(String)#a dictionary {id:username} of the people the user is following with this app
    targeting_list_dic_json = Column(String)#a dictionary {id:username} of the people whose followers will be followed
    actions_per_day=Column(Integer) #how much actions per time interval are allowed
    actions_rest_time=Column(Integer)#wait time interval since you run out of tokens
    wait_after_click = Column(Float)#how much time the bot waits after clicking a button
    scheduled_enabled = Column(Boolean)#sets automatic actions flag (act when the program starts)
    scheduled_follows = Column(Integer)#sets the total number of account that must be followed
    scheduled_unfollows = Column(Integer)#sets the total number of account that must be unfollowed
    scheduled_unfollows_everyone = Column(Boolean)#a bool that defines wether the scheduled unfollow should look at the following_list_json, or just unfollow everyone
    instagrapi_max_list_query = Column(Integer) #limit the followers/following ammount retrieved from instagram (for safety)

    def saveInstance(self):
        session.commit()

    def startClient(self,proxy=False):
        instalog.talk('Starting client...')
        self.client = instagrapi.Client()
        ctimer.wait(4,reason='client')
        instalog.talk(f'Client is {self.client}')
        self.login()
        
    def unfollow_mass(self)->int:
        '''Mass unfollows all your followings'''
        local_following_dict = json.loads(self.following_list_dic_json) 
        instalog.talk('Getting following list...')
        self_followers_dict={}
        try:
            self_followers_dict = self.client.user_following(self.client.user_id,self.instagrapi_max_list_query)
        except Exception as e:
            instalog.talk(f'Error getting following list. {e}')
            return
        instalog.talk(f'following list size: {str(len(self_followers_dict))}')
        user_ids = self_followers_dict.keys()
        result=0
        for user_id in user_ids:
            result = self.unfollow(user_id,local_following_dict)
            ctimer.wait(self.wait_after_click)
            if result:
                return result
        return result
            
    def follow_mass_by_target(self)->int:
        '''Selects a random user from your targets list and starts following its followers'''
        local_following_dict = json.loads(self.following_list_dic_json) 
        #find random target
        target_dic: dict = json.loads(self.targeting_list_dic_json) #load target list
        target_id = random.choice(list(target_dic.keys()))  #select a random target
        #load its followers(optimize)
        instalog.talk(f'Tring to get a follower list (max: {str(self.instagrapi_max_list_query)}) from @{target_dic[target_id]}')
        try:
            foreign_followers = self.client.user_followers(target_id,amount=self.instagrapi_max_list_query)
        except Exception as e:
            instalog.talk(e)
            return 404
        foreign_keys = foreign_followers.keys()
        #call follow for every follower
        for follower_id in foreign_keys:
            result = self.follow(follower_id,local_following_dict)
            ctimer.wait(self.wait_after_click)
            if result:
                return

    def unfollow_mass_followed(self)->int:
        '''Unfollows all the people you have followed using the follow_mass_by_target() method'''
        local_following_dict = json.loads(self.following_list_dic_json) 
        user_ids = local_following_dict.keys()
        #call unfollow for every follower
        for user_id in user_ids:
            result = self.unfollow(user_id,local_following_dict)
            ctimer.wait(self.wait_after_click,reason='Cooldown')
            if result:
                return result

    def login(self):
        """
        Attempts to login to Instagram using either the provided session information
        or the provided username and password.
        """
        instalog.talk(f'Trying to login into {self.username}')

        session=''
        try:
            #session = self.client.load_settings(f'{config.instagrapi_settings_path}.{self.username}')
            pass
        except:
            instalog.talk('No stored session found, trying via username and password.')

        logedin =False
        if session:
            try:
                instalog.talk('Stored session found, trying to log in.')
                self.client.login_by_sessionid(session["authorization_data"]["sessionid"])
                try:
                    self.client.get_timeline_feed()
                    logedin = True
                except LoginRequired:
                    instalog.talk("Session is invalid, need to login via username and password")
            except Exception as e:
                instalog.talk("Couldn't login user using session information: %s" % e)
        if not logedin:
            try:
                self.client.login(self.username,self.password)
                try:
                    self.client.get_timeline_feed()
                    logedin=True
                except:
                    instalog.talk('Invalid login.')
                    return
            except:
                instalog.talk('Error while trying to log in.')
                return
        if logedin:
            ctimer.wait(324,reason='login')
            self.client.dump_settings(f'{config.instagrapi_settings_path}.{self.username}')
            instalog.talk('Logged in.')
            now = datetime.datetime.now()
            self.last_login = now
            self.logins+=1
            self.saveInstance()
        
    def unfollow(self,user_id,local_following_dict:dict): #since the program cannot detect if the user accepted the follow request, try both cases.
        #checks if user can perform actions
        if not ctimer.check_avaliable(self):
            return 200

        #performs unfollow
        user_name = self.client.username_from_user_id(user_id)
        unfollowed=False
        try:
            unfollowed=self.client.user_unfollow(user_id)
        except LoginRequired as e:
            instalog.talk(e)
            self.login()
            return
        except Exception as e:
            instalog.talk(e)
            return
        
        #save stats
        if(unfollowed):
            self.stats_unfollowed(user_id,user_name,local_following_dict)
            self.saveInstance()
        else:
            instalog.talk(f'Error unfollowing {user_id}')
            

    def follow(self,user_id,local_following_dict:dict):
        #checks if user can perform actions
        if not ctimer.check_avaliable(self):
            return 200
        
        #performs follow
        user_name = self.client.username_from_user_id(user_id)
        followed=False
        try:
            followed = self.client.user_follow(user_id)
            followed=True
        except LoginRequired as e:
            instalog.talk(e)
            self.login()
            return
        except Exception as e:
            instalog.talk(e)
            return
        #save stats
        if(followed):
            self.stats_followed(user_id,user_name,local_following_dict)
            self.saveInstance()
        else:
            instalog.talk(f'Error following {user_id}')

    def stats_remove_token(self):
        '''Substracts a token from the bot'''
        self.tokens-=1
        self.saveInstance()

    def stats_unfollowed(self,userId:str,username:str,local_following_dict:dict):
        '''Removes user from following list, also changes the corresponding stats'''
        self.stats_remove_token()
        self.total_unfollowed+=1
        if hasattr(self,"scheduled"):
            if(self.scheduled):
                self.scheduled_unfollows-=1
        instalog.talk(f'Remaining actions: {str(self.tokens)}, unfollowed {username}')
        try:
            new_dic = dict(local_following_dict)
            new_dic.pop(userId)
            self.following_list_dic_json = json.dumps(new_dic)
        except:
            instalog.talk(f'Error removing {username} from the local following list.')
        self.saveInstance()

    def stats_followed(self,userId:str,username:str,local_following_dict:dict):
        '''Adds user to following dic, also changes the corresponding stats'''
        self.stats_remove_token()
        self.total_followed+=1
        if hasattr(self,"scheduled"):
            if(self.scheduled):
                self.scheduled_follows-=1
        instalog.talk(f'Remaining actions: {str(self.tokens)}, followed {username}')

        local_following_dict[userId] = username
        self.following_list_dic_json = json.dumps(local_following_dict)
        self.saveInstance()

    def target_remove(self,user_id:str):
        target_dic: dict = json.loads(self.targeting_list_dic_json) #load target list
        username = target_dic[user_id]
        try:
            target_dic.pop(user_id)
            self.targeting_list_dic_json = json.dumps(target_dic)
            instalog.talk(f'Removed {username} from targeting list.')
            self.saveInstance()
        except:
            instalog.talk(f'Error trying to remove {username} from targeting list.')
        
    def target_add(self,user_name:str):
        if not hasattr(self,"client"):
            instalog.talk('Login is required')
            self.startClient()
            
        else:
            instalog.talk(f'Reusing session {self.client}')

        try:
            text = f'Trying to get @{user_name}\'s account id.'
            print(text)
            user_id = self.client.user_id_from_username(user_name)
        except Exception as e:
            instalog.talk(f'An error ocurred: {e}')
            return
        if not user_id:
            instalog.talk(f'Error obtaining the user_id for @{user_name}.')
            return
        target_dic: dict = json.loads(self.targeting_list_dic_json) #load target list
        try:
            target_dic[user_id] = user_name
            self.targeting_list_dic_json = json.dumps(target_dic)
            instalog.talk(f'Added user {user_id} to targeting list.')
            self.saveInstance()
        except:
            instalog.talk(f'Error trying to add {user_id} to targeting list.')



# Create the SQLAlchemy engine
engine = create_engine(f'sqlite:///{config.db_file_path}')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
