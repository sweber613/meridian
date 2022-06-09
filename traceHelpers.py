import great_circle_calculator.great_circle_calculator as gcc
import plotly.graph_objects as go
# TRACE HELPERS ============================================================================

#great a great circle arc from p1 (lon/lat) to p2 (lon,lat)
def make_geo_arc(p1, p2, steps=50):
  lon = []
  lat = []

  for i in range(steps+1):
    loc = gcc.intermediate_point(p1,p2,i/50)

    lon.append(loc[0])
    lat.append(loc[1])

  #insert break in lat/lon data to string together multiple arcs if needed
  lon.append(None)
  lat.append(None)

  return lon, lat


#returns a plotly graph object of arcs given a pandas dataframe
#required dataframe fields: 'Latitude 1', 'Longitude 1', 'Latitude 2', 'Longitude 2'
def get_geo_arcs(df, width, color):

  lon = []
  lat = []

  for idx, row in df.iterrows():
    lat1 = row['Latitude 1']
    lon1 = row['Longitude 1']
    lat2 = row['Latitude 2']
    lon2 = row['Longitude 2']

    #plot arc
    i, j = make_geo_arc((lon1,lat1), (lon2,lat2))

    lon.extend(i)
    lat.extend(j)

  gobj = go.Scattermapbox(lon = lon,
                          lat = lat,
                          mode = 'lines',
                          line = dict(width=width, color=color))

  return gobj






def make_geo_arrow_mercator(p1, p2, width, width_scale=100000, lateral_offset=10000, steps=50):

  lon = []
  lat = []

  #arrowhead length
  ah = width*width_scale*4

  #half width
  hw = width*width_scale

  #bearings
  b1 = gcc.bearing_at_p1(p1,p2)
  b2 = gcc.bearing_at_p2(p1,p2)

  #lateral offset p1 and p2
  p1 = gcc.point_given_start_and_bearing(p1, b1 - 90, lateral_offset)
  p2 = gcc.point_given_start_and_bearing(p2, b2 - 90, lateral_offset)

  #distance
  dist = gcc.distance_between_points(p1,p2)

  pi = []
  ei = []

  for i in range(steps+1):
    s = (i/steps)*(dist-ah)/dist
    w = s*50/(1+s*50)*hw

    pi.append(gcc.intermediate_point(p1,p2,s))
    bi = gcc.bearing_at_p1(pi[i],p2)
    ei.append(gcc.point_given_start_and_bearing(pi[i], bi - 90, w))

  ei.append(gcc.point_given_start_and_bearing(pi[-1], bi - 100, 2*w))

  #extra steps at head
  h_steps = 2
  for i in range(h_steps):
    s = ((dist-ah) + (i+1)/(h_steps+1)*ah)/dist
    pi.append(gcc.intermediate_point(p1,p2,s))

  #build lon/lat lists
  lon = [e[0] for e in ei]
  lat = [e[1] for e in ei]

  lon += [p2[0]]
  lat += [p2[1]]

  lon += [p[0] for p in reversed(pi)]
  lat += [p[1] for p in reversed(pi)]

  return lon, lat



def get_geo_arc_arrows(df):

  gos = []

  loc_names = []
  loc_lats = []
  loc_lons = []

  #plot arcs
  for idx, row in df.iterrows():
    loc1 = row['Airport 1']
    loc2 = row['Airport 2']
    lat1 = row['Latitude 1']
    lon1 = row['Longitude 1']
    lat2 = row['Latitude 2']
    lon2 = row['Longitude 2']
    s = row['Strength']

    #save locations
    if loc1 not in loc_names:
      loc_names.append(loc1)
      loc_lats.append(lat1)
      loc_lons.append(lon1)

    if loc2 not in loc_names:
      loc_names.append(loc2)
      loc_lats.append(lat2)
      loc_lons.append(lon2)

    #plot arc
    lon, lat = make_geo_arrow_mercator((lon1,lat1), (lon2,lat2), s/100, lateral_offset=0)

    gos.append(go.Scattermapbox(lon = lon,
                                lat = lat,
                                mode = 'lines',
                                line = dict(width = 0, color = 'green'),
                                fill = 'toself'))

  #plot points and labels
  gos.append(go.Scattermapbox(
    lon = loc_lons,
    lat = loc_lats,
    text = loc_names,
    textposition = 'top center',
    mode = 'markers+text'))

  return gos
