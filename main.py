from RedditAuth import authenticate_reddit, fetch_posts

def main():
    reddit = authenticate_reddit()
    fetch_posts(reddit)


if __name__ == "__main__":
    main()
