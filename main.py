from RedditAuth import authenticate_reddit
from Fetch_Process_Data import fetch_posts, process_posts
from DataStorer import DataStorage
from concurrent.futures import ThreadPoolExecutor, as_completed

def crawl_subreddit(subreddit_info):
    subreddit_name, postLimit = subreddit_info
    print(f"\nCrawling subreddit r/{subreddit_name}")

    try:
        # Each thread gets its own Reddit instance
        reddit = authenticate_reddit()

        # Call methods from imported python files/modules
        print(f"Fetching posts for r/{subreddit_name}")
        posts_queue = fetch_posts(reddit, subreddit_name, postLimit)
        print(f"Fetched {len(posts_queue)} posts for r/{subreddit_name}")

        print(f"Processing posts for r/{subreddit_name}")
        processed_posts = process_posts(posts_queue)
        print(f"Processed {len(processed_posts)} posts for r/{subreddit_name}")

        return processed_posts, subreddit_name
    except Exception as e:
        print(f"Failed to process r/{subreddit_name}: {e}")
        return [], subreddit_name

def main():
    postLimit = 10
    subreddits = ['worldnews', 'science', 'space', 'sports', 'food']

    # Tuple list for passing multiple arguments
    subreddit_info = [(subreddit, postLimit) for subreddit in subreddits]

    dataStore = DataStorage()
    all_processed_posts = []

    # Execute multithreading to crawl subreddits in separate threads
    with ThreadPoolExecutor(max_workers=len(subreddits)) as executor:
        future_to_subreddit = {executor.submit(crawl_subreddit, info): info for info in subreddit_info}
        for future in as_completed(future_to_subreddit):
            try:
                processed_posts, subreddit_name = future.result()
                all_processed_posts.append((processed_posts, subreddit_name))
            except Exception as e:
                print(f"Failed to process: {e}")

    # Store data in the main thread
    for processed_posts, subreddit_name in all_processed_posts:
        dataStore.store_data(processed_posts, subreddit_name)
        print(f"Stored data for r/{subreddit_name}")

if __name__ == "__main__":
    main()

