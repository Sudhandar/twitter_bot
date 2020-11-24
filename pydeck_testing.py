import pydeck as pdk
import sqlalchemy
import pandas as pd

# HEXAGON_LAYER_DATA = (
#     "https://raw.githubusercontent.com/visgl/deck.gl-data/master/examples/3d-heatmap/heatmap-data.csv"  # noqa
# )
MAPBOX_API_KEY = 'sk.eyJ1Ijoic3VkaGFuZGFyIiwiYSI6ImNraHZnOTZkcTBldHAzNG1vZWp4ODh4djkifQ.sDKYtSCk1WTVAvf5qZDeVA'

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
# df = pd.DataFrame(database_connection.execute("SELECT longitude,latitude FROM sentiment_tweets WHERE  latitude NOT IN (0)  ORDER BY date DESC;"),columns = ['longitude','latitude'])

# Define a layer to display on a map
# layer = pdk.Layer(
#     "HexagonLayer",
#     df,
#     get_position=["longitude", "latitude"],
#     auto_highlight=True,
#     elevation_scale=50,
#     pickable=True,
#     elevation_range=[0, 3000],
#     extruded=True,
#     coverage=1,
# )

# # Set the viewport location
# view_state = pdk.ViewState(
#     longitude=-90,
#     latitude=40,
#     zoom=6,
#     min_zoom=5,
#     max_zoom=15,
#     pitch=40.5,
#     bearing=-27.36,
# )
# Render
# r = pdk.Deck(layers=[layer], initial_view_state=view_state,mapbox_key = MAPBOX_API_KEY)
# r.to_html("hexagon_layer.html")

ALTER TABLE twitter_streaming.sentiment_tweets ADD latitude FLOAT NOT NULL;
ALTER TABLE twitter_streaming.sentiment_tweets ADD longitude FLOAT NOT NULL;
