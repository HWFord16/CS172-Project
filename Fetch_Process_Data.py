import re
import requests
import queue
import heapq
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
            response = requests.get(url,timeout=10) #10 second timeout
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                return soup.title.string.strip() if soup.title else 'No title found'
        except requests.exceptions.RequestException as e:
            retries -= 1  #decrement the number of tries
            sleep(backoff) #wait backoff amount before trying again
            backoff *= 2  #increase backoff to wait a bit longer if more retires are neeeded
            if retries == 0:
                print(f"Failed to retrieve title after 3 attempts: {e}")
    return 'Failed to retrieve title'

def fetch_posts(reddit, subreddit_name, limit):
    #retrieve posts from subreddit & store them in a priority queue based on composition of score & comments
    subreddit = reddit.subreddit(subreddit_name)
    post_heapList= []                                #deploy a list for heapq
    for submission in subreddit.hot(limit=limit): 
        #use the both score(upvotes - downvores) and #comments as a priority measure
        priority = -(submission.score + submission.num_comments) #negative values get more priority
        heapq.heappush(post_heapList,(priority,submission)) #push item/post onto heap
    return post_heapList

def process_posts(heap):
    #process a list of praw Submission objects into JSON formatted data, including linked HTML titles
    processed_posts = []
    while heap: #loop through heapq if items contained within based on the priority metric
        priority, submission = heapq.heappop(heap)  #pop smallest of heap
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