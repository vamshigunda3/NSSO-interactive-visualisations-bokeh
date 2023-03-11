import pandas as pd
import pandas as pd
import numpy as np
from bokeh.io import output_notebook, show, output_file, save
from bokeh.plotting import figure
from bokeh.models import Legend,Panel,FactorRange,CheckboxButtonGroup,CheckboxGroup, CustomJS,LabelSet,RadioGroup, ColumnDataSource, Button, HoverTool,Div, Select, RadioButtonGroup
from bokeh.palettes import brewer, Set1,Turbo256
from bokeh.io.doc import curdoc
from bokeh.layouts import widgetbox, row, column
from bokeh.models.widgets import Select
from bokeh.transform import factor_cmap
from . import d_files
from os.path import dirname, join

iv = d_files.all_data["data"]
iv = iv[~iv.basic_course.isin(["not literate"])]

def data_filter(data,Gender,caste, clas, place):
    x = data[data["gender"].isin(Gender) & data["social_group"].isin(caste) & data["clas"].isin(clas) & data["place"].isin(place)]
    print("length of filtered data: ",len(x))
    total = x.groupby(["inst_type","basic_course"],observed = True).agg({"weight":"sum"}).rename(columns = {"weight":"t_weight"}).reset_index()
    ft = x.groupby(["inst_type",'pvt_coaching',"basic_course"],observed = True).agg({"weight":"sum"}).reset_index()
    merge = ft.merge(total, on = ["inst_type","basic_course"])
    if len(merge) == 0:
        merge = data.groupby(["inst_type","basic_course"], observed = True).size().to_frame("numbers").reset_index()
        merge["percentage"] = 0
    else:
        merge["percentage"] = round((merge.weight/merge.t_weight*100),2)
        merge = merge.query('pvt_coaching == "yes"')
        #merge = merge[merge["pvt_coaching"] == "yes"]
    merge = merge[["inst_type","basic_course","percentage"]]
    merge = merge.sort_values(["inst_type","basic_course"],ascending = [True,False])
    merge = merge.set_index(["inst_type","basic_course"])      
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
    p = figure(x_range=FactorRange(*x),y_range = (0,60), plot_height=500, plot_width = width,title=title,
               toolbar_location="right",tools = "pan,wheel_zoom,box_zoom,reset,save")
    p.vbar(x= 'x', top="y_val", width=0.8, source=source, line_color="white",
           fill_color=factor_cmap('x', palette=Set1[len(l)], factors=l, start=1, end=2),hover_line_color = "darkgrey")
    p.add_tools(HoverTool(tooltips = [(y_val,"@y_val")]))
    p.x_range.range_padding = 0.1
    p.xaxis.major_label_orientation = 1
    p.xgrid.grid_line_color = None
    return p 


# In[7]:


x = data_filter(iv,["male","female"],['Others', 'OBC', 'ST', 'SC'],['Middle', 'Low', 'Very Low','High','Very High'],["rural","urban"])
data_source = ColumnDataSource(x)
p = grouped_bar_color(x,"percentage","Percentage of people opting for private coaching")


gen = list(iv.gender.unique())
caste = list(iv.social_group.unique())
clas = ['Very High','High', 'Middle','Low', 'Very Low']
sector = ["rural","urban"]


pl = Div(text = """<u>Choose the sector below<u>""")
sctr = CheckboxGroup(labels=["Rural","Urban"], active=[0, 1])

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
    for i in sctr.active:
        sctor.append(sector[i])
    for i in gend.active:
        gr.append(gen[i])
    for i in cst.active:
        sg.append(caste[i])
    for i in cls.active:
        claas.append(clas[i])
    df = data_filter(iv,gr,sg,claas,sctor)
    data_source.data = df
    p = grouped_bar_color(df,"percentage","percentage of people opting for private coaching")
    inputs.children[0] = p
    button_state.button_type = "success"

def state_handler(event):
    button_state.button_type = "danger"
    
button_state.on_click(state_handler)
button_state.js_on_click(CustomJS(args=dict(source=data_source),
                            code=open(join(dirname(__file__),"download.js")).read()))



sctr.on_change("active",update_data)
gend.on_change("active",update_data)
cst.on_change("active",update_data)
cls.on_change("active",update_data)

inputs = column(p)
widgets = column(pl,sctr,gender,gend,sog,cst,inc,cls,button_state)
layout = column(row(widgets,inputs))

curdoc().add_root(layout)
