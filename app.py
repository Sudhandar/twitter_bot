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

POS_NEG_NEUT = 0.1

sentiment_colors = {-1:"#EE6055",
					-0.5:"#FDE74C",
					0:"#FFE6AC",
					0.5:"#D0F2DF",
					1:"#9CEC5B",}

app_colors = {
	'background': '#0C0F0A',
	'text': '#FFFFFF',
	'sentiment-plot':'#41EAD4',
	'volume-bar':'#FBFC74',
	'someothercolor':'#FF206E',
}


app = dash.Dash(external_stylesheets=[dbc.themes.GRID])

app.layout = html.Div(
	[
		dbc.Row(dbc.Col(html.Div([html.H1("Live Sentiment Tracker")]), width ={"size":6,"offset":4}), align = 'center'),

		dbc.Row(dbc.Col(html.Div([
								html.Div(children = 'Enter search term'),
								dcc.Input(id = 'sentiment_term', value = 'trump', type = 'text'),
								]))),

		dbc.Row(dbc.Col(html.Br())),

		dbc.Row(
			[
				dbc.Col(html.Div([html.H4("Live sentiment graph")]), width = {"size":5}),
				dbc.Col(html.Div([html.H4("Historical sentiment Graph")]), width = {"size":5, "offset":1}),
			], justify = 'center'
		),

		dbc.Row(
			[
				dbc.Col(html.Div(
							[ 
								dcc.Graph(id = 'live-graph', animate = False),
								dcc.Interval(id='graph-update', interval= 1*1000,n_intervals = 0)
							]), width = {"size":6}),
			])

			]
		)



@app.callback(Output('live-graph', 'figure'),
		[Input('graph-update', 'n_intervals'),
		Input('sentiment_term', 'value')])

def update_graph_scatter(n, sentiment_term):
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
		df = pd.DataFrame(database_connection.execute(" SELECT * FROM sentiment WHERE tweet LIKE %s ORDER BY unix DESC LIMIT 1000", ("%" + sentiment_term + "%",)),columns = ['unix','tweet','sentiment'])
		df.sort_values('unix', inplace=True)
		df['date'] = pd.to_datetime(df['unix'], unit = 'ms')
		df.set_index('date', inplace = True)
		df['sentiment_smoothed'] = df['sentiment'].rolling(int(len(df)/5)).mean()
		df.dropna(inplace=True)
		df = df.resample('1s').mean()
		X = df.index[-100:]
		Y = df.sentiment.values[-100:]
		data = go.Scatter(
			    x=list(X),
			    y=list(Y),
			    name='Scatter',
			    mode= 'lines',
			    )
		return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(X),max(X)]),
													yaxis=dict(range=[min(Y),max(Y)]),
													title = 'Term : {}'.format(sentiment_term))}
	except Exception as e:
		with open('errors.txt','a') as f:
			f.write(str(e))
			f.write('\n')


if __name__ == '__main__':
	app.run_server(debug=True)
