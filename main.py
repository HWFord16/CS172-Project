from RedditAuth import authenticate_reddit
from Fetch_Process_Data import fetch_posts, process_posts
from DataStorer import DataStorage

def main():
    postLimit = 50
    reddit = authenticate_reddit()
    subreddits = ['worldnews','science','space','sports','food','gadgets']
    dataStore = DataStorage()

    for subreddit in subreddits:
        print("\nCrawling for post")
        posts= fetch_posts(reddit,subreddit,postLimit)
        processedPosts= process_posts(posts)
        dataStore.store_data(processedPosts,subreddit)
        print("Fetched,Processed & Stored Post")

if __name__ == "__main__":
    main()
