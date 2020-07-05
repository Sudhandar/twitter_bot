import sqlalchemy

def db_connection():
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
    return database_connection

def truncate_before_dump(table):
   '''
   To Truncate all tables before populating them
   '''
   engine = db_connection()
   with engine.connect() as con:
       print("Deleting %s table from %s" % (table, 'twitter_streaming'))
       con.execute("DELETE FROM " + table + ";")

if __name__ == '__main__':
  truncate_before_dump('sentiment_tweets')