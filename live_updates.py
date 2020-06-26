import dash
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import random
import plotly.graph_objs as go 
from collections import deque
import sqlalchemy
import pandas as pd

app = dash.Dash(__name__)
app.layout = html.Div(
    [	html.H2('Live Twitter Sentiment'),
    	dcc.Input(id ='sentiment_term', value = 'trump', type = 'text'),
        dcc.Graph(id='live-graph', animate=True),
        dcc.Interval(
            id='graph-update',
            interval= 1*1000,
            n_intervals = 0
        ),
    ]
)

@app.callback(Output('live-graph', 'figure'),
		[Input('graph-update', 'n_intervals'),
		Input(component_id = 'sentiment_term', component_property = 'value')])


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
		df['sentiment_smoothed'] = df['sentiment'].rolling(int(len(df)/5)).mean()
		df.dropna(inplace=True)

		X = df.unix.values[-100:]
		Y = df.sentiment.values[-100:]

		data = go.Scatter(
			    x=list(X),
			    y=list(Y),
			    name='Scatter',
			    mode= 'lines+markers',
			    )

		return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(X),max(X)]),
		                                            yaxis=dict(range=[min(Y),max(Y)]),)}

	except Exception as e:
		with open('errors.txt','a') as f:
			f.write(str(e))
			f.write('\n')


if __name__ == '__main__':
    app.run_server(debug=True)