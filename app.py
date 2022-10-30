import json
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
    map_div, hdr_txt, script_txt = choro.build_choropleth(df, choro_var)

    return render_template('world.html', map_div=map_div, hdr_txt=hdr_txt, script_txt=script_txt, data={'table':table, 'choro_var':choro_var}) #known bug here, page reloads after map updated causing dropdowns to be reset

@app.route('/aboutus')
def about_us():
    return render_template('about_us.html')

@app.route('/find_country', methods=['GET', 'POST'])
def find_country(): 

    lat = None
    long = None
    results = None

    # TODO: is this if statement needed? 
    # if request.method == 'POST': 
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

@app.route('/data/<country>', methods=['GET', 'POST'])
def data(country): 

    print("More details requested for country #" + country)

    # geodataframe returned of world data aggregated by country
    df = db.get_country(country)
    # map will contain inner country details (confucious institutes, expenditures, regional data)
    map_div, hdr_txt, script_txt = c_maps.build_layers(df)

    graphJSON = c_maps.build_graphs(df['country_id'].item(), 'expend')
    if graphJSON == None: 
        print("No data recieved for expenditures. Plot a different value.") 

    expend_titles = c_maps.get_finance_country(country)

    # details needed for sidebar to display data chart 
    country_details = df.iloc[0][['country_id', 'country', 'bri_partner', 'ldc', 'landlocked_dc']]

    return render_template('country.html', map_div=map_div, hdr_txt=hdr_txt, script_txt=script_txt, country_details=country_details, graphJSON=graphJSON, expend_titles=expend_titles)

@app.route('/load_graph', methods=['GET', 'POST'])
def load_graph(): 
    
    print(request.args.get('graph'))
    print(request.args.get('country'))
    graphic = request.args.get('graph')
    country = request.args.get('country')
    graphJSON = c_maps.build_graphs(country, graphic)
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
    map_div, hdr_txt, script_txt = choro.build_choropleth(df, choro_var)
    print("building choropleth")

    return jsonify({'map_div':map_div, 'hdr_txt':hdr_txt, 'script_txt': script_txt, 'text':'text'}) # put this into a json and return one obejct

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=3000, debug=True)