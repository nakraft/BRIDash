'''
Used to build Choropleths of Chinese Influence 
'''
import folium 
import maps # abstracts functionality using folium to reduce redundantcies 


'''
Builds a choropleth given a geographic area and a variable of interest. 
Identify configuration of maps in config file. No customization available here. 
Parameters: 
df: geodataframe of world countries 
choro_var: variable name aggregated
Return: html rendering of map
'''
def build_choropleth(df, choro_var): 

    # determine center of map
    location = maps.determine_center(df)
    # define mapping parameters
    map = maps.build_map(location, 2)

    # myscale = (df[choro_var].quantile((0,0.1,0.75,0.9,0.98,1))).tolist()
    choro = folium.Choropleth(
        geo_data=df,
        name='Choropleth',
        data=df,
        columns=['country_id', choro_var],
        key_on="feature.properties.country_id",
        fill_color='YlGnBu',
        # threshold_scale=myscale,
        fill_opacity=1,
        line_opacity=0.2,
        legend_name='filler', # Make this dynamic based on question
        smooth_factor=0, 
        nan_fill_color = '#bababa'
    ).add_to(map)

    choro.geojson.add_child(
        folium.features.GeoJsonTooltip(fields=[
                                            'country_id',
                                            'bri_partner', 
                                            'ldc', 
                                            'landlocked_dc' # note, you could pull over sids (small island developing states)
                                        ],
                                        aliases=[
                                            "Country: ",
                                            "BRI Partner: ", 
                                            "Least Developed: ", 
                                            "Landlocked: "
                                        ],
                                        style=("background-color: white; color: white; font-family: arial; font-size: 12px; padding: 10px;"))
    )

    return maps.html_json(map)