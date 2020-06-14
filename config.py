import tweepy

auth = tweepy.OAuthHandler("eEGwOmCSyGHHq3WvPkr3yQ4jR", "yoaD1IHSpsi64bzl4jrA9UCsUAULbYbUdbcmPC5jgh6cHdQa1i")
auth.set_access_token("1272135393878503424-Gf9rbA6gfpyRIdvZ2FMpbOViEjck2m", "FGm6D3NpNrbP5hjTF0Cabpussd4gzn1nfoQxkOPLe5pHH")

# Create API object
api = tweepy.API(auth, wait_on_rate_limit=True,
    wait_on_rate_limit_notify=True)
api.update_status("Test tweet from Tweepy Python")
