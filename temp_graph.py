import pandas as pd 
import plotly
import plotly.graph_objects as go
import json

import db

def build_graph(country_id, table, timerange): 

    layout = go.Layout(
        paper_bgcolor='#555',
        plot_bgcolor='#555', 
        font_color= 'white', 
        margin=dict(l=50,r=30,b=30,t=50),
    )
    fig = go.Figure(layout=layout)

    # graph immigration records
    if table == 'us_immigration' or table == 'chinese_immigration':

        df = db.get_immigration_data(country_id, table)
        if df is None: 
            return None

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
    
    elif table == 'expend': 

        print("Getting expenditure data")
        df = db.get_expend_data(country_id, 'all', timerange[0], timerange[1])
        df['color'] = df['sector_name'].map( {'EDUCATION' : '#AF1D1D', 
                            'TRANSPORT AND STORAGE' : '#FBD61D', 
                            'ENERGY' : '#1E9912', 
                            'COMMUNCIATIONS' : '#0356C6', 
                            'COMMUNICATIONS' : '#0356C6', 
                            'INDUSTRY, MINING AND CONSTRUCTION' : '#8519B0', 
                            'HEALTH' : '#DE769A'
                        })
        df['color'] = ["#F50404" if pd.isna(x) else x for x in df['color']]

        amounts = df.groupby(['completion_year', 'sector_name', 'color'])['amount_constant2017'].sum().reset_index()
        if len(amounts) == 0: 
            return None

        for x in amounts['sector_name'].unique():
            fig.add_trace(
                go.Bar(
                    x = amounts[amounts['sector_name'] == x]['completion_year'],
                    y = amounts[amounts['sector_name'] == x]['amount_constant2017'], 
                    name = x, 
                    marker=dict(color = amounts[amounts['sector_name'] == x]['color'])
                 )
            )

        fig.update_layout(
            barmode="stack", xaxis_title="Year", yaxis_title="Total Expenditures"
        )
    
    else: 
        print('no other graphs established yet')
        return None

    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
