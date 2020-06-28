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
    'background': 'white',
    'text': 'black',
    'sentiment-plot':'#41EAD4',
    'volume-bar':'#FBFC74',
    'someothercolor':'#FF206E',
}
MAX_DF_LENGTH = 100

def df_resample_sizes(df, maxlen=MAX_DF_LENGTH):
    df_len = len(df)
    resample_amt = 100
    vol_df = df.copy()
    vol_df['volume'] = 1

    ms_span = (df.index[-1] - df.index[0]).seconds * 1000
    rs = int(ms_span / maxlen)

    df = df.resample('{}ms'.format(int(rs))).mean()
    df.dropna(inplace=True)

    vol_df = vol_df.resample('{}ms'.format(int(rs))).sum()
    vol_df.dropna(inplace=True)

    df = df.join(vol_df['volume'])

    return df

def pos_neg_neutral(col):
    if col >= POS_NEG_NEUT:
        # positive
        return 1
    elif col <= -POS_NEG_NEUT:
        # negative:
        return -1
    else:
        return 0

app = dash.Dash(external_stylesheets=[dbc.themes.GRID])

app.layout = html.Div(
    [
        dbc.Row(dbc.Col(html.Div([html.H1("Twitter Sentiment Tracker")]),width ={"size":6, "offset":3})),

        dbc.Row(dbc.Col(html.Div([
                                html.Div(children = 'Enter search term'),
                                dcc.Input(id = 'sentiment_term', value = 'trump', type = 'text'),
                                ]))),

        dbc.Row(
            [
                dbc.Col(html.Div([html.H2("Live graph")])),
                dbc.Col(html.Div([html.H2("Historical Graph")])),
            ], justify = 'center'
        ),

        dbc.Row(
        [
            dbc.Col(html.Div(
                        [ 
                            dcc.Graph(id = 'live_graph', animate = False),
                            dcc.Interval(id='live_graph_update', interval= 1*1000,n_intervals = 0)
                        ]), width = {"size":6,}),
            dbc.Col(html.Div(
                        [
                            dcc.Graph(id = 'long_graph', animate = False),
                            dcc.Interval(id='long_graph_update', interval= 30*1000,n_intervals = 0)
                        ]) ,width = {"size":6})
        ]),

    ]
)

@app.callback(Output('live_graph', 'figure'),
        [Input('live_graph_update', 'n_intervals'),
        Input('sentiment_term', 'value')])

def update_graph_scatter(n,sentiment_term):
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
        df['date'] = pd.to_datetime(df['unix'], unit='ms')
        df.set_index('date', inplace=True)
        init_length = len(df)
        df['sentiment_smoothed'] = df['sentiment'].rolling(int(len(df)/5)).mean()
        df = df_resample_sizes(df)
        X = df.index
        Y = df.sentiment_smoothed.values
        Y2 = df.volume.values
        data = plotly.graph_objs.Scatter(
                x=X,
                y=Y,
                name='Sentiment',
                mode= 'lines',
                yaxis='y2',
                line = dict(color = (app_colors['sentiment-plot']),
                            width = 4,)
                )

        data2 = plotly.graph_objs.Bar(
                x=X,
                y=Y2,
                name='Volume',
                marker=dict(color=app_colors['volume-bar']),
                )

        return {'data': [data,data2],'layout' : go.Layout(xaxis=dict(range=[min(X),max(X)]),
                                                          yaxis=dict(range=[min(Y2),max(Y2*4)], title='Volume', side='right'),
                                                          yaxis2=dict(range=[min(Y),max(Y)], side='left', overlaying='y',title='sentiment'),
                                                          title='Live sentiment for term : "{}"'.format(sentiment_term),
                                                          font={'color':app_colors['text']},
                                                          plot_bgcolor = app_colors['background'],
                                                          paper_bgcolor = app_colors['background'],
                                                          showlegend=False)}

    except Exception as e:
        with open('errors.txt','a') as f:
            f.write(str(e))
            f.write('\n')

@app.callback(Output('long_graph', 'figure'),
        [Input('long_graph_update', 'n_intervals'),
        Input('sentiment_term', 'value')])

def update_hist_graph_scatter(n,sentiment_term):
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
        df = pd.DataFrame(database_connection.execute(" SELECT * FROM sentiment WHERE tweet LIKE %s ORDER BY unix DESC LIMIT 10000", ("%" + sentiment_term + "%",)),columns = ['unix','tweet','sentiment'])
        df.sort_values('unix', inplace=True)
        df['date'] = pd.to_datetime(df['unix'], unit='ms')
        df.set_index('date', inplace=True)
        init_length = len(df)
        df['sentiment_smoothed'] = df['sentiment'].rolling(int(len(df)/5)).mean()
        df.dropna(inplace=True)
        df = df_resample_sizes(df,maxlen=1000)
        X = df.index
        Y = df.sentiment_smoothed.values
        Y2 = df.volume.values
        data = plotly.graph_objs.Scatter(
                x=X,
                y=Y,
                name='Sentiment',
                mode= 'lines',
                yaxis='y2',
                line = dict(color = (app_colors['sentiment-plot']),
                            width = 4,)
                )
        data2 = plotly.graph_objs.Bar(
                x=X,
                y=Y2,
                name='Volume',
                marker=dict(color=app_colors['volume-bar']),
                )
        df['sentiment_shares'] = list(map(pos_neg_neutral, df['sentiment']))
        return {'data': [data,data2],'layout' : go.Layout(xaxis=dict(range=[min(X),max(X)]),
                                                          yaxis=dict(range=[min(Y2),max(Y2*4)], title='Volume', side='right'),
                                                          yaxis2=dict(range=[min(Y),max(Y)], side='left', overlaying='y',title='sentiment'),
                                                          title='Longer-term sentiment for: "{}"'.format(sentiment_term),
                                                          font={'color':app_colors['text']},
                                                          plot_bgcolor = app_colors['background'],
                                                          paper_bgcolor = app_colors['background'],
                                                          showlegend=False)}

    except Exception as e:
        with open('errors.txt','a') as f:
            f.write(str(e))
            f.write('\n')


if __name__ == '__main__':
    app.run_server(debug = True)