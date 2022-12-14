import pandas as pd
import folium
from flask import Markup

import LatLngPopup

'''
Accesses config file to build a map with the proper specifications. 
Specifications include image size, map center, zoom restrictions, layer settings, 
map type, etc. 
'''
def build_map(location, zoom, level): 

    if level == 'world': 
        m = folium.Map(location=[location[1], location[0]], tiles=None, 
                        zoomSnap = .25, zoomDelta = .25, start_zoom=zoom, 
                        max_bounds = True, min_lat= -52, max_lat=80, min_lon= -145, max_lon=170) # change to location in config file OR center of displayed borders

        m.fit_bounds([[-52, -145], [80, 170]])
    else: 
        m = folium.Map(location=[location[1], location[0]], tiles=None, 
                        zoomSnap = .25, zoomDelta = .25, start_zoom = zoom, 
                        max_bounds = True, min_lat= -52, max_lat=80, min_lon= -145, max_lon=170) # change to location in config file OR center of displayed borders

    folium.TileLayer('cartodbdark_matter',name="Dark Map",control=False).add_to(m) # change to custom layer settings 
    # ensure click gets more details on area
    m.add_child(LatLngPopup.LatLngPopup())

    return m

'''
Convert JSON to HTML to pass to templating pages 

Parameter: folium map to convert
Return: HTML designations for map, header, and accompanying script
'''
def html_json(map): 

    # first, force map to render as HTML, for us to dissect
    _ = map._repr_html_()

    map_div = Markup(map.get_root().html.render())
    hdr_txt = Markup(map.get_root().header.render())
    script_txt = Markup(map.get_root().script.render())

    return map_div, hdr_txt, script_txt

'''
Helper method to determine where the maps center location should be 

Parameter: a geodataframe of shapes
Return: long, lat coordinates of center 
'''
def determine_center(df): 

    loc = df['geometry'].centroid
    lat = pd.Series([float(x.y) for x in loc]).mean()
    lng = pd.Series([float(x.x) for x in loc]).mean()

    return lng, lat

def determine_bounds(df): 
    bounds = df.bounds
    max_lon_south = min(bounds.minx) 
    max_lon_north = max(bounds.maxx)
    min_lat_west = min(bounds.miny)
    max_lat_east = max(bounds.maxy)
    return [[min_lat_west, max_lon_south], [max_lat_east, max_lon_north]]