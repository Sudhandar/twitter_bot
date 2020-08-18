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
import plotly.express as px

POS_NEG_NEUT = 0.1
sentiment_colors = {-1:"#EE6055",
                    -0.5:"#FDE74C",
                     0:"#FFE6AC",
                     0.5:"#D0F2DF",
                     1:"#9CEC5B",}
app_colors = {
    'background': 'white',
    'text': 'black',
    'sentiment-plot':'#41EAD4',
    'volume-bar':'yellow',
    'someothercolor':'#FF206E',
}
def pos_neg_neutral(col):
    if col >= POS_NEG_NEUT:
        # positive
        return 'Positive'
    elif col <= -POS_NEG_NEUT:
        # negative:
        return 'Negative'
    else:
        return 'Neutral'


app = dash.Dash(external_stylesheets=[dbc.themes.CYBORG])

app.layout = html.Div(
    [	html.H2('Live Twitter Sentiment'),
    	dcc.Input(id = 'sentiment_term', value = 'trump', type = 'text'),
        dcc.Graph(id = 'live-graph', animate = False),
        dcc.Interval(
            id='graph-update',
            interval= 1*1000,
            n_intervals = 0
        ),

        dcc.Graph(id = 'pie-chart', animate = False),
        dcc.Interval(
            id='pie-update',
            interval= 10*1000,
            n_intervals = 0
        ),
        


		html.Div(children = 'Recent Trends', style = {'textAlign' :'center'}),


        html.Div(children = [html.Div(id = 'recent_trends')]),
        dcc.Interval(
        	id = 'trend_interval',
        	interval = 30*1000,
        	n_intervals = 0),

		html.Div(children = 'Latest Tweets', style = {'textAlign' :'center'}),

        html.Div(children = [html.Div(id = 'recent_tweets_table')]),
        dcc.Interval(
            id='recent_tweets_table_update',
            interval= 10*1000,
            n_intervals = 0
        ),
        
], className = 'container', style = {'width':'50%', 'margin-left' : 10, 'margin-right' : 10}
)

def quick_color(s):
    if s >= POS_NEG_NEUT:
        return "#2ca02c"
    elif s <= -POS_NEG_NEUT:
        return "#d62728"
    else:
        return '#7f7f7f'

# def generate_table(df, max_rows=10):
#     return html.Table(className="responsive-table",
#                       children=[
#                           html.Thead(
#                               html.Tr(
#                                   children=[
#                                       html.Th(col.title()) for col in df.columns.values],
                              
#                                   )
#                               ),
#                           html.Tbody(
#                               [
                                  
#                               html.Tr(
#                                   children=[
#                                       html.Td(data) for data in d
#                                       ], style={'color':'#FFFFFF',
#                                                 'background-color':quick_color(d[2])}
#                                   )
#                                for d in df.values.tolist()])
#                           ]
#     )


# @app.callback(Output('live-graph', 'figure'),
# 		[Input('graph-update', 'n_intervals'),
# 		Input(component_id = 'sentiment_term', component_property = 'value')])


# def update_graph_scatter(n, sentiment_term):

# 	try:

# 		database_username = 'root'
# 		database_password = ''
# 		database_ip = 'localhost'
# 		database_name = 'twitter_streaming'
# 		database_connection = sqlalchemy.create_engine(
# 		   'mysql+pymysql://{0}:{1}@{2}/{3}'.format(
# 		       database_username, database_password,
# 		       database_ip, database_name
# 		   )
# 		)

# 		df = pd.DataFrame(database_connection.execute(" SELECT * FROM sentiment WHERE tweet LIKE %s ORDER BY unix DESC LIMIT 1000", ("%" + sentiment_term + "%",)),columns = ['unix','tweet','sentiment'])
# 		df.sort_values('unix', inplace=True)
# 		df['date'] = pd.to_datetime(df['unix'], unit = 'ms')
# 		df.set_index('date', inplace = True)
# 		df['sentiment_smoothed'] = df['sentiment'].rolling(int(len(df)/5)).mean()
# 		df.dropna(inplace=True)
# 		df = df.resample('1s').mean()

# 		X = df.index[-100:]
# 		Y = df.sentiment.values[-100:]

# 		data = go.Scatter(
# 			    x=list(X),
# 			    y=list(Y),
# 			    name='Scatter',
# 			    mode= 'lines',
# 			    )

# 		return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(X),max(X)]),
# 		                                            yaxis=dict(range=[min(Y),max(Y)]),
# 		                                            title = 'Term : {}'.format(sentiment_term))}

# 	except Exception as e:
# 		with open('errors.txt','a') as f:
# 			f.write(str(e))
# 			f.write('\n')

# @app.callback(Output('recent_tweets_table', 'children'),
# 		[Input('recent_tweets_table_update', 'n_intervals'),
# 		Input(component_id = 'sentiment_term', component_property = 'value')])

# def update_table(n, sentiment_term):

# 	try:

# 		database_username = 'root'
# 		database_password = ''
# 		database_ip = 'localhost'
# 		database_name = 'twitter_streaming'
# 		database_connection = sqlalchemy.create_engine(
# 		   'mysql+pymysql://{0}:{1}@{2}/{3}'.format(
# 		       database_username, database_password,
# 		       database_ip, database_name
# 		   )
# 		)

# 		df = pd.DataFrame(database_connection.execute(" SELECT * FROM sentiment WHERE tweet LIKE %s ORDER BY unix DESC LIMIT 10", ("%" + sentiment_term + "%",)),columns = ['unix','tweet','sentiment'])
# 		df.sort_values('unix', inplace=True)
# 		df['date'] = pd.to_datetime(df['unix'], unit = 'ms')
# 		df.pop('unix')
# 		df = df[['date','tweet','sentiment']]

# 		return generate_table(df,10)

# 	except Exception as e:
# 		with open('errors.txt','a') as f:
# 			f.write(str(e))
# 			f.write('\n')

# @app.callback(Output('recent_trends', 'children'),
# 		[Input('trend_interval', 'n_intervals'),])


# def recent_trends_df(n):

# 	auth = OAuthHandler(credentials.CONSUMER_KEY, credentials.CONSUMER_KEY_SECRET)
# 	auth.set_access_token(credentials.ACCESS_TOKEN, credentials.ACCESS_TOKEN_SECRET)
# 	api = API(auth)
# 	trends1 = api.trends_place(23424848)
# 	data = trends1[0]['trends']
# 	trends = [trend['name'] for trend in data][:10]

# 	return trends

# @app.callback(Output('pie-chart', 'figure'),
# 		[Input('pie-update', 'n_intervals'),
# 		Input(component_id = 'sentiment_term', component_property = 'value')])
# python seq_wc.py --load_arg checkpoint/cwlm_lstm_crf.json --load_check_point checkpoint/cwlm_lstm_crf.model --input_file input.tsv --output_file annotate/output --gpu 0


def update_graph_pie(n, sentiment_term):

    try:
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
        df = pd.DataFrame(database_connection.execute(" SELECT * FROM sentiment_tweets WHERE tweet LIKE %s ORDER BY date DESC LIMIT 1000", ("%" + sentiment_term + "%",)),columns = ['unix','tweet','sentiment'])
        df.sort_values('unix', inplace=True)
        df['sentiment_shares'] = list(map(pos_neg_neutral, df['sentiment']))
        df = df[df['sentiment_shares']!='Neutral']
        sentiment_df = pd.DataFrame(df['sentiment_shares'].value_counts())
        sentiment_df.reset_index(level=0 , inplace = True)
        sentiment_df.columns = ['term','count']        
        colors = ['green', 'red']
        fig = px.pie(sentiment_df, values='count',
                                names='term', 
                                color = 'term',
                                title = 'Positive vs Negative sentiment for "{}" (longer-term)'.format(sentiment_term),
                                color_discrete_map = {'Positive': 'green', 'Negative': 'red'})
        return fig
    except Exception as e:
    	with open('errors.txt','a') as f:
    		f.write(str(e))
    		f.write('\n')
if __name__ == '__main__':
    app.run_server(debug=False)

