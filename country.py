'''
Used to build maps of details within a country regarding Chinese Influence. 
Data includes: immigration, financial expenditures, public opinion data. 
'''

from datetime import date
import pandas as pd
import folium
from folium.plugins import MarkerCluster

import maps
import db
import temp_graph


'''
Builds a map with all the data combined for this country of interest
Parameters: 
df: geodataframe of country of interest
Return: html rendering of map
'''
def build_layers(df): 

    country = df['country'].item()
    print("working on " + country)

    # determine center of map
    location = maps.determine_center(df)

    # define mapping parameters
    map = maps.build_map(location, 2, 'country')
    map.fit_bounds(maps.determine_bounds(df))

    # puts the country boundary on the map 
    outline = folium.FeatureGroup(name='outline', control=False)
    geo_j = df['geometry'].to_json()
    geo_j = folium.GeoJson(data=geo_j,
                            style_function=lambda x: {'fillColor': 'light blue'})
    
    # add in country overall details
    folium.Popup(
        f''' 
        <html>
        <h3> 
        {country}: 
        </h3>
        <p>
        Explore what data has been collected for {country}. No further regional divisions have been established for this region.
        </p>
        </html> 
        '''
    ).add_to(geo_j)
    outline.add_child(geo_j)
    outline.add_to(map)

    # plot different data layers
    # make sure these are limited by year 
    try: 
        map = plot_institutes(df['country_id'][0], map)  
    except Exception:
        print("No data recieved for confucius institutes. Plot a different value.") 

    date_range = [2000, 2024]
    try: 
        map, date_range_f = plot_finance(df['country_id'][0], map)
        if date_range_f != None: 
            date_range = [min(date_range[0], date_range_f[0]), max(date_range[1], date_range_f[1])]
            print(date_range)
    except Exception:
        print("No data recieved for expenditures. Plot a different value.") 

    try: 
        map, date_range_p = plot_public_opinions(df['country_id'][0]).add_to(map) 
        # date_range = [min(date_range[0], date_range_p[0]), max(date_range[1], date_range_p[1])] 
    except Exception: 
        print("No data recieved for public opinions. Plot a different value.") 

    # map = plot_immigration(country)

    folium.LayerControl(collapsed=True).add_to(map)
    # [min(date_range_f[0], date_range_p[0]), max(date_range_f[1], date_range_p[1])]

    return [maps.html_json(map), date_range]

def build_graphs(country_id, type): 
    
    graph = temp_graph.build_graph(country_id, type)
    return graph

def plot_finance(country_id, map): 

    expend = folium.FeatureGroup(name='Financial Expenditures')

    # plotting finance is split into two goals 
    # PART 1: point locations of expenditures 
    df = db.get_expend_data(country_id, 'city')
    date_range = [min(df['commitment_year']), max(df['commitment_year'])]

    print("Country #" + str(country_id) + " financials being loaded." + str(len(df)) + " records found for cities.")

    df_dict = df.to_dict('records')

    market_cluster_expend = MarkerCluster(name = "Expend") # no known options for tooltip on cluster, but you can change cluster icon with icon_create_function

    for loc in range(0, len(df)):
        type_color = "red"
        iframe = folium.IFrame(''' 
                                <html>
                                <p>
                                Project: {title} <br>
                                Status: {status} <br>
                                </p>
                                </html> 
                                '''.format(**df_dict[loc]))
        pop = folium.Popup(iframe, min_width=300, max_width=300)

        folium.Marker(location = [df['latitude'][loc], df['longitude'][loc]], # Add in popup 
                        popup = pop,
                        icon = folium.Icon(color = '%s' % type_color)).add_to(market_cluster_expend)

    market_cluster_expend.add_to(expend)

    # PART 2: regional locations of expenditures 
    df_r = db.get_expend_data(country_id, 'region')

    dfr_dict = df[['title', 'status']].to_dict('records')
    for ele in range(0, len(df_r)):
        geo_j = df_r['geometry'].to_json()
        geo_j = folium.GeoJson(data=geo_j,
                                style_function=lambda x: {'fillColor': 'red'})
        
        print(dfr_dict[ele]['title'])
        pop = folium.Popup(''' 
                                <html>
                                <p>
                                Project: {title} <br>
                                Status: {status} <br>
                                </p>
                                </html> 
                                '''.format(**dfr_dict[ele]), min_width=300, max_width=300) # TODO: fix bug here, naming convention of regions doesn't change.
        pop.add_to(geo_j)
        expend.add_child(geo_j)

    expend.add_to(map) 

    return map, date_range

def get_finance_country(country_id): 

    df = db.get_expend_data(country_id, 'all')

    # get a list of all project titles
    return df[(pd.isna(df['gl3_id']))]['title']

    # Aggregate country level finances here 

def plot_institutes(country_id, map): 

    df = db.get_institutes_data(country_id)
    print("Country #" + str(country_id) + " institutes being loaded.")

    df_dict = df.to_dict('records')

    confucius_institutes = folium.FeatureGroup(name='Confucius Institutes')
    for loc in range(0, len(df)):
        # TODO: assign a color marker for the type of volcano, Strato being the most common
        #assign color based on status
        # if geo_df.Type[i] == "Stratovolcano":
        #     type_color = "green"
        # elif geo_df.Type[i] == "Complex volcano":
        #     type_color = "blue"
        type_color = "blue"

        # generate the popup 
        iframe = folium.IFrame(''' 
                                <html>
                                <p>
                                <a href=\"{ci_webpage}\"> 
                                {confucius_institute}: 
                                </a>   

                                <br>
                                Esablished: {date_est} <br>
                                Status: {status} <br>
                                Partner University: {partner_uni} <br>
                                </p>
                                </html> 
                                '''.format(**df_dict[loc]))
        pop = folium.Popup(iframe, min_width=300, max_width=300)

        # Place the markers with the popup labels and data
        confucius_institutes.add_child(folium.Marker(location = [df['latitude'][loc], df['longitude'][loc]],
                                # Add in popup 
                                popup = pop,
                                icon = folium.Icon(color = '%s' % type_color)))

    confucius_institutes.add_to(map)

    return map 

def plot_public_opinions(country_id): 

    df = db.get_public_opinion(country_id)

    if len(df) == 0: 
        raise Exception

    # myscale = (df[choro_var].quantile((0,0.1,0.75,0.9,0.98,1))).tolist()
    choro = folium.Choropleth(
        geo_data=df,
        name='Public Opinion',
        data=df,
        columns=['shape_name', 'us_econ_power'],
        key_on="feature.properties.shape_name",
        fill_color='YlGnBu',
        # threshold_scale=myscale,
        fill_opacity=1,
        line_opacity=0.2,
        legend_name='filler', # Make this dynamic based on question
        smooth_factor=0, 
        nan_fill_color = '#bababa'
    )

    choro.geojson.add_child(
        folium.features.GeoJsonTooltip(fields=[
                                            'shape_name', 
                                            'us_econ_power', 
                                            'china_econ_power'
                                            ],
                                        aliases=[
                                            "Shape Name: ", 
                                            "US Econ Power: ", 
                                            "China Econ Power: "
                                            ],
                                        style=("background-color: white; color: white; font-family: arial; font-size: 12px; padding: 10px;"))
    )

    return choro