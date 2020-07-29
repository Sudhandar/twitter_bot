import dash
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
from tweepy import API
import plotly
import plotly.graph_objs as go 
import sqlalchemy
import pandas as pd
import credentials
from tweepy import OAuthHandler
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import plotly.express as px

POS_NEG_NEUT = 0.1

MAX_DF_LENGTH = 100
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

#def df_resample_sizes(df, maxlen=1000):
#    df_len = len(df)
#    resample_amt = 100
#    vol_df = df.copy()
#    vol_df['volume'] = 1
#    ms_span = (df.index[-1] - df.index[0]).seconds * 1000
#    rs = int(ms_span / maxlen)
#    df = df.resample('{}ms'.format(int(rs))).mean()
#    df.dropna(inplace=True)
#    vol_df = vol_df.resample('{}ms'.format(int(rs))).sum()
#    vol_df.dropna(inplace=True)
#    df = df.join(vol_df['volume'])
#    return df

def pos_neg_neutral(col):
    if col >= POS_NEG_NEUT:
        # positive
        return 'Positive'
    elif col <= -POS_NEG_NEUT:
        # negative:
        return 'Negative'
    else:
        return 'Neutral'

app = dash.Dash(external_stylesheets=[dbc.themes.GRID])
server = app.server
app.config['suppress_callback_exceptions']=True

app.layout = html.Div(
    [
        dbc.Row(
        [
            dbc.Col(html.Div(
                        [   
                            html.H2("Sentiment Pie Chart"),
                            dcc.Graph(id = 'pie_chart', animate = False),
                            dcc.Interval(id='pie_chart_update', interval= 20*1000,n_intervals = 0)
                        ]) ,width = {"size":6, "offset": 1}, lg = 6, sm= 12)
        ]),


    ])
@app.callback(Output('pie_chart', 'figure'),
        [Input('pie_chart_update', 'n_intervals')])

def update_pie_chart(n):
    if n is None:
        raise PreventUpdate
    try:
        database_connection = db_connection()
        sentiment_term = 'trump'
        if sentiment_term:
            try:
                df = pd.DataFrame(database_connection.execute("SELECT * FROM sentiment_tweets WHERE Match(tweet) Against(%s) ORDER BY date DESC LIMIT 10000;",(sentiment_term)),columns = ['date','tweet','sentiment'])
            except:
                df = pd.DataFrame(database_connection.execute(" SELECT * FROM sentiment_tweets ORDER BY date DESC LIMIT 10000"),columns = ['date','tweet','sentiment'])  
                sentiment_term = ''
        else:
            df = pd.DataFrame(database_connection.execute(" SELECT * FROM sentiment_tweets ORDER BY date DESC LIMIT 10000"),columns = ['date','tweet','sentiment'])  
        df.set_index('date',inplace = True)
        df.sort_values('date', inplace=True)
        # df['sentiment_smoothed'] = df['sentiment'].rolling(int(len(df)/5)).mean()
        df['sentiment_ema'] = df['sentiment'].ewm(span=50,adjust=False).mean()
        df.dropna(inplace=True)
#        df = df_resample_sizes(df,maxlen=1000)
        df['sentiment_shares'] = list(map(pos_neg_neutral, df['sentiment_ema']))
        df = df[df['sentiment_shares']!='Neutral']
        sentiment_df = pd.DataFrame(df['sentiment_shares'].value_counts())
        sentiment_df.reset_index(level=0 , inplace = True)
        sentiment_df.columns = ['term','count']        
        fig = px.pie(sentiment_df, values='count',
                                names='term', 
                                color = 'term',
                                title = 'Positive vs Negative sentiment for "{}" (longer-term)'.format(sentiment_term),
                                color_discrete_map = {'Positive': 'green', 'Negative': 'crimson'})
        return fig
    except Exception as e:
        with open('errors.txt','a') as f:
            print(str(e))
            f.write(str(e))
            f.write('\n')
if __name__ == '__main__':
    app.run_server(debug=False)


    

