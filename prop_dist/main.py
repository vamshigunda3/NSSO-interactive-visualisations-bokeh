import pandas as pd
import numpy as np
from bokeh.io import output_notebook, show, output_file, save
from bokeh.plotting import figure
from bokeh.models import Legend,Panel,FactorRange,CheckboxButtonGroup,CustomJS,CheckboxGroup,LabelSet,RadioGroup, ColumnDataSource, Button, HoverTool,Div, Select, RadioButtonGroup
from bokeh.palettes import brewer, Set1,Turbo256, Dark2
from bokeh.io.doc import curdoc
from bokeh.layouts import widgetbox, row, column
from bokeh.models.widgets import Select
from bokeh.transform import factor_cmap
from . import d_files
from os.path import dirname, join

fv = d_files.all_data["data"]

def data_filter(data,Gender,inst_type,caste, clas, place):
    x = data[data["gender"].isin(Gender) &data["inst_type"].isin(inst_type) & data["social_group"].isin(caste) & data["clas"].isin(clas) & data["place"].isin(place)]
    total = x.groupby(["basic_course"],observed = True).agg({"weight":"sum"}).rename(columns = {"weight":"t_weight"}).reset_index()
    ft = x.groupby(["basic_course","inst_dist"], observed = True).agg({"weight":"sum"}).reset_index()
    merge = ft.merge(total, on = ["basic_course"])
    if len(merge) == 0:
        merge = data.groupby(["basic_course","inst_dist"]).size().to_frame("numbers").reset_index()
        merge["percentage"] = 0
    else:
        merge["percentage"] = round((merge.weight/merge.t_weight*100),2)
    merge = merge[["inst_dist","basic_course","percentage"]]
    merge = merge.sort_values(["basic_course","inst_dist"], ascending = [False,True])
    merge = merge.set_index(["basic_course","inst_dist"])
    return merge

def grouped_bar_color(df,y_val,title):
    """This plot will take 3 parameters, dataframe with multiindex index, name of the y-axis column and title.
    it will return a grouped bar graph"""
    df = df[[y_val]]
    x = df.index
    source = ColumnDataSource(data = dict(x = x,y_val = df[y_val]))
    color = df.reset_index()
    wid = list(color.iloc[:,0].unique())
    l = list(color.iloc[:,-2].unique())
    if len(wid) == 1:
        width = 600
    else:
        width = len(l)*len(wid)*85
        width = 800
    p = figure(x_range=FactorRange(*x),y_range = (0,80), plot_height=500, plot_width = width,title=title,
               toolbar_location="right",tools = "pan,wheel_zoom,box_zoom,save,reset")
    p.vbar(x= 'x', top="y_val", width=0.8, source=source, line_color="black",
           fill_color=factor_cmap('x', palette=Dark2[len(l)], factors=l, start=1, end=2),hover_line_color = "darkgrey")
    p.add_tools(HoverTool(tooltips = [(y_val,"@y_val")]))
    p.y_range.start = 0
    p.x_range.range_padding = 0.1
    p.xaxis.major_label_orientation = 1
    p.xgrid.grid_line_color = None
    return p 

gen = list(fv.gender.unique())
caste = list(fv.social_group.unique())
clas = ['Very High','High', 'Middle','Low', 'Very Low']
sector = ["rural","urban"]
inst = list(fv.inst_type.unique())
inst_type = ['Govt', 'Pvt_unaided', 'Pvt_aided', 'Not_known']

x = data_filter(fv,["male","female"],inst,['Others', 'OBC', 'ST', 'SC'],['Middle', 'Low', 'Very Low','High','Very High'],["rural","urban"])
data_source = ColumnDataSource(x)
p = grouped_bar_color(x,"percentage","Percentage of students enrolled in basic course according to distance")


pl = Div(text = """<u>Choose the sector below<u>""")
sctr = CheckboxGroup(labels=["Rural","Urban"], active=[0, 1])

institution = Div(text = """<u/> Please choose type of institution""")
it =  CheckboxGroup(labels= inst_type, active=[0,1,2,3])

gender = Div(text = """<u>Choose the gender below<u>""")
gend = CheckboxGroup(labels=["Female","Male"], active=[0, 1])

sog = Div(text = """<u>Choose the social group below<u>""")
cst = CheckboxGroup(labels=caste, active=[0,1,2,3])

inc = Div(text = """<u>Choose the class group below<u>""")
cls = CheckboxGroup(labels=clas, active=[0,1,2,3,4])

button_state = Button(label="Download data", button_type="success",  width = 150)


def update_data(attrname, old, new):
    sctor = []
    gr = []
    sg = []
    claas = []
    new_it = []
    for i in sctr.active:
        sctor.append(sector[i])
    for i in gend.active:
        gr.append(gen[i])
    for i in cst.active:
        sg.append(caste[i])
    for i in cls.active:
        claas.append(clas[i])
    for i in it.active:
        new_it.append(inst[i])
    df = data_filter(fv,gr,new_it,sg,claas,sctor)
    data_source = ColumnDataSource(df)
    p = grouped_bar_color(df,"percentage","Percentage of students enrolled in basic course according to distance")
    inputs.children[0] = p


def state_handler(event):
    button_state.button_type = "danger"
    
button_state.on_click(state_handler)
button_state.js_on_click(CustomJS(args=dict(source=data_source),
                            code=open(join(dirname(__file__),"download.js")).read()))



sctr.on_change("active",update_data)
gend.on_change("active",update_data)
cst.on_change("active",update_data)
cls.on_change("active",update_data)
it.on_change("active",update_data)

inputs = column(p)
widgets = column(institution,it,pl,sctr,gender,gend,sog,cst,inc,cls,button_state)
layout = column(row(widgets,inputs))

curdoc().add_root(layout)
curdoc().title = "NSSO Analysis"
