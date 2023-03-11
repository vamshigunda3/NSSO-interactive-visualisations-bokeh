import pandas as pd
from bokeh.io import output_notebook, show, output_file, save
from bokeh.plotting import figure
from bokeh.models import Legend,Panel,FactorRange,CheckboxButtonGroup,CustomJS,CheckboxGroup,LabelSet,RadioGroup, ColumnDataSource, Button, HoverTool,Div, Select, RadioButtonGroup
from bokeh.palettes import brewer, Set1,Turbo256
from bokeh.io.doc import curdoc
from bokeh.layouts import widgetbox, row, column
from bokeh.models.widgets import Select
from bokeh.transform import factor_cmap
from . import d_files
from os.path import dirname, join

df = d_files.all_data["data"]

def data_filter_bar(data, bc,gen, caste,clas,sector):
    df = data[(data["basic_course"] == bc) & data["gender"].isin(gen) & data["social_group"].isin(caste) & data["clas"].isin(clas) & data["place"].isin(sector)]
    if len(df) == 0:
        final = data.inst_type.value_counts().sort_index(ascending=True).to_frame("numbers").reset_index()
        final["percentage"] = 0
        final = final[["index","percentage"]]
        final.columns = ["inst_type","percentage"]
    else:
        final = df.groupby(["inst_type"],observed = True).agg({"weight":"sum"}).reset_index()
        final["total"] = df.weight.sum()
        final["percentage"] = round(final["weight"]/final["total"]*100,2)
        final = final[["inst_type","percentage"]]
    return final


def data_filter_st_bar(data,st, bc,gen, caste,clas,sector):
    df = data[(data["state_name"] == st) &(data["basic_course"] == bc) & data["gender"].isin(gen) & data["social_group"].isin(caste) & data["clas"].isin(clas) & data["place"].isin(sector)]
    print("length of filtered data: ",len(df))
    if len(df) == 0:
        final = data.inst_type.value_counts().sort_index(ascending=True).to_frame("numbers").reset_index()
        final["percentage"] = 0
        final = final[["index","percentage"]]
        final.columns = ["inst_type","percentage"]
    else:
        final = df.groupby(["inst_type"],observed = True).agg({"weight":"sum"}).reset_index()
        final["total"] = df.weight.sum()
        final["percentage"] = round(final["weight"]/final["total"]*100,2)
        final = final[["inst_type","percentage"]]
    return final


def bar_plot(df,x_val,y_val,title):
    """This plot will take four parameters, 1. dataframe 2.x_axis value 3.y_axis value
        4.title as a string for the plot and returns a barplot with hover tools"""
    x = list(df[x_val])
    l = len(x)
    if l < 3:
        l = 3
    Data = ColumnDataSource(df)
    a = df.columns[0]
    y = df.columns[-1]
    p = figure(x_range= x,y_range = (0,100), plot_height=300,plot_width = 350, title= title,
               toolbar_location = "right",tools = "pan,wheel_zoom,box_zoom,reset,save")
    labels = LabelSet(x=x_val, y=y_val, text=y_val, level='glyph',
        x_offset=-15.5, y_offset= 2, source=Data, render_mode='canvas',text_color = "black")
    p.vbar(x = x_val,top = y_val, width = 0.7,source = Data,
           fill_color=factor_cmap(x_val, palette=Set1[l], factors=x), hover_line_color = "white")
    p.add_tools(HoverTool(tooltips=[(y_val, "@"+y_val)]))
#     #p.add_layout(p.legend[0],'right')
    p.add_layout(labels)
    return p

gen = list(df.gender.unique())
caste = list(df.social_group.unique())
clas = ['Very High','High', 'Middle','Low', 'Very Low']
sector = ["rural","urban"]
#region = ['East', 'West', 'North','South']
edu = ['School','Higher_sec' ,'Higher_edu']
st = sorted(df.state_name.unique())

x = data_filter_bar(df, "School",gen,caste,clas,sector)
nat_source = ColumnDataSource(x)
plot = bar_plot(x,"inst_type","percentage","Percentage of national enrollment")

s_x = data_filter_st_bar(df,st[5], "School",gen,caste,clas,sector)
state_source = ColumnDataSource(s_x)

s_p = bar_plot(s_x,"inst_type","percentage","Percentage of enrollment in "+ str(st[5])+ "")

s2 = data_filter_st_bar(df,st[7],"School",gen,caste,clas,sector)
s_p2 = bar_plot(s2,"inst_type","percentage","Percentage of enrollment in "+ str(st[7])+ "")
    
compare = Div(text = """<h4>Compare percentage of enrollment between States below<h4>""")

s_t =  Div(text = """<u>Choose a State below<u>""")
state = Select(title="State",value=st[5],options=st)
state_2 = Select(title="State",value=st[7],options=st)


ed =  Div(text = """<u>Choose the Education level below<u>""")
Edu = RadioGroup(labels=edu, active=0)

# reg = Div(text = """<u>Choose the region below<u>""")
# regi = CheckboxGroup(labels=region, active=[0,1,2,3])

pl = Div(text = """<u>Choose the sector below<u>""")
sctr = CheckboxGroup(labels=["Rural","Urban"], active=[0, 1])

gender = Div(text = """<u>Choose the gender below<u>""")
gend = CheckboxGroup(labels=["Female","Male"], active=[0, 1])

sog = Div(text = """<u>Choose the social group below<u>""")
cst = CheckboxGroup(labels=caste, active=[0,1,2,3])

inc = Div(text = """<u>Choose the class group below<u>""")
cls = CheckboxGroup(labels=clas, active=[0,1,2,3,4])

button_national = Button(label="Download national data", button_type="success",  width = 150)
button_state = Button(label="Download state data", button_type="success",  width = 150)


def update_data(attrname, old, new):
   # regio = []
    sctor = []
    gr = []
    sg = []
    claas = []
    c_state = state.value
    c_2 = state_2.value
    ed_l = edu[Edu.active]
    print("edu",ed_l)
    for i in sctr.active:
        sctor.append(sector[i])
    for i in gend.active:
        gr.append(gen[i])
    for i in cst.active:
        sg.append(caste[i])
    for i in cls.active:
        claas.append(clas[i])
#     for i in regi.active:
#         regio.append(region[i])
    data = data_filter_bar(df,ed_l,gr,sg,claas,sctor)
    p = bar_plot(data,"inst_type","percentage","Percentage of national enrollment")
    nat_source.data = data
    
    s_d = data_filter_st_bar(df,c_state,ed_l,gr,sg,claas,sctor)
    s_p = bar_plot(s_d,"inst_type","percentage","Percentage of enrollment in "+ str(c_state)+ "")
    state_source.data = s_d
    
    s_d_2 = data_filter_st_bar(df,c_2,ed_l,gr,sg,claas,sctor)
    s_p_2 = bar_plot(s_d_2,"inst_type","percentage","Percentage of enrollment in "+ str(c_2)+ "")
    
    inputs.children[0] = p
    vs.children[1].children[0].children[0] = s_p
    vs.children[1].children[1].children[0] = s_p_2
    button_state.button_type = "success"
    button_national.button_type = "success"

def state_handler(event):
    button_state.button_type = "danger"

def national_handler(event):
    button_national.button_type = "danger"

button_national.on_click(national_handler)
button_state.on_click(state_handler)

button_national.js_on_click(CustomJS(args=dict(source=nat_source),
                            code=open(join(dirname(__file__),"download.js")).read()))
button_state.js_on_click(CustomJS(args=dict(source=state_source),
                            code=open(join(dirname(__file__),"download.js")).read()))





Edu.on_change("active",update_data)
sctr.on_change("active",update_data)
gend.on_change("active",update_data)
cst.on_change("active",update_data)
cls.on_change("active",update_data)
#regi.on_change("active",update_data)
state.on_change("value",update_data)
state_2.on_change("value",update_data)

vs = column(compare,row(column(s_p,s_t,state,button_state), column(s_p2,s_t,state_2)))
inputs = column(plot,vs)
widgets = column(ed,Edu,pl,sctr,gender,gend,sog,cst,inc,cls,button_national)
layout = column(row(widgets,inputs))

curdoc().add_root(layout)
