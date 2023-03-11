import pandas as pd
import pandas as pd
import numpy as np
from bokeh.io import output_notebook, show, output_file, save
from bokeh.plotting import figure
from bokeh.models import Legend,Panel,FactorRange,CustomJS,CheckboxButtonGroup,CheckboxGroup,LabelSet,RadioGroup, ColumnDataSource, Button, HoverTool,Div, Select, RadioButtonGroup
from bokeh.palettes import brewer, Set1,Turbo256, Dark2
from bokeh.io.doc import curdoc
from bokeh.layouts import widgetbox, row, column
from bokeh.models.widgets import Select
from bokeh.transform import factor_cmap
from . import d_files
from os.path import dirname, join

iv = d_files.all_data["data"]

def group_stack_df(data,cat1,cat2,cat3):
    """Input dataframe and input the categories to be analysed, 
        cat1 is the column value you want to groupby first and cat 2 is second"""
    Total = data.groupby([cat1,cat2], observed  =True).agg({"weight":"sum"}).rename(columns = {"weight":"t_weight"}).reset_index()
    Edu_level= data.groupby([cat1,cat2,cat3], observed  =True).agg({"weight":"sum"}).reset_index()
    Final_edu = Edu_level.merge(Total, on = [cat1,cat2])
    Final_edu["percentage"] = round((Final_edu.weight/Final_edu.t_weight *100),2)
    Final_edu["index"] =Final_edu[cat1].astype(str)+" " +Final_edu[cat2].astype(str)
    Final = Final_edu.pivot(index =  "index", columns = cat3, values = "percentage")
    Final.columns = Final.columns.astype(list)
    Final = Final.reset_index()
    Final.columns.name = None
    Final[[cat1,cat2]] = Final["index"].str.split(" ",expand=True)
    Final = Final.set_index([cat1,cat2])
    Final.drop(columns = "index", inplace = True)
    Final.replace(np.nan, 0, inplace = True)
    return Final

def grouped_bar_stack(data,title):
    bars = list(data.columns)
    x = data.index
    source = ColumnDataSource(data = dict(x = x, english = list(data[bars[0]]),others = list(data[bars[1]]),))
    
    p = figure(x_range=FactorRange(*x), plot_height=500, plot_width = 800,title=title,
               toolbar_location="right",tools = "pan,wheel_zoom,box_zoom,reset,save,hover", tooltips="$name : @$name")
    p.vbar_stack(bars, x='x', width=0.9, alpha=0.8,line_color="white", color=["blue", "green"], source=source,
             legend_label=bars,hover_line_color = "darkgrey")
    p.y_range.start = 0
    p.x_range.range_padding = 0.1
    p.xaxis.major_label_orientation = 1
    p.xgrid.grid_line_color = None
    return p

Categories = ["Social group", "Gender", "Class", "Place"]
oc = ["social_group", "gender", "clas", "place"]
Title = ["Choice of medium of instruction with respect to type of institution and social group","Choice of medium of instruction with respect to type of institution and gender","Choice of medium of instruction with respect to type of institution and class","Choice of medium of instruction with respect to type of institution and place"]

h = group_stack_df(iv,"inst_type",oc[0],'instruction_med')
data_source = ColumnDataSource(h)
p = grouped_bar_stack(h,Title[0])
cath = Div(text = """<u/> Please choose any category for the plot""")
cat = RadioButtonGroup(labels = Categories, active = 0)


button_state = Button(label="Download data", button_type="success",  width = 150)

def update_data(attrname, old, new):
    new_cat = cat.active
    h = group_stack_df(iv,"inst_type",oc[new_cat],'instruction_med')
    data_source.data = h
    p = grouped_bar_stack(h,Title[new_cat])
    inputs.children[0] = p
    button_state.button_type = "success"
    
def state_handler(event):
    button_state.button_type = "danger"
    
button_state.on_click(state_handler)
button_state.js_on_click(CustomJS(args=dict(source=data_source),
                            code=open(join(dirname(__file__),"download.js")).read()))
    
cat.on_change("active",update_data)

inputs = column(p)
widgets = column(cath,cat,button_state)
layout = column(row(widgets,inputs))
curdoc().add_root(layout)
curdoc().title = "NSSO Analysis"
