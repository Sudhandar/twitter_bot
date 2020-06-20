from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import credentials
from tweepy import API
from tweepy import Cursor
import pandas as pd 
import numpy as np

class twitter_client():

	def __init__(self, twitter_user = None):
		self.auth = authenticator().authenticate_twitter_app()
		self.twitter_client = API(self.auth)
		self.twitter_user = twitter_user

	def get_twitter_client_api(self):
		return self.twitter_client

	def get_user_timeline_tweets(self,num_tweets):
		tweets = []
		for tweet in Cursor(self.twitter_client.user_timeline, id = self.twitter_user).items(num_tweets):
			tweets.append(tweet)
		return tweets

	def get_friend_list(self,num_friends):
		friend_list = []
		for friend in Cursor(self.twitter_client.friends, id = self.twitter_user).items(num_friends):
			friend_list.append(friend)
		return friend_list

	def get_home_timeline_tweets(self, num_tweets):
		home_timeline_tweets = []
		for tweet in Cursor(self.twitter_client.home_timeline, id = self.twitter_user).items(num_tweets):
			home_timeline_tweets.append(tweet)
		return home_timeline_tweets

class authenticator():

	def authenticate_twitter_app(self):

		auth = OAuthHandler(credentials.CONSUMER_KEY, credentials.CONSUMER_KEY_SECRET)
		auth.set_access_token(credentials.ACCESS_TOKEN, credentials.ACCESS_TOKEN_SECRET)
		return auth


class twitter_streamer():
	" Class for streaming and processing live tweets"

	def __init__(self):
		self.twitter_authenticator = authenticator()

	def stream_tweets(self, fetched_data_file, hashtag_list):
		listener = tweet_listener(fetched_data_file)
		auth = self.twitter_authenticator.authenticate_twitter_app()
		stream = Stream(auth, listener)
		stream.filter(track = hashtag_list)


class tweet_listener(StreamListener):

	def __init__(self, fetched_data_file):
		self.fetched_data_file = fetched_data_file

	def on_data(self,data):
		try:
			print(data)
			with open(self.fetched_data_file, 'a') as tf:
				tf.write(data)
			return True
		except BaseException as e:
			print("Error on data: %s" % str(e))
		return True

	def on_error(self, status):
		print(status)

class tweet_analyzer():

	def tweets_to_dataframe(self, tweets):
		df = pd.DataFrame(data = [tweet.text for tweet in tweets], columns = ['tweets'])
		df['id'] = np.array([tweet.id for tweet in tweets])
		df['len'] = np.array([len([tweet.text]) for tweet in tweets])
		df['date'] = np.array([tweet.created_at for tweet in tweets])
		df['source'] = np.array([tweet.source for tweet in tweets])
		df['likes'] = np.array([tweet.favorite_count for tweet in tweets])
		df['retweets'] = np.array([tweet.retweet_count for tweet in tweets])
		df['location'] = np.array([tweet.geo for tweet in tweets])

		return df


if __name__ =='__main__':

	client = twitter_client()
	analyzer = tweet_analyzer()
	api = client.get_twitter_client_api()
	tweets = api.user_timeline(screen_name="realDonaldTrump", count=20)
	df = tweet_analyzer.tweets_to_dataframe(tweets)
    


