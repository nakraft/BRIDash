'''
Used to build maps of details within a country regarding Chinese Influence. 
Data includes: immigration, financial expenditures, public opinion data. 
'''

from datetime import date
import pandas as pd
import folium
from folium.plugins import MarkerCluster, BeautifyIcon
import plotly.graph_objects as go

import maps
import db
import temp_graph

import gauge
import HomeButton

'''
Builds a map with all the data combined for this country of interest
Parameters: 
df: geodataframe of country of interest
Return: html rendering of map
'''
def build_layers(df, timerange, details): 

    country = df['country'].item()
    print("working on " + country)

    # determine center of map
    location = maps.determine_center(df)

    # define mapping parameters
    map = maps.build_map(location, 2, 'country')
    bounds = maps.determine_bounds(df)
    map.fit_bounds(bounds)

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
    print(details)
    # plot different data layers
    # make sure these are limited by year 
    try: 
        if details != None and details['ci_status'] != '': 
            map = plot_institutes(df['country_id'][0], map, timerange, details['ci_status'])  
        else: 
            map = plot_institutes(df['country_id'][0], map, timerange, None)  
    except Exception:
        print("No data recieved for confucius institutes. Plot a different value.") 

    try: 
        if details != None: 
            map = plot_finance(df['country_id'][0], map, timerange, details['expenditure_type'], details['donor_name'], details['keyword_search'])
        else: 
            map = plot_finance(df['country_id'][0], map, timerange, None, None, None)
    except Exception:
        print("No data recieved for expenditures. Plot a different value.") 

    try: 
        if details != None: 
            map = plot_public_opinions(df['country_id'][0], map, timerange, {'wealthy' : details['wealthy'], 'religion' : details['religion']})
        else: 
            map = plot_public_opinions(df['country_id'][0], map, timerange, {'wealthy' : '', 'religion' : ''}) 

    except Exception as err: 
        print(err)
        print("No data recieved for public opinions. Plot a different value.") 

    # map = plot_immigration(country)

    folium.LayerControl(collapsed=True).add_to(map)
    # [min(date_range_f[0], date_range_p[0]), max(date_range_f[1], date_range_p[1])]
    map.add_child(HomeButton.HomeButton(bounds))

    return maps.html_json(map)

def build_graphs(country_id, type, timerange, expenditure_type, donor_name, keyword_search): 
    
    graph = temp_graph.build_graph(country_id, type, timerange, expenditure_type, donor_name, keyword_search)
    return graph

def plot_finance(country_id, map, timerange, expenditure_type, donor_name, keyword_search): 

    print("Timerange is: ", timerange[0] != None, timerange[1] != None)

    expend = folium.FeatureGroup(name='Financial Expenditures')

    # plotting finance is split into two goals 
    # PART 1: point locations of expenditures 
    df = db.get_expend_data(country_id, 'city', timerange[0], timerange[1], expenditure_type, donor_name, keyword_search)
    date_range = [min(df['commitment_year']), max(df['commitment_year'])]
    if timerange[0] != None and timerange[1] != None: 
        df = df.loc[(df['commitment_year'] == None) | ((df['commitment_year'] <= timerange[1]) & (df['commitment_year'] >= timerange[0]))].reset_index() 

    print("Country #" + str(country_id) + " financials being loaded. " + str(len(df)) + " records found for cities.")

    df_dict = df[['title', 'status', 'sector_name', 'description', 'commitment_year', 'completion_year', 'amount_constant2017']].to_dict('records')

    market_cluster_expend = MarkerCluster(name = "Expend") # no known options for tooltip on cluster, but you can change cluster icon with icon_create_function

    expenditure_key = {
        'EDUCATION' : '#AF1D1D', 
        'TRANSPORT AND STORAGE' : '#FBD61D', 
        'ENERGY' : '#1E9912', 
        'COMMUNCIATIONS' : '#0356C6', 
        'COMMUNICATIONS' : '#0356C6', 
        'INDUSTRY, MINING AND CONSTRUCTION' : '#8519B0', 
        'HEALTH' : '#DE769A'
    }
    for loc in range(0, len(df)):
        type_color = expenditure_key.get(df_dict[loc]['sector_name'], "#F50404")
        pop = folium.Popup(''' 
                                <html>
                                <table id ="t01" style="background-color: white; color: white; font-family: arial; font-size: 12px; padding: 10px;">
                                    <tr> 
                                        <td> Project </td>
                                        <td> {title} </td>
                                    </tr>
                                    <tr> 
                                        <td> Sector </td>
                                        <td> {sector_name} </td>
                                    </tr>
                                    <tr> 
                                        <td> Amount 2017 USD </td>
                                        <td> {amount_constant2017} </td>
                                    </tr>
                                    <tr> 
                                        <td> Scheduled </td>
                                        <td> {commitment_year} - {completion_year} </td>
                                    </tr>
                                    <tr> 
                                        <td> Status </td>
                                        <td> {status} </td>
                                    </tr>
                                    <tr> 
                                        <td> Description </td>
                                        <td> {description} </td>
                                    </tr>
                                </table>
                                </html> 
                                '''.format(**df_dict[loc]), min_width=300, max_width=700)

        folium.Marker(location = [df['latitude'][loc], df['longitude'][loc]], # Add in popup 
                        popup = pop,
                        icon = BeautifyIcon(border_color = type_color, background_color = type_color)).add_to(market_cluster_expend)

    market_cluster_expend.add_to(expend)

    # PART 2: regional locations of expenditures 
    df_r = db.get_expend_data(country_id, 'region', timerange[0], timerange[1], expenditure_type, donor_name, keyword_search)
    if timerange[0] != None and timerange[1] != None: 
        df_r = df_r.loc[(df_r['commitment_year'] == None) | ((df_r['commitment_year'] <= timerange[1]) & (df_r['commitment_year'] >= timerange[0]))].reset_index()
        print(df_r.shape)

    dfr_dict = df[['title', 'status', 'sector_name', 'description', 'commitment_year', 'completion_year', 'amount_constant2017']].to_dict('records')
    for ele in range(0, len(df_r)):
        geo_j = df_r['geometry'].to_json()
        geo_j = folium.GeoJson(data=geo_j,
                                style_function=lambda x: {'fillColor': expenditure_key.get(dfr_dict[ele]['sector_name'].strip(), "#F50404"), 'color': expenditure_key.get(dfr_dict[ele]['sector_name'].strip(), "#F50404")})
        
        pop = folium.Popup(''' 
                                <html>
                                <table id ="t01" style="background-color: white; color: white; font-family: arial; font-size: 12px; padding: 10px;">
                                    <tr> 
                                        <td> Project </td>
                                        <td> {title} </td>
                                    </tr>
                                    <tr> 
                                        <td> Sector </td>
                                        <td> {sector_name} </td>
                                    </tr>
                                    <tr> 
                                        <td> Amount 2017 USD </td>
                                        <td> {amount_constant2017} </td>
                                    </tr>
                                    <tr> 
                                        <td> Scheduled </td>
                                        <td> {commitment_year} - {completion_year} </td>
                                    </tr>
                                    <tr> 
                                        <td> Status </td>
                                        <td> {status} </td>
                                    </tr>
                                    <tr> 
                                        <td> Description </td>
                                        <td> {description} </td>
                                    </tr>
                                </table>
                                </html> 
                                '''.format(**dfr_dict[ele]), min_width=300, max_width=700) # TODO: fix bug here, naming convention of regions doesn't change.
        pop.add_to(geo_j)
        expend.add_child(geo_j)

    expend.add_to(map) 

    # build a gauge for comparison of financial expenditures 
    fig = go.Figure(go.Indicator(
        domain = {'x': [0, 1], 'y': [0, 1]},
        value = db.get_dollar_expend(country_id, timerange[0], timerange[1]),
        mode = "gauge+number+delta",
        delta = {'reference': 4584212384, 'relative': True, 'position' : "bottom"},
        title = {'text': "Financial Expenditures", 'font_color' : 'white', 'font_size' : 40},
        gauge = {'axis': {'range': [None, 125375455552], 'tickcolor':'red', 'tickfont':{'color':'white', 'size':23}},
                'steps' : [
                    {'range': [0, 4584212384], 'color': "red"},
                    {'range': [4584212384, 125375455552], 'color': "darkred"}],
                'threshold' : {'line': {'color': "white", 'width': 4}, 'thickness': 0.75, 'value': 4584212384}, 
                'bar' : {'color':'red'}, 
                'bordercolor' : 'white',
                'shape' : 'angular'},
        number={'font_color':'white', 'font_size':100}))
    fig.update_layout({
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)'
    })

    fig.write_image("static/img/gauge.png") # TODO: need to pass image directly rather than saving for multi-user use

    map.add_child(gauge.Gauge())

    return map

def get_finance_country(country_id, timerange, expenditure_type, donor_name, keyword_search): 

    df = db.get_expend_data(country_id, 'all', timerange[0], timerange[1], expenditure_type, donor_name, keyword_search)
    df = df.loc[(pd.isna(df['gl3_id'])) & (pd.isna(df['gl2_id']))].reset_index()

    expenditure_key = {
        'EDUCATION' : '#AF1D1D', 
        'TRANSPORT AND STORAGE' : '#FBD61D', 
        'ENERGY' : '#1E9912', 
        'COMMUNCIATIONS' : '#0356C6', 
        'COMMUNICATIONS' : '#0356C6', 
        'INDUSTRY, MINING AND CONSTRUCTION' : '#8519B0', 
        'HEALTH' : '#DE769A'
    }
    # get a list of all project titles
    return [(df['title'][x], df['status'][x], df['sector_name'][x], df['description'][x], df['commitment_year'][x], df['completion_year'][x], df['amount_constant2017'][x], expenditure_key.get(df['sector_name'][x], "#F50404")) for x in range(0, len(df))]

    # Aggregate country level finances here 

def plot_institutes(country_id, map, timerange, status): 
    df = db.get_institutes_data(str(country_id), timerange[0], timerange[1], status)
    print("Country #" + str(country_id) + " institutes being loaded.")
    # df = df[df['date_est'] >= timerange(0) & df['date_est'] <= timerange[1]]

    df_dict = df.to_dict('records')

    confucius_institutes = folium.FeatureGroup(name='Confucius Institutes')
    for loc in range(0, len(df)):
        type_color = "blue"

        # generate the popup 
        pop = folium.Popup(''' 
                                <html>
                                <p>
                                <a href=\"{ci_webpage}\"> 
                                {confucius_institute}
                                </a>   
                                <br>
                                <table id ="t01" style="background-color: white; color: white; font-family: arial; font-size: 12px; padding: 10px;">
                                    <tr> 
                                        <td> Established </td>
                                        <td> {date_est}  </td>
                                    </tr>
                                    <tr> 
                                        <td> Status </td>
                                        <td> {status} </td>
                                    </tr>
                                    <tr> 
                                        <td> Partner University </td>
                                        <td> {partner_uni} </td>
                                    </tr>
                                </table>
                                </p>
                                </html> 
                                '''.format(**df_dict[loc]), min_width=300, max_width=300)

        # Place the markers with the popup labels and data
        confucius_institutes.add_child(folium.Marker(location = [df['latitude'][loc], df['longitude'][loc]],
                                # Add in popup 
                                popup = pop,
                                icon = folium.Icon(color = '%s' % type_color)))

    confucius_institutes.add_to(map)

    return map 

def plot_public_opinions(country_id, map, timerange, details): 

    df = db.get_public_opinion(country_id, timerange[0], timerange[1], details)

    if len(df) == 0: 
        raise Exception

    # myscale = (df['china_econ_power'].quantile((0,0.1,0.75,0.9,0.98,1))).tolist()
    base_choro = folium.Choropleth(
        geo_data=df,
        name='Public Opinion',
        data=df,
        columns=['shape_name', 'us_econ_power'],
        key_on="feature.properties.shape_name",
        fill_color='YlGnBu',
        fill_opacity=0,
        line_opacity=1,
        line_color = 'white',
        legend_name='filler', # Make this dynamic based on question
        smooth_factor=0
    )

    base_choro.geojson.add_child(
            folium.features.GeoJsonTooltip(fields=[
                                                'shape_name', 
                                                'us_econ_power', 
                                                'china_econ_power', 
                                                'fav_china'
                                                ],
                                            aliases=[
                                                "Shape Name: ", 
                                                "US Econ Power: ", 
                                                "China Econ Power: ", 
                                                "Favor toward China: "
                                                ],
                                            style=("background-color: white; color: white; font-family: arial; font-size: 12px; padding: 10px;"))
    )

    choro = folium.Choropleth(
        geo_data=df,
        name='US Economic Power',
        data=df,
        columns=['shape_name', 'us_econ_power'],
        key_on="feature.properties.shape_name",
        fill_color='YlGnBu',
        fill_opacity=1,
        line_opacity=1,
        line_color= 'black',
        overlay=True,
        show=False,
        legend_name='filler', # Make this dynamic based on question
        smooth_factor=0, 
        nan_fill_color = '#bababa'
    )
    for key in choro._children:
        if key.startswith('color_map'):
            del(choro._children[key])
    choro.add_to(map)

    # choro.update_layout( showlegend=False)

    choro2 = folium.Choropleth(
        geo_data=df,
        name='China Economic Power',
        data=df,
        columns=['shape_name', 'china_econ_power'],
        key_on="feature.properties.shape_name",
        fill_color='YlGnBu',
        fill_opacity=1,
        line_opacity=1,
        line_color= 'black',
        legend_name='filler', # Make this dynamic based on question
        show=False,
        smooth_factor=0, 
        nan_fill_color = '#bababa'
    )
    for key in choro2._children:
        if key.startswith('color_map'):
            del(choro2._children[key])
    choro2.add_to(map)



    choro3 = folium.Choropleth(
        geo_data=df,
        name='Favorability Toward China',
        data=df,
        columns=['shape_name', 'fav_china'],
        key_on="feature.properties.shape_name",
        fill_color='YlGnBu',
        fill_opacity=1,
        line_opacity=1,
        line_color= 'black',
        legend_name='filler', # Make this dynamic based on question
        smooth_factor=0, 
        nan_fill_color = '#bababa'
    )
    for key in choro3._children:
        if key.startswith('color_map'):
            del(choro3._children[key])
    choro3.add_to(map)

    # for key in base_choro._children:
    #     if key.startswith('color_map'):
    #         print(base_choro._children[key])
    #         base_choro._children[key].include(style="fill: rgb(255, 255, 255);")

    base_choro.add_to(map)

    #TODO: shift base layer to the last layer and combine statistics there about all datasets 

    return map

def get_religion_details(country): 

    return db.get_religion_details(country)

def get_finance_details(country): 

    return db.get_finance_details(country)