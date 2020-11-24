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
from pages import live_sentiment
import json

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

# the style arguments for the sidebar. We use position:fixed and a fixed width

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "12rem",
    "padding": "1rem 1rem",
    "background-color": "#f8f9fa",
}
# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "13rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H2("Twitter Tracker", className="display-4"),
        html.Hr(),
        html.P(
            "Select any one of the analysis", className="lead"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Live Sentiment", href="/live-sentiment", id="live-sentiment-link"),
                dbc.NavLink("Page 2", href="/page-2", id="page-2-link"),
                dbc.NavLink("Page 3", href="/page-3", id="page-3-link"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server
app.config['suppress_callback_exceptions']=True
app.layout = html.Div([dcc.Location(id="url"), sidebar, content])

@app.callback(
    [Output("live-sentiment-link", "active"),Output("page-2-link", "active"),Output("page-3-link", "active")],
    [Input("url", "pathname")],
)
def toggle_active_links(pathname):
    if pathname == "/":
        # Treat page 1 as the homepage / index
        return True, False, False
    return  [pathname == "/live-sentiment",pathname == "/page-2",pathname == "/page-3"]


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname in ["/", "/live-sentiment"]:
        return live_sentiment.layout
    elif pathname == "/page-2":
        return html.P("This is the content of page 2. Yay!")
    elif pathname == "/page-3":
        return html.P("Oh cool, this is page 3!")
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
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

@app.callback([Output('long_graph', 'figure'),Output('hidden-div','children')],
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
        dataset = {}
        dataset['df'] = df
        data_dict = {
            key: dataset[key].to_dict(orient='records') 
            for key in dataset.keys()
        }
        df_json = json.dumps(data_dict)
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
                                                          showlegend=False)}, df_json
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
        return live_sentiment.generate_table(df)
    except Exception as e:
        with open('errors.txt','a') as f:
            print(str(e))
            f.write(str(e))
            f.write('\n')

@app.callback(Output('pie_chart', 'figure'),
        [Input('pie_chart_update', 'n_intervals'),
        Input('sentiment_term', 'value'),
        Input('hidden-div','children')])
def update_pie_chart(n, sentiment_term,json_file):
    if n is None:
        raise PreventUpdate
    try:
        dataset_json = json.loads(json_file)
        dataset = {
            key: pd.DataFrame(dataset_json[key]) 
            for key in dataset_json
        }
        df = dataset['df']
        df.rename(columns = {'sentiment_smoothed':'sentiment_ema'}, inplace = True) 
        df['sentiment_shares'] = list(map(pos_neg_neutral, df['sentiment_ema']))
        df = df[df['sentiment_shares']!='Neutral']
        sentiment_df = pd.DataFrame(df['sentiment_shares'].value_counts())
        sentiment_df.reset_index(level=0 , inplace = True)
        sentiment_df.columns = ['term','count']        
        fig = px.pie(sentiment_df, values='count',
                                names='term', 
                                color = 'term',
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
