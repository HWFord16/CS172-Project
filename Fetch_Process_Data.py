import re
import requests
import queue
from time import sleep
from bs4 import BeautifulSoup

def clean_html(text):
    #remove HTML tags and unnecessary spaces from a string
    return re.sub('\s+', ' ', re.sub('<.*?>', '', text)).strip()

def fetch_html_title(url):
    #try and get the title of a webpage given a URL from reddit post along with #retry limits
    retries= 3 #max #retries to of URL
    backoff= 1 #time to wait before trying again

    while retries > 0:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                return soup.title.string.strip() if soup.title else 'No title found'
        except requests.exceptions.RequestException:
            retries -= 1  #decrement the number of tries
            sleep(backoff) #wait backoff amount before trying agai
            backoff *= 2  #increase backoff to wait a bit longer if more retires are neeeded
    return 'Failed to retrieve title after 3 attempts'

def fetch_posts(reddit, subreddit_name, limit):
    #retrieve posts from subreddit & store them in a priority queue based on composition of score & comments
    subreddit = reddit.subreddit(subreddit_name)
    post_queue = queue.PriorityQueue()     #deploy a priority for thread-safe operations
    for submission in subreddit.hot(limit=limit): 
        #use the both score(upvotes - downvores) and #comments as a priority measure
        priority = -(submission.score + submission.num_comments) #negative values get more priority
        post_queue.put((priority, submission))
    return post_queue

def process_posts(post_queue):
    #process a list of praw Submission objects into JSON formatted data, including linked HTML titles
    processed_posts = []
    while not post_queue.empty():  #loop through pri queue based on the priority metric
        _, submission = post_queue.get()  #get the post with the highest priority
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

"""Old version of fetching/processing posts as a list"""
# def fetch_posts(reddit, subreddit_name, limit):
#     subreddit = reddit.subreddit(subreddit_name)
#     posts = []
#     for submission in subreddit.hot(limit=limit): 
#         posts.append(submission)
#     return posts

# def process_posts(posts):
#     #process a list of praw Submission objects into JSON formatted data, including linked HTML titles
#     processed_posts = []
#     for submission in posts:
#         post_info = {
#             'id': submission.id,
#             'title': submission.title,
#             'user': submission.author.name if submission.author else 'Anonymous',
#             'body': clean_html(submission.selftext),
#             'comments': [clean_html(comment.body) for comment in submission.comments if hasattr(comment, 'body')],
#             'url': submission.url,
#             'linked_title': fetch_html_title(submission.url) if submission.url and not submission.is_self else ''
#         }
#         processed_posts.append(post_info)
#     return processed_posts