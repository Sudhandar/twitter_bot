import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash

live_graph = dbc.Card( 
                 dbc.CardBody(
                    [     
                            dcc.Graph(id = 'live_graph', animate = False),
                            dcc.Interval(id='live_graph_update', interval= 3*1000,n_intervals = 0)
                    ]
                )
            )

historical_graph = dbc.Card(
                        dbc.CardBody(
                                [  
                                    dcc.Graph(id = 'long_graph', animate = False),
                                    dcc.Interval(id='long_graph_update', interval= 30*1000,n_intervals = 0)
                                ] 
                            )
                        )

tweets_table = dbc.Card(
                        dbc.CardBody(
                            [   
                                html.H2("Tweets Table",style = {"textAlign":'center'}),
                                html.Div(id = 'tweets_table'),
                                dcc.Interval(id='tweets_table_update', interval= 10*1000,n_intervals = 0)

                            ]
                        )
                    )

sentiment_chart = dbc.Card(
                        dbc.CardBody(
                            [
                                html.H2("Sentiment Pie Chart",style = {"textAlign":'center'}),
                                dcc.Graph(id = 'pie_chart', animate = False),
                                dcc.Interval(id='pie_chart_update', interval= 20*1000,n_intervals = 0)
                            ]
                        )
                    )

layout = html.Div(
    [
        dbc.Row([dbc.Col(
                            html.Div([html.H1("Live Sentiment Updates",style = {"textAlign":'center'})]),
            )
        ]),
        dbc.Row(html.Div(children = [
                                html.Div(children = 'Enter search term'),
                                dcc.Input(id = 'sentiment_term', value = 'trump', type = 'text', debounce = True),
                                ])),
        html.Div(id='hidden-div', style={'display': 'none'}),
        html.Hr(),
        dbc.Row([dbc.Col(live_graph,width = 6), dbc.Col(historical_graph,width=6)], no_gutters = True),

        dbc.Row([dbc.Col(tweets_table,width = 6), dbc.Col(sentiment_chart,width=6)], no_gutters = True),
    ]
)

POS_NEG_NEUT = 0

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
