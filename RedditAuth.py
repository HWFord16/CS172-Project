import os
import praw

#load credentials from envrionment variables
CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
USER_AGENT = os.getenv('REDDIT_USER_AGENT')

def authenticate_reddit():
    #use PRAW reddit authenticaion flow
    reddit = praw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        user_agent=USER_AGENT,
    )
    
    return reddit #authenticated sesssion