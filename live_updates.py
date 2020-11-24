# import dash
# from dash.dependencies import Output, Input
# import dash_core_components as dcc
# import dash_html_components as html
import sqlalchemy
# import pandas as pd
# import plotly.express as px
# from dash.exceptions import PreventUpdate
# import dash_bootstrap_components as dbc
# import pydeck as pdk

# MAPBOX_API_KEY = 'sk.eyJ1Ijoic3VkaGFuZGFyIiwiYSI6ImNraHZnOTZkcTBldHAzNG1vZWp4ODh4djkifQ.sDKYtSCk1WTVAvf5qZDeVA'


# def db_connection():
#     database_username = 'root'
#     database_password = ''
#     database_ip = 'localhost'
#     database_name = 'twitter_streaming'
#     database_connection = sqlalchemy.create_engine(
#        'mysql+pymysql://{0}:{1}@{2}/{3}'.format(
#            database_username, database_password,
#            database_ip, database_name
#        )
#     )
#     return database_connection
# def grouping(x):
#   if x >0.5:
#     return 1
#   elif (x >0) and (x<=0.5):
#     return 0.5
#   elif (x<0) and (x>=-0.5):
#     return -0.5
#   elif x<0.5:
#     return -1
#   elif x == 0:
#     return 0

# app = dash.Dash()

# maps = html.Div([
#                   dcc.Input(id = 'input_term', value = 'trump', type = 'text', debounce = True),
#                   dcc.Graph(id = 'heatmap', animate = False),
#                   ])
# app.layout = html.Div(
#   [
#     dbc.Row([dbc.Col(maps)])
#     ])

# # @app.callback(Output('heatmap', 'figure'),[Input('input_term', 'value')])
# # def update_heatmap(input_term):
# #     database_connection = db_connection()
# #     df = pd.DataFrame(database_connection.execute("SELECT * FROM sentiment_tweets WHERE  latitude NOT IN (0)  ORDER BY date DESC;"),columns = ['date','tweet','sentiment','latitude','longitude'])
# #     df['sentiment'] = df['sentiment'].apply(lambda x : grouping(x))
# #     print(df.shape[0])
# #     # fig = px.scatter_geo(df, lat='latitude', lon='longitude',
# #     #                         center=dict(lat=50, lon=-100),scope = 'north america')
# #     fig = px.density_mapbox(df, lat='latitude', lon='longitude', z='sentiment', radius=10,
# #                       center=dict(lat=40, lon=-90), zoom=2,
# #                       mapbox_style="stamen-terrain")

# #     return fig
# @app.callback(Output('heatmap', 'figure'),[Input('input_term', 'value')])
# def update_heatmap(input_term):
#     database_connection = db_connection()
#     df = pd.DataFrame(database_connection.execute("SELECT longitude,latitude FROM sentiment_tweets WHERE  latitude NOT IN (0)  ORDER BY date DESC;"),columns = ['longitude','latitude'])
#     # fig = px.scatter_geo(df, lat='latitude', lon='longitude',
#     #                         center=dict(lat=50, lon=-100),scope = 'north america')
#     layer = pdk.Layer(
#         "HexagonLayer",
#         df,
#         get_position=["longitude", "latitude"],
#         auto_highlight=True,
#         elevation_scale=50,
#         pickable=True,
#         elevation_range=[0, 3000],
#         extruded=True,
#         coverage=1,
#     )

#     # Set the viewport location
#     view_state = pdk.ViewState(
#         longitude=-90,
#         latitude=40,
#         zoom=6,
#         min_zoom=5,
#         max_zoom=15,
#         pitch=40.5,
#         bearing=-27.36,
#     )
#     # Render
#     fig = pdk.Deck(layers=[layer], initial_view_state=view_state,mapbox_key = MAPBOX_API_KEY)
#     # r.to_html("hexagon_layer.html")
#     return fig


# if __name__ == '__main__':
#     app.run_server(debug=True)

import dash
import dash_deck
import dash_html_components as html
import pydeck as pdk
import pandas as pd

mapbox_api_token = 'pk.eyJ1Ijoic3VkaGFuZGFyIiwiYSI6ImNraHZmdXlwajE3NDgyeHBpa213NDVxOG8ifQ.P02Pv5ZWgZyAiFLtfEEMvg'
# MAPBOX_API_KEY = 'sk.eyJ1Ijoic3VkaGFuZGFyIiwiYSI6ImNraHZnOTZkcTBldHAzNG1vZWp4ODh4djkifQ.sDKYtSCk1WTVAvf5qZDeVA'
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
database_connection = db_connection()

df = pd.DataFrame(database_connection.execute("SELECT longitude,latitude FROM sentiment_tweets WHERE  latitude NOT IN (0)  ORDER BY date DESC;"),columns = ['longitude','latitude'])


# HEXAGON_LAYER_DATA = "https://raw.githubusercontent.com/visgl/deck.gl-data/master/examples/3d-heatmap/heatmap-data.csv"  # noqa

# Define a layer to display on a map
layer = pdk.Layer(
    "HexagonLayer",
    df,
    get_position=["longitude", "latitude"],
    auto_highlight=True,
    elevation_scale=200,
    pickable=True,
    elevation_range=[0, 3000],
    extruded=True,
    coverage=1,
)

# Set the viewport location
view_state = pdk.ViewState(
    longitude=-90,
    latitude=40,
    zoom=4,
    min_zoom=2,
    max_zoom=15,
    pitch=40.5,
    bearing=-27.36,
)

r = pdk.Deck(layers=[layer], initial_view_state=view_state)


app = dash.Dash(__name__)

app.layout = html.Div(
    dash_deck.DeckGL(r.to_json(), id="deck-gl", mapboxKey=mapbox_api_token)
)


if __name__ == "__main__":
    app.run_server(debug=True)