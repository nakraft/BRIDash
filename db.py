'''
Web application built using postgres database. 
Access to postgres database to load global and intra-country data. 
'''

from ast import Not
import pandas as pd
import geopandas as gpd
import shapely
from shapely.geometry import Point
from sqlalchemy import create_engine

'''
Establishes and returns connection to database. 
'''
def get_db_connection_to_df():
    alchemyEngine = create_engine('postgresql://nakraft:park@127.0.0.1:5435') #TODO: abstract to private file before push to git
    conn = alchemyEngine.connect()
    return conn

'''
Based on user interest in viewing global comparisons, acquire all country files plus an 
aggregated value by country. 
Input: variable to aggregate by country for use in choropleth manipulation 
Output: GeoDataFrame inclusive of aggregated metric to plot
'''
def get_world_data(table, choro_var, aggregate): 

    conn = get_db_connection_to_df()
    countries = pd.read_sql(
                '''
                SELECT country_id, country, geometry, ldc, 
                landlocked_dc, sids, bri_partner FROM countries
                ''', conn)

    print(str(countries.shape[0]) + " entities retreived from database")

    # get the information needed for a choropleth
    if table is not None: 
        sql_stm = ""
        if (table == 'us_immigration') or (table == 'chinese_immigration'): 
            sql_stm = 'SELECT country_id, demographic, \"' + choro_var + '\" FROM ' + table + " WHERE demographic = \'all\'"
        elif table == 'pew': 
            sql_stm = 'SELECT AVG(us_econ_power) AS us_econ_power, AVG(china_econ_power) AS china_econ_power, country_id FROM pew GROUP BY country_id' 
        df = pd.read_sql(sql_stm, conn)
        print(df.head())
        if aggregate == 'sum': 
            df = df.groupby('country_id')[choro_var].sum()
        elif aggregate == 'mean': 
            df = df.groupby('country_id')[choro_var].mean()
        else: 
            # join from data to country data 
            countries = countries.merge(df, on='country_id', how='left')
    
    countries = turn_geo(countries)
    
    conn.close() 

    return countries

def get_public_opinion(country_id): 

    conn = get_db_connection_to_df()

    regions = pd.read_sql(
                ''' SELECT r.geometry, r.shape_name, AVG(us_econ_power) AS us_econ_power, AVG(china_econ_power) AS china_econ_power
                FROM adm as r INNER JOIN pew ON (r.shape_name = pew.adm1) AND (r.country_id = pew.country_id)
                WHERE r.country_id = \'''' + str(country_id) + "\' GROUP BY r.geometry, r.shape_name;", conn)

    regions = turn_geo(regions)

    conn.close() 

    return regions
    

'''
Collects all data regarding to one country. 
This includes all possible aggregated metrics that could be displayed on the global choropleth. 
Input: country_id to use in aggregating sources 
Return: GeoDataFrame containing 1 record for a country with aggregated attributes 
    across datasets pertaining to this country.
'''
def get_country(country_id): 

    conn = get_db_connection_to_df()
    countries = pd.read_sql(
                ''' SELECT country_id, country, geometry, ldc, 
                landlocked_dc, sids, bri_partner FROM countries WHERE country_id = \'''' + str(country_id) + "\';", conn)
    # if countries.shape[0] == 1: 
    #     print("entity retreieved from database")
    # else: 
    #     raise Exception("only one country should have been returned")
    countries = turn_geo(countries)
    conn.close() 

    return countries

'''
Determines the max time range of data available for a particular country 
Input: country_id
Return: a start date and end date for this country denoting the time range of data available 
'''
def get_country_timeline(country_id): 

    conn = get_db_connection_to_df()

    p = pd.read_sql(''' SELECT min(survey_year), max(survey_year) FROM pew
    WHERE country_id = \'''' + str(country_id) + "\';", conn)
    invest = pd.read_sql(''' SELECT min(commitment_year) as minc, max(commitment_year) as maxc, min(completion_year), max(completion_year) 
    FROM investments WHERE country_id = \'''' + str(country_id) + "\';", conn)
    insti = pd.read_sql(''' SELECT EXTRACT(year from min(date_est)) as min, EXTRACT(year from max(date_est)) as max FROM institutes
    WHERE country_id = \'''' + str(country_id) + "\';", conn)

    # select the min/max total values 
    minn = min([p['min'][0], invest['minc'][0], invest['min'][0], insti['min'][0]])
    maxx = max([p['max'][0], invest['maxc'][0], invest['max'][0], insti['max'][0]])
    print("HERE IS THE MIN, MAX", minn, maxx)

    conn.close()
    return int(minn), int(maxx)

'''
Load Confucius Institutes data as merged with cities data to get location elements.
Data is stored as coordinates and does not need to be converted to geometry's before plotting. 
Input: country_id to get institutes within
Return: CI dataframe
'''
def get_institutes_data(country_id, start_time, end_time): 

    conn = get_db_connection_to_df()
    df = pd.read_sql(
        '''
        SELECT institutes.date_est, institutes.confucius_institute, 
        institutes.partner_uni, institutes.status, institutes.ci_webpage,
        cities.latitude, cities.longitude FROM institutes, cities
        WHERE cities.country_id = \'''' + str(country_id) + '''\'
        AND institutes.country_id = \'''' + str(country_id) + '''\'
        AND cities.id = institutes.gl3_id AND CAST(date_est AS DATE) >= \'''' + str(start_time) + '''-01-01\' 
        AND CAST(date_est AS DATE) <= \'''' + str(end_time) + '''-12-31\';
        ''', conn) 

    if df.shape[0] > 0: 
        print(str(df.shape[0]) + " institutes retreived from database")
    else: 
        raise Exception()

    conn.close() 

    return df 

'''
Load Immigration Data 
Input: country_id to get institutes within
Return: Immigration dataframe
'''
def get_immigration_data(country_id, table): 

    conn = get_db_connection_to_df()
    df = pd.read_sql(
        '''
        SELECT * FROM ''' + table + '''
        WHERE country_id = \'''' + str(country_id) + '''\'
        ''', conn) 

    print(df)
    if df.shape[0] == 0: 
        print("No immigration data retreived from database")
        return None

    conn.close() 

    return df 

'''
Load Country Financial Expenditure Data 
Input: country_id to get institutes within, 
       level to express which (city/region/country) level the data has been stored at
Return: Immigration dataframe
'''
def get_expend_data(country_id, level, start_time, end_time): 

    conn = get_db_connection_to_df()
    # build SQL statement 
    innersql = {
    'city' : '''INNER JOIN cities 
                    ON (cities.id = I.gl3_id) AND (cities.country_id = I.country_id)
                ''', 
    'region' : '''INNER JOIN regions 
                    ON (regions.id = I.gl2_id) AND (regions.country_id = I.country_id) AND (I.gl3_id is NULL)
                ''', 
    'country' : '''INNER JOIN countries
                    ON (cities.country_id = I.country_id) AND (I.gl3_id is NULL) AND (I.gl2_id is NULL)
                ''', 
    'all' : ""
    }

    sql = 'SELECT * FROM investments AS I ' + innersql[level] + 'WHERE I.country_id = \'' +  str(country_id) + '''\'
    AND commitment_year >= ''' + str(start_time) + ''' AND completion_year <= ''' + str(end_time)
    df = pd.read_sql(sql, conn) 
    print(str(len(df)), level, "records collected")

    conn.close() 

    if level == 'region' or level == 'country': 
        df = turn_geo(df)

    return df.reset_index()

'''
Convert Polygon or Multipolygon objects back to their geometry. Point data 
has all been stored as coordinates, and needs to be converted seperately. 
Input: dataframe needed to be converted to have Multipolygon/Polygon geometries. 
Return: GeoDataFrame
'''
def turn_geo(df): 

    # convert shapes back to polygons
    df['geometry'] = [shapely.wkt.loads(x) for x in df['geometry']]
    # add into GeoDataFrame 
    df = gpd.GeoDataFrame(df).reset_index(drop=True)
    df.crs = "epsg:4326"

    return df