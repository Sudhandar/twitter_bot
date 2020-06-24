from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import credentials
from textblob import TextBlob
import sqlalchemy
import json
import pandas as pd
from unidecode import unidecode

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

class listener(StreamListener):

    def on_data(self, data):
        try:
            data = json.loads(data)
            tweet = unidecode(data['text'])
            analyzer = TextBlob(tweet)
            time_ms = data['timestamp_ms']
            sentiment = analyzer.sentiment.polarity
            print(time_ms, tweet, sentiment)
            df = pd.DataFrame({'unix': [time_ms],'tweet':[tweet], 'sentiment':[sentiment]})
            df.to_sql('sentiment', con = database_connection, if_exists = 'append', index = False)

        except KeyError as e:
            print(str(e))
        return(True)

    def on_error(self, status):
        print(status)

auth = OAuthHandler(credentials.CONSUMER_KEY, credentials.CONSUMER_KEY_SECRET)
auth.set_access_token(credentials.ACCESS_TOKEN, credentials.ACCESS_TOKEN_SECRET)

twitterStream = Stream(auth, listener())
twitterStream.filter( languages =['en'], track=["trump","biden"])