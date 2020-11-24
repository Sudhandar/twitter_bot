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
from geopy.geocoders import Nominatim

analyzer = SentimentIntensityAnalyzer()

database_username = 'root'
database_password = ''
database_ip = 'localhost'
database_name = 'twitter_streaming'
database_connection = sqlalchemy.create_engine(
   'mysql+pymysql://{0}:{1}@{2}/{3}'.format(
       database_username, database_password,
       database_ip, database_name
   )
)

geolocator = Nominatim(user_agent="app")

class listener(StreamListener):

	def on_data(self, data):
		try:
			data = json.loads(data)
			if data['user']['location']!=None:
				location = geolocator.geocode(data['user']['location'])
				if location != None:
					if (-141<location.longitude<-67):
						tweet = unidecode(data['text'])
						time_ms = data['timestamp_ms']
						vs = analyzer.polarity_scores(tweet)
						latitude = location.latitude
						longitude = location.longitude
						sentiment = vs['compound']
						df = pd.DataFrame({'date': [time_ms],'tweet':[tweet], 'sentiment':[sentiment],'latitude':[latitude],'longitude':[longitude]})
						df['date'] = pd.to_datetime(df['date'], unit='ms')
						df['date'] = df['date'].dt.strftime('%Y-%m-%d %H:%M:%S')
						df['date'] = df['date'].astype('datetime64[ns]')
						df.to_sql('sentiment_tweets', con = database_connection, if_exists = 'append', index = False)
					else:
						pass
				else:
					pass
			else:
				pass
		except Exception as e:
			with open('errors.txt','a') as f:
				print(str(e))
				f.write(str(e))
				f.write('\n')

auth = OAuthHandler(credentials.CONSUMER_KEY, credentials.CONSUMER_KEY_SECRET)
auth.set_access_token(credentials.ACCESS_TOKEN, credentials.ACCESS_TOKEN_SECRET)
notify = Notify()

twitterStream = Stream(auth, listener())
try:
	twitterStream.filter( languages =['en'], locations = [-140.99778, 18.91619, -66.96466,  83.23324],stall_warnings = True)
except:
	notify.send('App stopped')
