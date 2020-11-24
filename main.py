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

POS_NEG_NEUT = 0
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
    if col > POS_NEG_NEUT:
        return 'Positive'
    elif col < POS_NEG_NEUT:
        return 'Negative'
    else:
        return 'Neutral'

app = dash.Dash(external_stylesheets=[dbc.themes.GRID])
server = app.server
app.config['suppress_callback_exceptions']=True

app.layout = html.Div(
    [
        dbc.Row(dbc.Col(html.Div([html.H1("Twitter Sentiment Tracker")]),width ={"size":6, "offset":3},sm = 6)),

        dbc.Row(dbc.Col(html.Div(children = [
                                html.Div(children = 'Enter search term'),
                                dcc.Input(id = 'sentiment_term', value = 'trump', type = 'text', debounce = True),
                                ]),sm = 4)),
        dbc.Row(
        [
            dbc.Col(html.Div(
                        [   
                            html.H2("Live graph"),
                            dcc.Graph(id = 'live_graph', animate = False),
                            dcc.Interval(id='live_graph_update', interval= 3*1000,n_intervals = 0)
                        ]), width = {"size":6,}, lg= 6 , sm = 12 ),
            dbc.Col(html.Div(
                        [   
                            html.H2("Historical Graph"),
                            dcc.Graph(id = 'long_graph', animate = False),
                            dcc.Interval(id='long_graph_update', interval= 10*1000,n_intervals = 0)
                        ]) ,width = {"size":6}, lg = 6 , sm = 12)
        ]),
        dbc.Row(
        [
            dbc.Col(html.Div(
                        [   
                            html.H2("Tweets Table"),
                            html.Div(children = [html.Div(id = 'tweets_table')]),
                            dcc.Interval(id='tweets_table_update', interval= 10*1000,n_intervals = 0)
                        ]), width = {"size":6,},lg = 6, sm = 12),
            dbc.Col(html.Div(
                        [   
                            html.H2("Sentiment Pie Chart"),
                            dcc.Graph(id = 'pie_chart', animate = False),
                            dcc.Interval(id='pie_chart_update', interval= 20*1000,n_intervals = 0)
                        ]) ,width = {"size":6}, lg = 6, sm= 12)
        ]),
    ]
)
def quick_color(s):
    if s > POS_NEG_NEUT:
        return "#2ca02c"
    elif s < POS_NEG_NEUT:
        return "crimson"
    else:
        return '#7f7f7f'
def generate_table(df, max_rows=10):
    return html.Table(className="responsive-table",
                      children=[
                          html.Thead(
                              html.Tr(
                                  children=[
                                      html.Th(col.title()) for col in df.columns.values],
                              
                                  )
                              ),
                          html.Tbody(
                              [
                                  
                              html.Tr(
                                  children=[
                                      html.Td(data) for data in d
                                      ], style={'color':'#FFFFFF',
                                                'background-color':quick_color(d[2])}
                                  )
                               for d in df.values.tolist()])
                          ]
    )

@app.callback(Output('live_graph', 'figure'),
        [Input('live_graph_update', 'n_intervals'),
        Input('sentiment_term', 'value')])
def update_graph_scatter(n,sentiment_term):
    if n is None:
        raise PreventUpdate
    try:
        database_connection = db_connection()
        if sentiment_term:
            try:
                df = pd.DataFrame(database_connection.execute("SELECT * FROM sentiment_tweets WHERE Match(tweet) Against(%s) ORDER BY date DESC LIMIT 1000;",(sentiment_term)),columns = ['date','tweet','sentiment'])
            except:
                df = pd.DataFrame(database_connection.execute(" SELECT * FROM sentiment_tweets ORDER BY date DESC LIMIT 1000"),columns = ['date','tweet','sentiment']) 
                sentiment_term = ''
        else:
            df = pd.DataFrame(database_connection.execute(" SELECT * FROM sentiment_tweets ORDER BY date DESC LIMIT 1000"),columns = ['date','tweet','sentiment']) 
        df.sort_values('date', inplace=True)
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
            print(str(e))
            f.write(str(e))
            f.write('\n')

@app.callback(Output('long_graph', 'figure'),
        [Input('long_graph_update', 'n_intervals'),
        Input('sentiment_term', 'value')])
def update_hist_graph_scatter(n,sentiment_term):
    if n is None:
        raise PreventUpdate
    try:
        database_connection = db_connection()
        if sentiment_term:
            try:
                df = pd.DataFrame(database_connection.execute("SELECT * FROM sentiment_tweets WHERE Match(tweet) Against(%s) ORDER BY date DESC LIMIT 10000;",(sentiment_term)),columns = ['date','tweet','sentiment'])
            except:
                df = pd.DataFrame(database_connection.execute(" SELECT * FROM sentiment_tweets ORDER BY date DESC LIMIT 10000"),columns = ['date','tweet','sentiment'])
                sentiment_term = ''
        else:
            df = pd.DataFrame(database_connection.execute(" SELECT * FROM sentiment_tweets ORDER BY date DESC LIMIT 10000"),columns = ['date','tweet','sentiment']) 
        df.set_index('date', inplace=True)
        init_length = len(df)
        df['sentiment_smoothed'] = df['sentiment'].ewm(span=50,adjust=False).mean()
        df.dropna(inplace=True)
        df = df_resample_sizes(df, 1000)  
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
                                                          title='Longer-term sentiment for: "{}"'.format(sentiment_term),
                                                          font={'color':app_colors['text']},
                                                          plot_bgcolor = app_colors['background'],
                                                          paper_bgcolor = app_colors['background'],
                                                          showlegend=False)}
    except Exception as e:
        with open('errors.txt','a') as f:
            print(str(e))            
            f.write(str(e))
            f.write('\n')
@app.callback(Output('tweets_table', 'children'),
        [Input('tweets_table_update', 'n_intervals'),
        Input('sentiment_term', 'value')])
def update_table(n, sentiment_term):
    if n is None:
        raise PreventUpdate
    try:
        database_connection = db_connection()
        if sentiment_term:
            try:
                df = pd.DataFrame(database_connection.execute("SELECT * FROM sentiment_tweets WHERE Match(tweet) Against(%s) ORDER BY date DESC LIMIT 20;",(sentiment_term)),columns = ['date','tweet','sentiment'])
            except:
                df = pd.DataFrame(database_connection.execute(" SELECT * FROM sentiment_tweets ORDER BY date DESC LIMIT 20"),columns = ['date','tweet','sentiment'])        
                sentiment_term = ''
        else:
            df = pd.DataFrame(database_connection.execute(" SELECT * FROM sentiment_tweets ORDER BY date DESC LIMIT 20"),columns = ['date','tweet','sentiment'])        
        df['time'] = df['date'].dt.strftime('%H:%M:%S')
        df = df[['time','tweet','sentiment']]
        df = df.drop_duplicates(subset = 'tweet')
        df = df[:10]
        return generate_table(df)
    except Exception as e:
        with open('errors.txt','a') as f:
            print(str(e))
            f.write(str(e))
            f.write('\n')

@app.callback(Output('pie_chart', 'figure'),
        [Input('pie_chart_update', 'n_intervals'),
        Input('sentiment_term', 'value')])
def update_pie_chart(n, sentiment_term):
    if n is None:
        raise PreventUpdate
    try:
        database_connection = db_connection()
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
        df['sentiment_ema'] = df['sentiment'].ewm(span=50,adjust=False).mean()
        df.dropna(inplace=True)
        df = df_resample_sizes(df, 1000)
        df['sentiment_shares'] = list(map(pos_neg_neutral, df['sentiment_ema']))
        df = df[df['sentiment_shares']!='Neutral']
        sentiment_df = pd.DataFrame(df['sentiment_shares'].value_counts())
        sentiment_df.reset_index(level=0 , inplace = True)
        sentiment_df.columns = ['term','count']        
        fig = px.pie(sentiment_df, values='count',
                                names='term', 
                                color = 'term',
                                title = 'Positive vs Negative sentiment for "{}" (longer-term)'.format(sentiment_term),
                                color_discrete_map = {'Positive': '#2ca02c', 'Negative': 'crimson'})
        fig.update_layout(font={'size' : 13, 'color': 'black'})

        return fig
    except Exception as e:
        with open('errors.txt','a') as f:
            print(str(e))
            f.write(str(e))
            f.write('\n')
if __name__ == '__main__':
    # app.run_server(host = '0.0.0.0',port= 8050,debug =False)
    app.run_server(debug=True)