import praw
import json
import re
import requests
from bs4 import BeautifulSoup

def clean_html(text):
    #remove HTML tags and unnecessary spaces from a string
    return re.sub('\s+', ' ', re.sub('<.*?>', '', text)).strip()

def fetch_html_title(url):
    #try and get the title of a webpage given a URL from reddit post
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup.title.string.strip() if soup.title else 'No title found'
    except requests.exceptions.RequestException:
        return 'Failed to retrieve title'
    
def fetch_posts(reddit, subreddit_name, limit):
    subreddit = reddit.subreddit(subreddit_name)
    posts = []
    for submission in subreddit.hot(limit=limit): 
        posts.append(submission)
    return posts

def process_posts(posts):
    #process a list of praw Submission objects into JSON formatted data, including linked HTML titles
    processed_posts = []
    for submission in posts:
        post_info = {
            'id': submission.id,
            'title': submission.title,
            'user': submission.author.name if submission.author else 'Anonymous',
            'body': clean_html(submission.selftext),
            'comments': [clean_html(comment.body) for comment in submission.comments if hasattr(comment, 'body')],
            'url': submission.url,
            'linked_title': fetch_html_title(submission.url) if submission.url and not submission.is_self else ''
        }
        processed_posts.append(post_info)
    return processed_posts