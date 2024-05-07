import os
import praw
from OAuth import OAuthCallback
from TokenManagement import TokenManager
from http.server import HTTPServer

#load credentials from envrionment variables
CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
USER_AGENT = os.getenv('REDDIT_USER_AGENT')

def authenticate_reddit():
    #use PRAW lib token manager after authenticating with reddit
    token= TokenManager()

    #use PRAW reddit authenticaion flow
    reddit = praw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri='http://localhost:8080',
        user_agent=USER_AGENT,
        token_manager=token
    )
    
    #define the scopes for OAuth to generate authentication URL
    #because this is being run from remote bolt server, users must manually open URL to auth (easiet approach)
    scopes = ['read','identity']
    authURL= reddit.auth.url(scopes, 'uniqueKey','permanent')
    print(f"Please copy/paste this URL in your browser to open and and authenticate \n\n {authURL}")

    #start the local HTTP server listening for the OAuth callback/flow to complete
    server = HTTPServer(('localhost',8080),OAuthCallback)
    server.handle_request() #handles one authentication request then shuts down

    #use the code var. in OAuthCallback class to auth and reddit crawling session
    reddit.auth.authorize(OAuthCallback.code)
    
    return reddit #authenticated sesssion

def fetch_posts(reddit):
    print("\nFetching Posts...\n\n")

    #Test the session with retrieving Titles of r/learnPythonsubreddit (limit 25)
    subreddit= reddit.subreddit('learnpython')

    for submissions in subreddit.hot(limit=25):
        print(submissions.title)