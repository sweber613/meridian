# from urllib.request import urlopen
# import json
# import pandas as pd
# import plotly.express as px
# import numpy as np
#
#
# import geopandas as gpd
#
# geodf = gpd.read_file('../lcd_000b16a_e/lcd_000b16a_e.shp')
#
# print(geodf)
#
# df = pd.DataFrame().assign(CDUID=geodf['CDUID'])
# df['randNum'] = np.random.uniform(0.0, 1.0, df.shape[0])
#
# print(df)
#
# fig = px.choropleth(df, geojson=geodf.geometry,
#                     locations=geodf.CDUID,
#                     projection="mercator"
#                    )
# fig.update_geos(fitbounds="locations", visible=False)
# fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
# fig.show()

# geodf.to_file("canada_census_divisions.json", driver = "GeoJSON")
# with open("canada_census_divisions.json") as geofile:
#     j_file = json.load(geofile)



# with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
#     counties = json.load(response)
#
# print(counties)
#
# unemp = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/fips-unemp-16.csv",
#                    dtype={"fips": str})
#
# print(unemp)

# data = json.load(open('../canada_census_divisions.json'))
#
# print(data)

# import numpy as np
# import pandas as pd
# import geopandas as gpd
# import datetime as dt
# import plotly.express as px
#
# shp_provinces = gpd.read_file("../lpr_000a21a_e/lpr_000a21a_e.shp")
#
# # shp_census_tracts.plot() # this just maps as an image to verify that the dataframe is geospatial
#
# fig = px.choropleth_mapbox(shp_provinces,
#                            geojson=shp_provinces.geometry,
#                            locations="PRUID",
#                            featureidkey="properties.PRUID",
#                            color="PRUID",
#                            mapbox_style="carto-positron",
#                            center={"lat": 43.798625, "lon": -79.479050},
#                            zoom=4)
# fig.show()

import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import json
import pandas as pd
import numpy as np
from urllib.request import urlopen
import descartes

#
# data = gpd.read_file('provinces.json')
#
# jdata = json.load(open('provinces.json'))

data = gpd.read_file('census_subdivisions_simple_2016.json')

print(data)

# PRUID = [feat['properties']['PRUID'] for feat in jdata['features']]
# PRENAME = [feat['properties']['PRENAME'] for feat in jdata['features']]
#
# df = pd.DataFrame(list(zip(PRUID, PRENAME)), columns =['PRUID', 'PRENAME'])
# df['randNum'] = np.random.uniform(0.0, 1.0, df.shape[0])
#
# print(df)



# geodf = gpd.read_file('../lpr_000a21a_e/lpr_000a21a_e.shp')
#
# geodf_wgs84 = geodf.to_crs({'init': 'epsg:4326'})
#
# print(geodf_wgs84)

# df = pd.DataFrame(geodf[['PRUID', 'PRENAME']])
#
# df['randNum'] = np.random.uniform(0.0, 1.0, df.shape[0])
#
# print(df)

# print(geodf_wgs84)
#
# geodf_wgs84.to_file('provinces.json', driver='GeoJSON')

# with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
#     counties = gpd.read_file(response)
#
# unemp = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/fips-unemp-16.csv",
#                    dtype={"fips": str})
#
# print(unemp)
#
# print(counties)
#
# fig = px.choropleth_mapbox(geojson=jdata,
#                            locations=df['PRUID'],
#                            featureidkey='properties.PRUID',
#                            color=df['randNum'],
#                            center={"lat": 45.5517, "lon": -73.7073},
#                            mapbox_style="open-street-map",
#                            zoom=8.5)
# fig.show()

# fig = px.choropleth_mapbox(unemp, geojson=counties, locations='fips', color='unemp',
#                            color_continuous_scale="Viridis",
#                            range_color=(0, 12),
#                            mapbox_style="carto-positron",
#                            zoom=3, center = {"lat": 37.0902, "lon": -95.7129},
#                            opacity=0.5,
#                            labels={'unemp':'unemployment rate'}
#                           )
# fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
# fig.show()

# fig= go.Figure(go.Choroplethmapbox(z=df['randNum'],
#                             locations=df['PRUID'],
#                             colorscale='reds',
#                             colorbar=dict(thickness=20, ticklen=3),
#                             geojson=jdata,
#                             text=df['PRENAME'],
#                             hoverinfo='all',
#                             marker_line_width=1, marker_opacity=0.75))
#
#
# # fig.update_layout(title_text= 'Choroplethmapbox',
# #                   title_x=0.5, width = 700,# height=700,
# #                   mapbox = dict(center= dict(lat=36.913818,  lon=106.363625),
# #                                  accesstoken= mapboxt,
# #                                  style='basic',
# #                                  zoom=2.35,
# #                                ));
#
# fig.show()
