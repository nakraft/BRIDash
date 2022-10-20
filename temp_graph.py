import pandas as pd 
import plotly
import plotly.graph_objects as go
import json

import db

def build_graph(country_id, table): 

    # get data from database 
    df = db.get_immigration_data(country_id, table)
    
    if df is None: 
        return None

    if table == 'us_immigration' or table == 'chinese_immigration':
        layout = go.Layout(
            paper_bgcolor='#555',
            plot_bgcolor='#555', 
            font_color= 'white', 
            margin=dict(l=50,r=30,b=30,t=50),
        )
        fig = go.Figure(layout=layout)

        for demo in ['male', 'female', 'all']:
            val = []
            [val.append(i[1].item()) for i in df[df['demographic']==demo][['2000', '2005', '2010', '2015', '2020']].items()]
            fig.add_trace(
                go.Scatter(
                    x = ['2000', '2005', '2010', '2015', '2020'],
                    y = val,
                    name = demo
                )
            )

        fig.update_layout(legend_title_text = "Demographics")
        fig.update_xaxes(title_text="Year")
        fig.update_yaxes(title_text="Immigration Count")
    else: 
        print('no other graphs established yet')
        return None

    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    # for country in country_list:
    #     args = [False] * len(country_list)
    #     args[i] = True
        
    #     #create a button object for the country we are on
    #     button = dict(label = country,
    #                 method = "update",
    #                 args=[{"visible": args}])
        
    #     #add the button to our list of buttons
    #     buttons.append(button)
        
    #     #i is an iterable used to tell our "args" list which value to set to True
    #     i+=1
        
    # fig3.update_layout(updatemenus=[dict(active=0,
    #                                     type="dropdown",
    #                                     buttons=buttons,
    #                                     x = 0,
    #                                     y = 1.1,
    #                                     xanchor = 'left',
    #                                     yanchor = 'bottom'),
    #                             ])

    # map graph dynamic, if several years of graph highlighted, print these years 

    # return the graph for use in sidebar of country level. 