import dash
import base64
import io
from dash import dcc
from dash import html, ctx
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_daq as daq
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from urllib.request import urlopen
import json
import numpy as np
from traceHelpers import *
import base64

logo = 'meridianLogo.png'
logo_base64 = base64.b64encode(open(logo, 'rb').read()).decode('ascii')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

mapboxToken = 'pk.eyJ1Ijoic3dlYmVyNjEzIiwiYSI6ImNsNDMwaGQ5NzE0N3AzZG9menk4cWljMWQifQ.jkgByHIsA8MOWgULENoDJA'

px.set_mapbox_access_token(mapboxToken)

app = dash.Dash(
    __name__, external_stylesheets=external_stylesheets
)

# read in canadian city data
canada_cities = pd.read_csv('https://raw.githubusercontent.com/sweber613/meridian/main/Canadian%20Population%20Centres%20-%20Adapted%20From%20GeoNames.org.csv', encoding = "ISO-8859-1")

us_cities = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/us-cities-top-1k.csv")

airports = pd.read_csv('https://raw.githubusercontent.com/sweber613/meridian/main/Airports%20with%20Header%20Row%20adapted%20from%20OpenFlights.org.csv')

with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

unemp = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/fips-unemp-16.csv", dtype={"fips": str})

with urlopen('https://raw.githubusercontent.com/sweber613/meridian/main/census_subdivisions_simple_2016.json') as response:
    census_subdivisions = json.load(response)

mean_age = pd.read_csv('https://raw.githubusercontent.com/sweber613/meridian/main/2016%20Censsus%20-%20Mean%20Age%20by%20CSD.csv', encoding = "ISO-8859-1")

airport_great_circles = pd.read_csv('https://raw.githubusercontent.com/sweber613/meridian/main/Example%20Data%20-%20Airports%20for%20Great%20Circles.csv', encoding = "ISO-8859-1")


from geohexviz.builder import PlotBuilder

myBuilder = PlotBuilder()

# set hexbin layer
myBuilder.set_hexbin(
    data="Fish Sampling Locations for Hexagonal Binning.csv",
    hexbin_info=dict(
        hex_resolution=4,
    ),
    manager=dict(
        marker=dict(
            line=dict(
                width=0.1
            )
        ),
        # colorscale="Dark24"
    )
)

myBuilder.set_mapbox(mapboxToken)

# add region layers
myBuilder.add_region(
    name="sample_Region_Canada",
    data="CANADA"
)

# add grid layers
myBuilder.add_grid(
    name="sample_Grid_Canada",
    data="CANADA"
)

# alter figure layout
myBuilder.update_figure(
    layout=dict(
        legend=dict(
            x=0.8043,
            bordercolor="black",
            borderwidth=1,
            font=dict(
                size=8
            )
        )
    )
)

# invoke functions
myBuilder.clip_layers(
    clip="hexbin+grids",
    to="regions"
)
myBuilder.adjust_focus(
    on="hexbin+grids",
    buffer_lat=[0, 15],
    rot_buffer_lon=-8
)

# finalize and output
myBuilder.finalize()
# myBuilder.output(
#     filepath="fish.pdf",
#     # crop_output=True
# )

class dataLayer:
    def __init__(self, type, graphObjects):
        self.type = type
        self.graphObjects = graphObjects

standardDataDict = {}
customDataDict = {}
layoutDict = {}

defaultData = 'Canadian population centres'
defaultLayout = 'Street'

standardDataDict['Fish Observations'] = dataLayer('GeoHexViz',myBuilder._figure['data'])

standardDataDict['Canadian population centres'] = dataLayer('scatter',
                                [go.Scattermapbox(lon = canada_cities['Longitude'],
                                  lat = canada_cities['Latitude'],
                                  text = canada_cities['Place Name (UTF8) VarChar(200)'],
                                  mode = 'markers',
                                  marker_size = 20,
                                  marker_opacity = 1.0,
                                  name='Canadian population centres')]
                              )

standardDataDict['USA cities'] = dataLayer('scatter',
                            [go.Scattermapbox(lon = us_cities['lon'],
                               lat = us_cities['lat'],
                               text = us_cities['City'],
                               mode = 'markers',
                               marker_size = 10,
                               marker_opacity = 1.0,
                               name='USA cities')]
                           )

standardDataDict['Airports'] = dataLayer('scatter',
                        [go.Scattermapbox(lon = airports['Longitude'],
                           lat = airports['Latitude'],
                           text = airports['Name'],
                           mode = 'markers',
                           marker_size = 10,
                           marker_opacity = 1.0,
                           name='Airports')]
                       )

# standardDataDict['Air traffic'] = dataLayer('arcs',
#                                             [get_geo_arcs(airport_great_circles, 3, 'rgba(255,0,0,0.5)')])


standardDataDict['Air traffic'] = dataLayer('arcs', get_geo_arc_arrows(airport_great_circles))

# standardDataDict['Unemp'] = dataLayer('choropleth',
#                         go.Choroplethmapbox(geojson=counties,
#                             locations=unemp['fips'],
#                             z=unemp['unemp'],
#                             colorscale="Viridis",
#                             marker_line_width=.5)
#                       )

standardDataDict['Mean Age'] = dataLayer('choropleth',
                        [go.Choroplethmapbox(z=mean_age['MEAN_AGE'],
                            locations=mean_age['GEO_CODE'],
                            featureidkey='properties.CSDUID',
                            colorscale="Viridis",
                            marker_line_width=.5,
                            geojson=census_subdivisions,
                            text=mean_age['GEO_NAME'],
                            marker_opacity=0.33,
                            name='Mean Age')]
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

fig = go.Figure(layout=layoutDict[defaultLayout], data=standardDataDict[defaultData].graphObjects)

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
                                list(standardDataDict.keys()),
                                [defaultData],
                                id='standard-data-checklist'
                            ),
                            dcc.Tabs(id='standard-overlay-configuration-tabs', children=[])
                        ]),
                        dcc.Tab(value='custom-overlay-tab', label='Custom Overlays', children=[
                            dcc.Upload(
                                id='upload-data',
                                children=[html.Button('Upload File')]
                            ),
                            dcc.Checklist(
                                list(customDataDict.keys()),
                                id='custom-data-checklist'
                            ),
                            dcc.Tabs(id='custom-overlay-configuration-tabs', children=[])
                        ]),
                    ])], style={'width': '14%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                html.Div(
                    dcc.Graph(id='basemap-container', figure=fig),
                    style={'width': '84%', 'display': 'inline-block', 'verticalAlign': 'top'}
                ),
                html.Div([
                    html.Img(src='data:image/png;base64,{}'.format(logo_base64))
                ]),
])

def parseCSV(fileContents, fileName):
    content_type, content_string = fileContents.split(',')

    decoded = base64.b64decode(content_string)
    if 'csv' in fileName:
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))

    return df

@app.callback(
    Output('custom-data-checklist', 'options'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename'),
)
def importCustomData(content, filename):
    if content is not None:
        userDF = parseCSV(content, filename)
        customDataDict['User Data'] = dataLayer('scatter',
                                    [go.Scattermapbox(lon = userDF['Longitude'],
                                       lat = userDF['Latitude'],
                                       text = userDF['Name'],
                                       mode = 'markers',
                                       marker_size = 10,
                                       marker_opacity = 1.0,
                                       name='User Data')]
                               )
    return list(customDataDict.keys())

@app.callback(
    Output('basemap-container', 'figure'),
    Input('basemap-dropdown', 'value'),
    Input('standard-data-checklist', 'value'),
    Input('custom-data-checklist', 'value'),
    State('basemap-container', 'figure'),
    Input({'type' : 'marker-size', 'id' : ALL}, 'value'),
    State({'type' : 'marker-size', 'id' : ALL}, 'id'),
    Input({'type' : 'marker-opacity', 'id' : ALL}, 'value'),
    State({'type' : 'marker-opacity', 'id' : ALL}, 'id'),
    Input({'type' : 'colour-picker', 'id' : ALL}, 'value'),
    State({'type' : 'colour-picker', 'id' : ALL}, 'id'),
)
def updateMapFigure(basemap, standardDatasets, customDatasets, figureState, sizeValues, sizeIds, opacityValues, opacityIds, colourValues, colourIds):

    # get current map position
    zoom = figureState['layout']['mapbox']['zoom']
    center_lat = figureState['layout']['mapbox']['center']['lat']
    center_lon = figureState['layout']['mapbox']['center']['lon']

    figureData = figureState['data']

    # print(ctx.triggered_id == 'standard-data-checklist')
    # print(ctx.triggered_id)
    #
    # if ctx.triggered_id == 'standard-data-checklist':
    #     for data in standardDatasets:
    #         if data == figData['name'] for figdata in figureData:
    #             continue
    #         figureData += standardDataDict[data].graphObjects

    mapData = []
    standardData = []
    for data in standardDatasets:
        for i, id in enumerate(sizeIds):
            if(id['id'] == data):
                standardDataDict[data].graphObjects[0].marker.size = sizeValues[i]
        for i, id in enumerate(opacityIds):
            if(id['id'] == data):
                standardDataDict[data].graphObjects[0].marker.opacity = opacityValues[i]
        for i, id in enumerate(colourIds):
            if(id['id'] == data):
                standardDataDict[data].graphObjects[0].marker.color = colourValues[i]['hex']
        standardData += standardDataDict[data].graphObjects

    customData = []
    if customDatasets:
        for data in customDatasets:
            for i, id in enumerate(sizeIds):
                if(id['id'] == data):
                    customDataDict[data].graphObjects[0].marker.size = sizeValues[i]
            for i, id in enumerate(opacityIds):
                if(id['id'] == data):
                    customDataDict[data].graphObjects[0].marker.opacity = opacityValues[i]
            for i, id in enumerate(colourIds):
                if(id['id'] == data):
                    customDataDict[data].graphObjects[0].marker.color = colourValues[i]['hex']
            customData += customDataDict[data].graphObjects

    mapData = standardData + customData
    layout = layoutDict[basemap]
    layout.mapbox.zoom = zoom
    layout.mapbox.center.lat = center_lat
    layout.mapbox.center.lon = center_lon
    return go.Figure(data = mapData, layout = layout)

@app.callback(
    Output('standard-overlay-configuration-tabs', 'children'),
    Input('standard-data-checklist', 'value'),
)
def defineStandardDataTabs(datasets):
    tabs = []
    if datasets:
        for data in datasets:
            children = []
            if standardDataDict[data].type == 'scatter':
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
            if standardDataDict[data].type == 'choropleth':
                children.append(html.H3('Opacity'))
                children.append(
                    dcc.Input(type='number', debounce=True, value=1, min=0, max=1, step=0.01,id={
                        'type' : 'marker-opacity',
                        'id' : data
                    }))
            tabs.append(dcc.Tab(value=data, label=data, children=children))
    return tabs

@app.callback(
    Output('custom-overlay-configuration-tabs', 'children'),
    Input('custom-data-checklist', 'value'),
)
def defineCustomDataTabs(datasets):
    tabs = []
    if datasets:
        for data in datasets:
            children = []
            if customDataDict[data].type == 'scatter':
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
            if customDataDict[data].type == 'choropleth':
                children.append(html.H3('Opacity'))
                children.append(
                    dcc.Input(type='number', debounce=True, value=1, min=0, max=1, step=0.01,id={
                        'type' : 'marker-opacity',
                        'id' : data
                    }))
            tabs.append(dcc.Tab(value=data, label=data, children=children))
    return tabs

if __name__ == "__main__":
    app.run_server(debug=True)
