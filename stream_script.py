from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import credentials

class twitter_streamer():
	" Class for streaming and processing live tweets"

	def stream_tweets(self, fetched_data_file, hashtag_list):
		listener = stdout_listener(fetched_data_file)
		auth = OAuthHandler(credentials.CONSUMER_KEY, credentials.CONSUMER_KEY_SECRET)
		auth.set_access_token(credentials.ACCESS_TOKEN, credentials.ACCESS_TOKEN_SECRET)
		stream = Stream(auth, listener)
		stream.filter(track = hashtag_list)


class stdout_listener(StreamListener):

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

if __name__ =='__main__':

	hashtag_list = ["MAGA2020"]
	fetched_data_file = "test.json"

	twitter = twitter_streamer()
	twitter.stream_tweets(fetched_data_file, hashtag_list)