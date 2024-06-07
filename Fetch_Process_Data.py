import re
import requests
import heapq
from time import sleep
from bs4 import BeautifulSoup

def clean_html(text):
    # Remove HTML tags and unnecessary spaces from a string
    return re.sub('\s+', ' ', re.sub('<.*?>', '', text)).strip()

def fetch_html_title(url):
    retries = 3  # Max number of retries for URL
    backoff = 1  # Time to wait before trying again
    timeout_seconds = 10  # Timeout for parsing HTML
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    while retries > 0:
        try:
            print(f"Fetching title for URL: {url}")
            response = requests.get(url, headers=headers,timeout=timeout_seconds)  # 10-second timeout for request
            response.raise_for_status()  # Raise an HTTPError on bad status
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string.strip() if soup.title else 'No title found'
            print(f"Successfully fetched title for URL: {url}")
            return title
        except requests.exceptions.Timeout:
            retries -= 1
            print(f"\nTimeout error for URL: {url}, retries left: {retries}")
        except requests.exceptions.RequestException as e:
            print(f"\nRequestException: Failed to retrieve title for URL: {url}, error: {e}")
            return 'Failed to retrieve title'
        except Exception as e:
            print(f"\nUnexpected error: Failed to retrieve title for URL: {url}, error: {e}")
            return 'Failed to retrieve title'
        
        sleep(backoff)
        backoff *= 2
        
    print(f"\nFailed to retrieve title after 3 attempts for URL: {url}")
    return 'Failed to retrieve title'

def fetch_posts(reddit, subreddit_name, limit):
    try:
        post_heap_list = [] #list for heapq
        sections = [        #sort options on subreddits to crawl
            ('hot', None),
            ('new', None),
            ('top', 'all'),('top', 'year'),('top', 'month'),
            ('controversial', 'all'),('controversial', 'year'),('controversial', 'month'),
            ('rising', None)
        ]

        # Retrieve posts from subreddit & store them in a priority queue based on composition of score & comments
        for section, time_filter in sections:
            subreddit = getattr(reddit.subreddit(subreddit_name), section)
            if time_filter:
                submissions = subreddit(time_filter=time_filter, limit=limit)
            else:
                submissions = subreddit(limit=limit)

            for submission in submissions:
                # Use both score (upvotes - downvotes) and number of comments as a priority measure
                priority = -(submission.score + submission.num_comments)  # Negative values get more priority
                heapq.heappush(post_heap_list, (priority, submission.id, submission)) # Push item/post onto heap
                
                #break out of loop if post-limit is met
                if len(post_heap_list) >= limit:
                    break
            if len(post_heap_list) >= limit:
                break
        
        #print(f"\nStarting fetch_posts for r/{subreddit_name}")
        # Retrieve posts from subreddit & store them in a priority queue based on composition of score & comments
        subreddit = reddit.subreddit(subreddit_name)
        post_heap_list = []  # Deploy a list for heapq
        for submission in subreddit.hot(limit=limit):
            # Use both score (upvotes - downvotes) and number of comments as a priority measure
            priority = -(submission.score + submission.num_comments)  # Negative values get more priority
            heapq.heappush(post_heap_list, (priority, submission.id, submission))  # Push item/post onto heap
        #print(f"Finished fetch_posts for r/{subreddit_name} with {len(post_heap_list)} posts")
    except Exception as e:
        print(f"\nFailed to fetch posts for r/{subreddit_name}: {e}")
    return post_heap_list

def process_posts(heap):
    try:
        processed_posts = []
        while heap:   # Loop through heapq if items contained within based on the priority metric
            print(f"\nStarting process_posts with {len(heap)} posts")
            #Process a list of praw Submission objects into JSON formatted data, including linked HTML titles
            priority, submission_id, submission = heapq.heappop(heap)  # Pop smallest of heap
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
            print(f"Finished process_posts with {len(processed_posts)} posts")
    except Exception as e:
        print(f"\nFailed to process posts {submission.id}: {e}")
    
    return processed_posts
