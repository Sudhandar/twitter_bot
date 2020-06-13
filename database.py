import sqlite3
import json
from datetime import datetime

timeframe ='2009-09'
sql_transactions = []

connection = sqlite3.connect('{}.db'.format(timeframe))
c = connection.cursor()

def format_data(data):
    data = data.replace("\n"," newlinechar ").replace("\r"," newlinechar ").replace('"',"'")
    return data

def find_parent(pid):
    try:
        sql = "SELECT comment FROM parent_reply WHERE comment_id = '{}' LIMIT 1".format(pid)
        c.execute(sql)
        result = c.fetchone()
        if result!= None:
            return result
        else:
            return False
    except:
        return False
    

def create_table():
    c.execute("""CREATE TABLE IF NOT EXISTS parent_reply
    (parent_id TEXT PRIMARY KEY, comment_id TEXT UNIQUE, parent TEXT,
    comment TEXT, unix INT, score INT)""")
    
if __name__ == '__main__':
    create_table()
    row_counter = 0 
    paired_rows = 0
    
    with open("RC_{}".format(timeframe), buffer =1000) as f:
        for row in f:
            row_counter +=1
            row = json.load(row)
            parent_id = row['parent_id']
            body = format_data(row['body'])
            created_utc = row['created_utc']
            score = row['score']
            row = row['subreddit']
            parent_data = find_parent(parent_id)
            
    