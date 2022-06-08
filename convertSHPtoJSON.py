import geopandas as gpd

geodf = gpd.read_file('..\CensusSubdivisionsDigital2016\lcsd000a16a_e.shp')
geodf_wgs84 = geodf.to_crs({'init': 'epsg:4326'})

geodf_wgs84.to_file('census_subdivisions_digital_2016.json', driver='GeoJSON')
