import json
from tracemalloc import start
from venv import create

from flask import Flask, render_template, request, Markup, jsonify, url_for
import shapely
from shapely.geometry import Point

import choro
import country as c_maps
import db

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def world_comparison():

    # this varible will be aggregated to use in choropleth construction 
    choro_var = None 

    if request.method == 'POST' : 
        table = request.form.get('table')
        choro_var = request.form.get('choro_var')
    else: 
        # these will be the default records on the table 
        choro_var = "2000"
        table = 'chinese_immigration'

    print("Changing choropleth view to: ")
    print("Table:", table, ", Variable:", choro_var)

    # geodataframe returned of world data aggregated by country
    df = db.get_world_data(table, choro_var, False)
    labels = {
        'pew' : [2017, 2018, 2019, 2020, 2021],
        'chinese_immigration' : [2000, 2005, 2010, 2015, 2020], 
        'us_immigration' : [2000, 2005, 2010, 2015, 2020]
    }
    map_div, hdr_txt, script_txt = choro.build_choropleth(df, choro_var, 'world')

    return render_template('world.html', map_div=map_div, hdr_txt=hdr_txt, script_txt=script_txt, data={'table':table, 'choro_var':choro_var, 'timeline': labels[table]}, country_details={'country_id': 'None', 'religion' : 'None'}) #known bug here, page reloads after map updated causing dropdowns to be reset

@app.route('/aboutus')
def about_us():
    return render_template('about_us.html')

@app.route('/find_country', methods=['GET', 'POST'])
def find_country(): 

    lat = None
    long = None
    results = None

    print("location change request ")
    df = db.get_world_data(None, None, None)
    if request.json['type'] == 'point':
        lat = request.json['lat']
        long = request.json['long']

        clicked = Point(float(long), float(lat))
        country = df[df['geometry'].contains(clicked)].reset_index()['country'][0]
    elif request.json['type'] == 'name':
        country = df[df['country'] == request.json['name']].reset_index()['country'][0]
    else: 
        raise Exception

    country_id = df.loc[df['country'] == country, 'country_id'].item()
    print("name: " + str(country) + " | id: " + str(country_id))

    results = {'country': str(country), 'country_id': str(country_id)}

    print(jsonify(results) )

    return jsonify(results)    

# @app.route('/data/<country>', methods=['GET', 'POST'])
# def data(country): 
#     if request.method == 'POST': 
#         return get_country_page(country, None, {'start':request.json['start'], 'end':request.json['end']}) 
#     else: 
#         return get_country_page(country, None, None) 

# @app.route('/filter_country', methods=['GET', 'POST'])
# def filter_country():
#     try:
#         return get_country_page(str(request.form.get('country')), ['lskdjf', 'skljdf'], {'start':request.json['start'], 'end':request.json['end']}) 
#     except: 
#         return get_country_page(str(request.form.get('country')), ['lskdjf', 'skljdf'], None) 

@app.route('/data/<country>', methods=['GET', 'POST'])
def get_country_page(country): 
    
    print("More details requested for country #" + country)
    min_range, max_range = db.get_country_timeline(country)

    # geodataframe returned of world data aggregated by country
    df = db.get_country(country)
    if request.method == 'POST': 

        start_range, end_range = request.json['start'], request.json['end']
        if request.json['status'] == 'query': 
            details = {'keyword_search': request.json['keyword_search'], 'expenditure_type': request.json['expenditure_type'], 'donor_name' : request.json['donor_name'], 'ci_status' : request.json['ci_status'], 'wealthy' : request.json['wealthy'], 'religion' : request.json['religion'] }
            print(details)
        else: 
            details = None

        print("New date range selected", start_range, end_range)

    else : 
        start_range, end_range = min_range, max_range
        details = None

    # map will contain inner country details (confucious institutes, expenditures, regional data)
    map_det = c_maps.build_layers(df, [start_range, end_range], details)
    map_div, hdr_txt, script_txt = map_det[0], map_det[1], map_det[2]

    graphJSON = c_maps.build_graphs(df['country_id'].item(), 'expend', [2000, 2024])
    if graphJSON == None: 
        print("No data recieved for expenditures. Plot a different value.") 

    expend_titles = c_maps.get_finance_country(country, [start_range, end_range])
    # details needed for sidebar to display data chart 
    country_details = dict(df.iloc[0][['country_id', 'country', 'bri_partner', 'ldc', 'landlocked_dc']])
    print(country_details)
    country_details.update({'religion': c_maps.get_religion_details(country)})

    print(country_details)
    return render_template('country.html', map_div=map_div, hdr_txt=hdr_txt, script_txt=script_txt, country_details=country_details,
     graphJSON=graphJSON, expend_titles=expend_titles, timeline= list(range(min_range, max_range + 1)), timeline_start = [start_range, end_range])


@app.route('/load_graph', methods=['GET', 'POST'])
def load_graph(): 
    
    graphic = request.json['graph']
    country = request.json['country']
    graphJSON = c_maps.build_graphs(country, graphic, [2000, 2024])
    if graphJSON == None: 
        print("No data recieved for this graph type. Plot a different value.") 

    return graphJSON

@app.route('/change_choro', methods=['GET', 'POST'])
def change_choro(): 
    
    print(request.args.get('table'))
    print(request.args.get('choro_var'))
    table = request.args.get('table')
    choro_var = request.args.get('choro_var')

    df = db.get_world_data(table, choro_var, False)
    map_div, hdr_txt, script_txt = choro.build_choropleth(df, choro_var, 'world')
    print("building choropleth")

    return jsonify({'map_div':map_div, 'hdr_txt':hdr_txt, 'script_txt': script_txt, 'text':'text'}) # put this into a json and return one obejct

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=3000, debug=True)