import pandas as pd
import numpy as np
from bokeh.io import output_notebook, show, output_file, save
from bokeh.plotting import figure
from bokeh.models import Legend,Panel,FactorRange,LabelSet,RadioGroup, ColumnDataSource,CustomJS, Button, HoverTool,Div, Select, RadioButtonGroup
from bokeh.palettes import brewer, Set1
from bokeh.io.doc import curdoc
from bokeh.layouts import widgetbox, row, column
from bokeh.models.widgets import Select
from . import d_files
from os.path import dirname, join


Final = d_files.all_data["data"]
print(Final.head())

def data_converter(df,cat,El):
    df = df[df["Education_Level"].isin(El)]
    if cat == "Class":
        cat = "Expenditure"
    if cat != "Expenditure":
        Total = df.groupby([cat]).agg({"weight":"sum"}).rename(columns = {"weight":"total_weight"}).reset_index()
        Edu_level= df.groupby([cat,"Education_Level"]).agg({"weight":"sum"}).reset_index()
        Final_edu = Edu_level.merge(Total, on = [cat])
        Final_edu["percentage"] = round((Final_edu.weight/Final_edu.total_weight *100),2)
        Final = Final_edu.pivot(index =  cat, columns = "Education_Level", values = "percentage")
        Final.replace(np.nan, 0, inplace = True)
    else:
        index = ["Lower_class","Working_class","Lower_Middle_Class","Upper_Middle_class","Upper_class"]
        Total = df.groupby(pd.qcut(df[cat],q = 5)).agg({"weight":"sum"}).rename(columns = {"weight":"total_weight"}).reset_index()
        Edu_level = df.groupby([pd.qcut(df[cat],q = 5),"Education_Level"]).agg({"weight":"sum"}).reset_index()
        Final_edu = Edu_level.merge(Total, on = [cat])
        Final_edu["percentage"] = round((Final_edu.weight/Final_edu.total_weight *100),2)
        Final = Final_edu.pivot(index =  cat, columns = "Education_Level", values = "percentage")
        Final.replace(np.nan, 0, inplace = True)
        Final.index = index
        Final.index.name = cat
    return Final
    
def plot(df,title):
    """give title as string"""
    stacks = list(df.columns)
   # stacks = stacks[:-1]
    cat = list(df.index)
    x = df.index.name
    Data = ColumnDataSource(df)
    p = figure(x_range = cat, plot_height = 500,width = 900, title = title, toolbar_location = "right", tools = "pan,wheel_zoom,box_zoom,reset,hover,save", tooltips="$name : @$name" )
    p.vbar_stack(stacks, x = x, color = Set1[len(stacks)],width = 0.5, source = Data,legend_label = stacks)
#     df_l = df.iloc[:,-1].to_frame()
#     df_l['y'] = 100
#     df_l.reset_index(inplace = True)
#     Data_l = ColumnDataSource(df_l)
#     labels = LabelSet(x= x, y ='y', text= "total",x_offset=5, y_offset=0, source= Data_l, render_mode='canvas')
    p.y_range.start = 0
    p.x_range.range_padding = 0.05
    p.xgrid.grid_line_color = None
    p.axis.minor_tick_line_color = None
    p.outline_line_color = None
    p.add_layout(p.legend[0],'right')
#     p.add_layout(labels)
    return p

Categories = ["Social group", "Gender","Region", "Class"]
Title_list = ["Caste wise participation in higher education","Gender wise participation in higher education","Region wise participation in higher education","Class_wise participation in higher education"]

Tech = ['Technical_Diploma(<graduate)', 'Eng_Degree','Technical_Diploma(>=graduate)', 'Agr_Degree', 'Med_Degree',]
Both =['Degree/PG','Technical_Diploma(<graduate)', 'Eng_Degree','Technical_Diploma(>=graduate)', 'Agr_Degree', 'Med_Degree']
Edu_level = [Tech,Both]
RG = ["Technical","Both(General & Technical)"]
x = data_converter(Final,Categories[3],Edu_level[0])
data_source = ColumnDataSource(x)

p = plot(x,Title_list[3])

SG = RadioButtonGroup(labels = Categories, active = 3)
#div_mh = Div(text = """<h3/> The below visualisation provides information on the percentage of participation in technical and professional higher education with respect to social group, gender and region. <h3/> """)
E_level = RadioGroup(labels=RG, active=0)
E_l = Div(text = """<u/> Please select type of education below""")
E_C = Div(text = """<u/> Please choose any category for the plot""")

button_state = Button(label="Download data", button_type="success",  width = 150)

def update_data(attrname, old, new):
    CV = SG.active
    R = E_level.active
    cd = data_converter(Final,Categories[CV],Edu_level[R])
    data_source.data = cd
    c = Title_list[CV]
    ch = plot(cd,c)
    inputs.children[0] = ch
    button_state.button_type = "success"
    
def state_handler(event):
    button_state.button_type = "danger"
    
button_state.on_click(state_handler)
button_state.js_on_click(CustomJS(args=dict(source=data_source),
                            code=open(join(dirname(__file__),"download.js")).read()))



SG.on_change("active",update_data)
E_level.on_change("active",update_data)

inputs = column(p)
w = column(E_l,E_level,E_C,SG,button_state)
layout = column(row(w,inputs))
curdoc().add_root(layout)
curdoc().title = "NSSO Analysis"
