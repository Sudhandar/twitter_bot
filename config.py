import tweepy

auth = tweepy.OAuthHandler("r87jHGXvcPRblfhXqaH5glq4y", "WglJmIk35AQJHaWEs7HD9gnpIfDwsDXMwwJ04nE8Ymgp0nDAMJ")
auth.set_access_token("340326969-qY4NhaaqZYR7TXyyUFLX6h9jVa8sMWJP51yqKZwR", "75HdqggKrimXjwxoEhCxYGGBB0I7kWk26809jrcOVRAu9")

# Create API object
api = tweepy.API(auth, wait_on_rate_limit=True,
    wait_on_rate_limit_notify=True)
