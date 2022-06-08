import dash
import base64
import io
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_daq as daq
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from urllib.request import urlopen
import json
import numpy as np

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

px.set_mapbox_access_token('pk.eyJ1Ijoic3dlYmVyNjEzIiwiYSI6ImNsNDMwaGQ5NzE0N3AzZG9menk4cWljMWQifQ.jkgByHIsA8MOWgULENoDJA')

app = dash.Dash(
    __name__, external_stylesheets=external_stylesheets
)

# read in canadian city data
canada_cities = pd.read_csv('https://raw.githubusercontent.com/sweber613/meridian/main/Canadian%20Population%20Centres%20-%20Adapted%20From%20GeoNames.org.csv', encoding = "ISO-8859-1")

us_cities = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/us-cities-top-1k.csv")

airports = pd.read_csv('https://raw.githubusercontent.com/sweber613/meridian/main/Airports%20with%20Header%20Row%20adapted%20from%20OpenFlights.org.csv')

with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

unemp = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/fips-unemp-16.csv",
                   dtype={"fips": str})


jdata = json.load(open('census_subdivisions_digital_2016.json'))

PRUID = [feat['properties']['CSDUID'] for feat in jdata['features']]
PRENAME = [feat['properties']['CSDNAME'] for feat in jdata['features']]

df = pd.DataFrame(list(zip(PRUID, PRENAME)), columns =['CSDUID', 'CSDNAME'])
df['randNum'] = np.random.uniform(0.0, 1.0, df.shape[0])

class dataLayer:
    def __init__(self, type, graphObject):
        self.type = type
        self.graphObject = graphObject

dataDict = {}
layoutDict = {}

defaultData = 'Canadian population centres'
defaultLayout = 'Street'

dataDict['Canadian population centres'] = dataLayer('scatter',
                                go.Scattermapbox(lon = canada_cities['Longitude'],
                                  lat = canada_cities['Latitude'],
                                  text = canada_cities['Place Name (UTF8) VarChar(200)'],
                                  mode = 'markers',
                                  marker_size = 20,
                                  marker_opacity = 1.0)
                              )

dataDict['USA cities'] = dataLayer('scatter',
                            go.Scattermapbox(lon = us_cities['lon'],
                               lat = us_cities['lat'],
                               text = us_cities['City'],
                               mode = 'markers',
                               marker_size = 10,
                               marker_opacity = 1.0)
                           )

dataDict['Airports'] = dataLayer('scatter',
                        go.Scattermapbox(lon = airports['Longitude'],
                           lat = airports['Latitude'],
                           text = airports['Name'],
                           mode = 'markers',
                           marker_size = 10,
                           marker_opacity = 1.0)
                       )

# dataDict['Unemp'] = dataLayer('choropleth',
#                         go.Choroplethmapbox(geojson=counties,
#                             locations=unemp['fips'],
#                             z=unemp['unemp'],
#                             colorscale="Viridis",
#                             marker_line_width=.5)
#                       )

dataDict['CensusDivisions'] = dataLayer('choropleth',
                        go.Choroplethmapbox(z=df['randNum'],
                            locations=df['CSDUID'],
                            featureidkey='properties.CSDUID',
                            colorscale="Viridis",
                            marker_line_width=.5,
                            geojson=jdata,
                            text=df['CSDNAME'],
                            marker_opacity=0.33)
                    )

layoutDict['Street'] = go.Layout(mapbox_style="open-street-map", height=1000, mapbox = {'zoom' : 3, 'center_lat' : 65, 'center_lon' : -105}, margin={"r":0,"t":0,"l":0,"b":0})

layoutDict['Satellite'] = go.Layout(
                        mapbox_style="white-bg",
                        mapbox_layers=[
                            {
                                "below": 'traces',
                                "sourcetype": "raster",
                                "sourceattribution": "United States Geological Survey",
                                "source": [
                                    "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
                                ]
                            }
                        ],
                        mapbox = {'zoom' : 3, 'center_lat' : 65, 'center_lon' : -105},
                        height=1000,
                        margin={"r":0,"t":0,"l":0,"b":0}
                    )

fig = go.Figure(layout=layoutDict[defaultLayout], data=dataDict[defaultData].graphObject)

app.layout = html.Div([
                html.Div([
                    dcc.Tabs(id='map-configuration-tabs', value='basemap-tab', children=[
                        dcc.Tab(value='basemap-tab', label='Basemap', children=[
                            dcc.Dropdown(
                                id='basemap-dropdown',
                                options=list(layoutDict.keys()),
                                value=defaultLayout
                            )
                        ]),
                        dcc.Tab(value='standard-overlay-tab', label='Standard Overlays', children=[
                            dcc.Checklist(
                                list(dataDict.keys()),
                                [defaultData],
                                id='data-checklist'
                            ),
                            dcc.Tabs(id='standard-overlay-configuration-tabs', children=[])
                        ]),
                        dcc.Tab(value='custom-overlay-tab', label='Custom Overlays', children=[
                            dcc.Upload(
                                id='upload-data',
                                children=[html.Button('Upload File')]
                            ),
                            dcc.Tabs(id='custom-overlay-configuration-tabs', children=[])
                        ]),
                    ])], style={'width': '14%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                html.Div(
                    dcc.Graph(id='basemap-container', figure=fig),
                    style={'width': '84%', 'display': 'inline-block', 'verticalAlign': 'top'}
                ),
])

def parseCSV(fileContents, fileName):
    content_type, content_string = fileContents.split(',')

    decoded = base64.b64decode(content_string)
    if 'csv' in fileName:
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))

    return df

@app.callback(
    Output('basemap-container', 'figure'),
    Input('basemap-dropdown', 'value'),
    Input('data-checklist', 'value'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename'),
    Input({'type' : 'marker-size', 'id' : ALL}, 'value'),
    State({'type' : 'marker-size', 'id' : ALL}, 'id'),
    Input({'type' : 'marker-opacity', 'id' : ALL}, 'value'),
    State({'type' : 'marker-opacity', 'id' : ALL}, 'id'),
    Input({'type' : 'colour-picker', 'id' : ALL}, 'value'),
    State({'type' : 'colour-picker', 'id' : ALL}, 'id'),
)
def updateMapFigure(basemap, datasets, content, filename, sizeValues, sizeIds, opacityValues, opacityIds, colourValues, colourIds):
    mapData = []
    print(colourValues, colourIds)
    for data in datasets:
        for i, id in enumerate(sizeIds):
            if(id['id'] == data):
                dataDict[data].graphObject.marker.size = sizeValues[i]
        for i, id in enumerate(opacityIds):
            if(id['id'] == data):
                dataDict[data].graphObject.marker.opacity = opacityValues[i]
        for i, id in enumerate(colourIds):
            if(id['id'] == data):
                dataDict[data].graphObject.marker.color = colourValues[i]['hex']
        mapData.append(dataDict[data].graphObject)

    if content is not None:
        userDF = parseCSV(content, filename)
        dataDict['userData'] = dataLayer('scatter',
                                    go.Scattermapbox(lon = userDF['Longitude'],
                                       lat = userDF['Latitude'],
                                       text = userDF['Name'],
                                       mode = 'markers',
                                       marker_size = 10,
                                       marker_opacity = 1.0)
                               )
        mapData.append(dataDict['userData'].graphObject)
    return go.Figure(data = mapData, layout = layoutDict[basemap])

@app.callback(
    Output('standard-overlay-configuration-tabs', 'children'),
    Input('data-checklist', 'value'),
)
def defineDataTabs(datasets):
    tabs = []
    for data in datasets:
        children = []
        if dataDict[data].type == 'scatter':
            children.append(html.H3('Size'))
            children.append(
                dcc.Input(type='number', debounce=True, value=10, min=0, max=100, step=1, id={
                    'type' : 'marker-size',
                    'id' : data
                }))
            children.append(html.H3('Opacity'))
            children.append(
                dcc.Input(type='number', debounce=True, value=1, min=0, max=1, step=0.01,id={
                    'type' : 'marker-opacity',
                    'id' : data
                }))
            children.append(html.H3('Colour'))
            children.append(
                daq.ColorPicker(value=dict(hex='#119DFF'),id={
                    'type' : 'colour-picker',
                    'id' : data
                }))
        tabs.append(dcc.Tab(value=data, label=data, children=children))
    return tabs

if __name__ == "__main__":
    app.run_server(debug=True)
