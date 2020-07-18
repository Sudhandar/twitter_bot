from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import credentials
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import sqlalchemy
import json
import pandas as pd
from unidecode import unidecode
from notify_run import Notify


analyzer = SentimentIntensityAnalyzer()

database_username = 'root'
database_password = 'sudhandar'
database_ip = 'localhost'
database_name = 'twitter_streaming'
database_connection = sqlalchemy.create_engine(
   'mysql+pymysql://{0}:{1}@{2}/{3}'.format(
       database_username, database_password,
       database_ip, database_name
   )
)

class listener(StreamListener):

	def on_data(self, data):
		try:
			data = json.loads(data)
			tweet = unidecode(data['text'])
			time_ms = data['timestamp_ms']
			vs = analyzer.polarity_scores(tweet)
			sentiment = vs['compound']
			# print(time_ms, tweet, sentiment)
			df = pd.DataFrame({'date': [time_ms],'tweet':[tweet], 'sentiment':[sentiment]})
			df['date'] = pd.to_datetime(df['date'], unit='ms')
			df['date'] = df['date'].dt.tz_localize('UCT').dt.tz_convert('Asia/Kolkata')
			df['date'] = df['date'].dt.strftime('%Y-%m-%d %H:%M:%S')
			df['date'] = df['date'].astype('datetime64[ns]')

			df.to_sql('sentiment_tweets', con = database_connection, if_exists = 'append', index = False)

		except KeyError as e:
			# print(str(e))
			pass

auth = OAuthHandler(credentials.CONSUMER_KEY, credentials.CONSUMER_KEY_SECRET)
auth.set_access_token(credentials.ACCESS_TOKEN, credentials.ACCESS_TOKEN_SECRET)
notify = Notify()

twitterStream = Stream(auth, listener())
try:
	twitterStream.filter( languages =['en'], track=["a","e","i","o","u"], stall_warnings = True)
except:
	notify.send('App stopped')

