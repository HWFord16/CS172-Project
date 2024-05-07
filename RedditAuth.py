import os
import praw
import logging

#Set up logging
logging.basicConfig(level=logging.INFO)

def authenticate_reddit():
    try:
        #load credentials from envrionment variables
        CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
        CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
        USER_AGENT = os.getenv('REDDIT_USER_AGENT')
        
        #use PRAW reddit authenticaion flow
        reddit = praw.Reddit(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            user_agent=USER_AGENT,
        )
        return reddit #authenticated sesssion
    except Exception as e:
        logging.error(f"Failed to authenticate with Reddit: {e}")
        raise #re-raise exception for log