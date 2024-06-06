import re
import requests
import heapq
from time import sleep
from bs4 import BeautifulSoup

def clean_html(text):
    #remove HTML tags and unnecessary spaces from a string
    return re.sub('\s+', ' ', re.sub('<.*?>', '', text)).strip()

def fetch_html_title(url):
    retries = 3  #max number of retries for URL
    backoff = 1  #time to wait before trying again
    timeout_seconds = 10  #timeout for parsing HTML

    while retries > 0:
        try:
            #print(f"Fetching title for URL: {url}")
            response = requests.get(url, timeout=timeout_seconds)  # 10-second timeout for request
            response.raise_for_status()  # Raise an HTTPError on bad status
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string.strip() if soup.title else 'No title found'
            #print(f"Successfully fetched title for URL: {url}")
            return title
        
        except requests.exceptions.Timeout:
            retries -= 1
            print(f"Timeout error for URL: {url}, retries left: {retries}")
        except requests.exceptions.RequestException as e:
            print(f"RequestException: Failed to retrieve title for URL: {url}, error: {e}")
            return 'Failed to retrieve title'
        except Exception as e:
            print(f"Unexpected error: Failed to retrieve title for URL: {url}, error: {e}")
            return 'Failed to retrieve title'
        
        sleep(backoff)
        backoff *= 2
        
    print(f"Failed to retrieve title after 3 attempts for URL: {url}")
    return 'Failed to retrieve title'


def fetch_posts(reddit, subreddit_name, limit):
    try:
        #print(f"\nStarting fetch_posts for r/{subreddit_name}")
        # Retrieve posts from subreddit & store them in a priority queue based on composition of score & comments
        subreddit = reddit.subreddit(subreddit_name)
        post_heap_list = []  # Deploy a list for heapq
        for submission in subreddit.hot(limit=limit):
            # Use both score (upvotes - downvotes) and number of comments as a priority measure
            priority = -(submission.score + submission.num_comments)  # Negative values get more priority
            heapq.heappush(post_heap_list, (priority, submission))  # Push item/post onto heap
        #print(f"Finished fetch_posts for r/{subreddit_name} with {len(post_heap_list)} posts")
        return post_heap_list
    except Exception as e:
        print(f"Failed to fetch posts for r/{subreddit_name}: {e}")
        return []

def process_posts(heap):
    try:
        #print(f"\nStarting process_posts with {len(heap)} posts")
        # Process a list of praw Submission objects into JSON formatted data, including linked HTML titles
        processed_posts = []
        while heap:  # Loop through heapq if items contained within based on the priority metric
            priority, submission = heapq.heappop(heap)  # Pop smallest of heap
            print(f"Processing post ID: {submission.id}, URL: {submission.url}")
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
        #print(f"Finished process_posts with {len(processed_posts)} posts")
        return processed_posts
    except Exception as e:
        print(f"Failed to process posts: {e}")
        return []

