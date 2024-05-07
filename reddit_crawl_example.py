import praw
import os

#Authentication credentials Needed to initiate reddit API calls
#Abstracted credentials away in bolt server's ./bashrc file for security purposes
#Retrieve Environment variables from ./bashrc
CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
USER_AGENT = os.getenv('REDDIT_USER_AGENT')


#Set up reddit instance with OAuth2
reddit = praw.Reddit(
  client_id= CLIENT_ID,
  client_secret = CLIENT_SECRET,
  user_agent= USER_AGENT
)

#Test the session with retrieving Titles of r/learnPythonsubreddit (limit 25)
subreddit= reddit.subreddit('learnpython')

for submissions in subreddit.hot(limit=25):
  print(submissions.title)


#Sources: https://praw.readthedocs.io/en/stable/getting_started/quick_start.html