from RedditAuth import authenticate_reddit
from Fetch_Process_Data import fetch_posts, process_posts
from DataStorer import DataStorage
from concurrent.futures import ThreadPoolExecutor


def crawl_subreddit(reddit,subreddit_name,postLimit,dataStore):
    print(f"\nCrawling subreddit {subreddit_name} for posts")
    #Call methods from imported python files/modules
    posts_queue = fetch_posts(reddit, subreddit_name, postLimit)
    processed_posts = process_posts(posts_queue)
    dataStore.store_data(processed_posts, subreddit_name)
    print(f"Fetched, Processed & Stored {subreddit_name}'s Posts")

def main():
    postLimit = 50
    reddit = authenticate_reddit()
    subreddits = ['worldnews','science','space','sports','food','gadgets']
    dataStore = DataStorage()
    
    #execute multithreading to crawl subreddit in separate threads
    with ThreadPoolExecutor(max_workers=len(subreddits)) as executor:
        subreddit_threads = [executor.submit(crawl_subreddit, reddit, subreddit, postLimit, dataStore) for subreddit in subreddits]
        
        #wait for all threads to complete, report any errors, synch with main thread
        for thread in subreddit_threads: 
            thread.result()

    """Old version crawling w/o multi-threading- sequential"""
    # for subreddit in subreddits:
    #     print("\nCrawling subreddit for posts")
    #     posts= fetch_posts(reddit,subreddit,postLimit)
    #     processedPosts= process_posts(posts)
    #     dataStore.store_data(processedPosts,subreddit)
    #     print("Fetched,Processed & Stored Subreddit's Posts")

if __name__ == "__main__":
    main()
