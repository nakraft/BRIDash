'''
Used to build maps of details within a country regarding Chinese Influence. 
Data includes: immigration, financial expenditures, public opinion data. 
'''

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
    map = maps.build_map(location, 5)
    # TODO perhaps implement fit_bounds. 
    # Possible by generating a sample of points on the border, extracting sw and ne most points 
    # and then adding that to a bounding box through maps.fit_bounds([sw, ne])

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
    try: 
        map = plot_institutes(df['country_id'][0], map)  
    except Exception:
        print("No data recieved for confucius institutes. Plot a different value.") 

    try: 
        plot_finance(df['country_id'][0]).add_to(map)  
    except Exception:
        print("No data recieved for expenditures. Plot a different value.") 

    # map = plot_immigration(country)

    folium.LayerControl(collapsed=True).add_to(map)

    return maps.html_json(map)

def build_graphs(country_id, type): 
    
    graph = temp_graph.build_graph(country_id, type)
    return graph

def plot_finance(country_id): 

    expend = folium.FeatureGroup(name='Financial Expenditures')

    # plotting finance is split into two goals 
    # PART 1: point locations of expenditures 
    df = db.get_expend_data(country_id, 'city')
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

    # for loc in range(0, len(df_r)):
    #     type_color = "red"
    #     iframe = folium.IFrame(''' 
    #                             <html>
    #                             <p>
    #                             Project: {title} <br>
    #                             Status: {status} <br>
    #                             </p>
    #                             </html> 
    #                             '''.format(**df_dict[loc]))
    #     pop = folium.Popup(iframe, min_width=300, max_width=300)

    #     folium.Marker(location = [df['latitude'][loc], df['longitude'][loc]], # Add in popup 
    #                     popup = pop,
    #                     icon = folium.Icon(color = '%s' % type_color)).add_to(market_cluster_expend)

    # market_cluster_expend.add_to(expend)

    return expend

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
