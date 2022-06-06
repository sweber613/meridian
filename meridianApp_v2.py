import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

px.set_mapbox_access_token('pk.eyJ1Ijoic3dlYmVyNjEzIiwiYSI6ImNsNDMwaGQ5NzE0N3AzZG9menk4cWljMWQifQ.jkgByHIsA8MOWgULENoDJA')

app = dash.Dash(
    __name__,
)

# read in canadian city data
df = pd.read_csv('https://gist.githubusercontent.com/curran/13d30e855d48cdd6f22acdf0afe27286/raw/0635f14817ec634833bb904a47594cc2f5f9dbf8/worldcities_clean.csv')
df = df[df['country'] == 'Canada']
df['text'] = df['city'] + ', pop ' + df['population'].astype(str)

us_cities = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/us-cities-top-1k.csv")

airports = pd.read_csv('https://raw.githubusercontent.com/sweber613/meridian/main/Airports%20with%20Header%20Row%20adapted%20from%20OpenFlights.org.csv')

dataDict = {}
layoutDict = {}

defaultData = 'Canadian cities'
defaultLayout = 'Satellite'

dataDict['Canadian cities'] = go.Scattermapbox(lon = df['lng'],
                              lat = df['lat'],
                              text = df['text'],
                              mode = 'markers',
                              marker_color = df['population'],
                              marker_size = 20,
                              marker_opacity = 0.33)

dataDict['USA cities'] = go.Scattermapbox(lon = us_cities['lon'],
                           lat = us_cities['lat'],
                           text = us_cities['City'],
                           mode = 'markers',
                           marker_size = 10,
                           marker_opacity = 1.0)

dataDict['Airport'] = go.Scattermapbox(lon = airports['Longitude'],
                           lat = airports['Latitude'],
                           text = airports['Name'],
                           mode = 'markers',
                           marker_size = 10,
                           marker_opacity = 1.0)


layoutDict['Street'] = go.Layout(mapbox_style="open-street-map", height=800, margin={"r":0,"t":0,"l":0,"b":0})

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
                        height=800,
                        margin={"r":0,"t":0,"l":0,"b":0}
                    )



fig = go.Figure(layout=layoutDict[defaultLayout], data=dataDict[defaultData])

app.layout = html.Div([
                html.Div([
                    dcc.Dropdown(
                        id='basemap-dropdown',
                        options=list(layoutDict.keys()),
                        value=defaultLayout
                    ),
                    dcc.Checklist(
                        list(dataDict.keys()),
                        [defaultData],
                        id='data-checklist'
                    )],
                    style={'width': '14%', 'display': 'inline-block'}
                ),
                html.Div(
                    dcc.Graph(id='basemap-container', figure=fig),
                    style={'width': '84%', 'display': 'inline-block'}
                ),
])

@app.callback(
    Output('basemap-container', 'figure'),
    Input('basemap-dropdown', 'value'),
    Input('data-checklist', 'value'),
)
def updateMapFigure(basemap, datasets):
    mapData = []
    for data in datasets:
        mapData.append(dataDict[data])
    return go.Figure(data = mapData, layout = layoutDict[basemap])

if __name__ == "__main__":
    app.run_server(debug=True)
