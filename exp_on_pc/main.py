
import time
start = time.process_time()
print("started",start)
import pandas as pd
import geopandas as gpd
import json
from . import d_files
from bokeh.io import show, save
from bokeh.plotting import figure
from bokeh.models import CheckboxGroup,CustomJS,CheckboxButtonGroup, Button,RadioButtonGroup,Div, Label, Slider, GeoJSONDataSource,ColumnDataSource,LinearColorMapper, ColorBar, HoverTool, Select
from bokeh.palettes import brewer
from bokeh.io.doc import curdoc
from bokeh.layouts import widgetbox, row, column
from os.path import dirname, join

loaded_packages = time.process_time()
print("loaded packages",time.process_time()-start)
Final, s_shp, d_shp, states_n, district_n = d_files.all_data["data"]
print("loaded files ",time.process_time()-loaded_packages)


def state_df(data,shp, states_names,Gender, edu_lev,caste, clas, place, inst):
    x = data[data["gender"].isin(Gender) & data["edu_lev_gen"].isin(edu_lev) & data["social_group"].isin(caste) & data["clas"].isin(clas) &data["place"].isin(place) &data["inst_type"].isin(inst)].groupby(["state_code"]).agg({"pvt_coaching":"sum","total_expd":"sum"}).reset_index()
    x["prop"] = round((x.pvt_coaching/x.total_expd * 100),2)
    w = x.merge(states_names, on = ["state_code"])
    if(len(x.index)<1):
        x=pd.DataFrame(columns=["state_code","prop"])
    x = s_shp.merge(x, on = ["state_code"],how = "left")
    x = x[["state_code","state_name","geometry","prop"]]
    return x, w


def dist_df(data,shp,st,district_names,Gender, edu_lev,caste, clas, place, inst):
    x = data[(data['state_code'] == st) & data["gender"].isin(Gender) & data["edu_lev_gen"].isin(edu_lev) & data["social_group"].isin(caste) & data["clas"].isin(clas) &data["place"].isin(place) &data["inst_type"].isin(inst)].groupby(["district_code"]).agg({"pvt_coaching":"sum","total_expd":"sum"}).reset_index()
    x["prop"] = round((x.pvt_coaching/x.total_expd * 100),2)
    dn = district_names[district_names.state_code == st]
    w = x.merge(dn, on = ["district_code"])
    if(len(x.index)<1):
        x=pd.DataFrame(columns=["district_code","prop"])
    dis_shp = shp[shp.state_code == st]
    x = dis_shp.merge(x, on = ["district_code"],how = "left")
    x = x[["district_name","geometry","prop"]]
    return x, w


gen = list(Final.gender.unique())
caste = list(Final.social_group.unique())
clas = ['Very High','High', 'Middle','Low', 'Very Low']
sector = list(Final.place.unique())
inst = list(Final.inst_type.unique())
edu_lev = ['school','higher_sec','higher_edu','others']

## Map
palette = brewer['YlGnBu'][4][::-1]

color_mapper = LinearColorMapper(palette = palette, low = 0, high = 50)
colormapper1 = LinearColorMapper(palette = palette, low = 0, high = 50)

color_bar_S = ColorBar(color_mapper=color_mapper, label_standoff=8,width = 350, height = 20,border_line_color=None,location = (0,0), orientation = 'horizontal')


color_bar_D = ColorBar(color_mapper=colormapper1, label_standoff=8,width = 350, height = 20,border_line_color=None,location = (0,0), orientation = 'horizontal')

Dist, dist_c = dist_df(Final,d_shp,5,district_n,gen,["school"],caste,clas,sector,["government"])
dist_source = ColumnDataSource(dist_c)
District = GeoJSONDataSource(geojson = Dist.to_json())
state,state_c =state_df(Final,s_shp,states_n,gen,["school"],caste,clas,sector,["government"])
state_source = ColumnDataSource(state_c)
State = GeoJSONDataSource(geojson = state.to_json())
TOOLS = "pan,wheel_zoom,box_zoom,reset,save"
p = figure(title = 'Percentage of Expenditure on Private Coaching', plot_height = 500 , plot_width = 400, tools = TOOLS+",tap")
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None
states = p.patches('xs','ys', source = State, fill_color = {'field' :"prop", 'transform' : color_mapper},
          line_color = 'black', line_width = 0.25, fill_alpha = 1)

Dg = figure(title = 'District wise of Uttarakhand', plot_height = 500 , plot_width = 400, tools = TOOLS)
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None
Districts = Dg.patches('xs','ys', source = District, fill_color = {'field' :"prop", 'transform' : colormapper1},
          line_color = 'black', line_width = 0.25, fill_alpha = 1)
p.add_tools(HoverTool(renderers = [states],
                       tooltips = [('State_Name','@state_name'),
                                   ('Percentage',"@prop")]))
Dg.add_tools(HoverTool(renderers = [Districts],
                       tooltips = [('District_Name','@district_name'),
                                   ('Percentage',"@prop")]))
Dg.xgrid.grid_line_color = None
Dg.ygrid.grid_line_color = None

p.add_layout(color_bar_S, 'below')
Dg.add_layout(color_bar_D, 'below')
p.yaxis.visible = False
p.xaxis.visible = False
Dg.yaxis.visible = False
Dg.xaxis.visible = False



ty = Div(text = """<u>Choose type of institution below <u>""")
type_l = CheckboxButtonGroup(labels=['Govt','Pvt Aided','Pvt Unaided','Not Known'],active=[0])

El = Div(text = """<u>Choose the Education level below<u>""")
scl_lvl = CheckboxGroup(labels=["School","Higher_Sec","Higher_Edu","Others"], active=[0])

pl = Div(text = """<u>Choose the sector below<u>""")
sctr = CheckboxButtonGroup(labels=["Rural","Urban"], active=[0, 1],background = "black")

gender = Div(text = """<u>Choose the Gender below<u>""")
gend = CheckboxButtonGroup(labels=["Female","Male","Transgender"], active=[0, 1,2])

sog = Div(text = """<u>Choose the Social group below<u>""")
cst = CheckboxGroup(labels=["Others","OBC","ST","SC"], active=[0,1,2,3])

inc = Div(text = """<u>Choose the class group below<u>""")
cls = CheckboxGroup(labels=clas, active=[0,1,2,3,4])
button_district = Button(label="Download district data", button_type="success", width = 150)
button_state = Button(label="Download state data", button_type="success",  width = 150)

cbar = Select(title="Choose a color here", value="YlGnBu",
              options=["Blues","Greens","Greys","Oranges","BuGn","GnBu","OrRd","RdPu","YlGn","Spectral","YlGnBu","RdYlGn","YlGnBu","YlOrBr","YlOrRd"], width=150)

def update_data(attrname, old, new):
    ty_l = []
    sl = []
    sctor = []
    gr = []
    sg = []
    claas = []
    for i in type_l.active:
        ty_l.append(inst[i])
    for i in scl_lvl.active:
        sl.append(edu_lev[i])
    for i in sctr.active:
        sctor.append(sector[i])
    for i in gend.active:
        gr.append(gen[i])
    for i in cst.active:
        sg.append(caste[i])
    for i in cls.active:
        claas.append(clas[i])
    s_d,state_c = state_df(Final,s_shp,states_n,gr,sl,sg,claas,sctor,ty_l)
    State.geojson = s_d.to_json()
    state_source.data = state_c
    palette = brewer[cbar.value][4][::-1]
    color_mapper.palette = palette
    color_bar_S.color_mapper.palette = palette
    color_bar_D.color_mapper.palette = palette
    states.glyph.fill_color = {'field' :"prop", 'transform' : color_mapper}
    Districts.glyph.fill_color = {'field' :"prop", 'transform' : color_mapper}
    button_state.button_type = "success"
    button_district.button_type = "success"
    
def my_tap_handler(attr,old,new):
    if len(new) != 0:
        ty_l = []
        sl = []
        sctor = []
        gr = []
        sg = []
        claas = []
        for i in type_l.active:
            ty_l.append(inst[i])
        for i in scl_lvl.active:
            sl.append(edu_lev[i])
        for i in sctr.active:
            sctor.append(sector[i])
        for i in gend.active:
            gr.append(gen[i])
        for i in cst.active:
            sg.append(caste[i])
        for i in cls.active:
            claas.append(clas[i])
        sc = state["state_code"] [new[0]]
        sn = state["state_name"] [new[0]]
        d_d,dist_c = dist_df(Final,d_shp,sc,district_n,gr,sl,sg,claas,sctor,ty_l)
        District.geojson = d_d.to_json()
        dist_source.data = dist_c
        Dg.title.text = "District wise of "+str(sn.capitalize())
        button_district.button_type = "success"
        
def state_handler(event):
    button_state.button_type = "danger"

def district_handler(event):
    button_district.button_type = "danger"

button_district.on_click(district_handler)
button_state.on_click(state_handler)

button_district.js_on_click(CustomJS(args=dict(source=dist_source),
                            code=open(join(dirname(__file__),"download.js")).read()))
button_state.js_on_click(CustomJS(args=dict(source=state_source),
                            code=open(join(dirname(__file__),"download.js")).read()))


scl_lvl.on_change("active",update_data)
sctr.on_change("active",update_data)
gend.on_change("active",update_data)
cst.on_change("active",update_data)
cls.on_change("active",update_data)
type_l.on_change("active",update_data)
State.selected.on_change("indices",my_tap_handler)
cbar.on_change("value",update_data)

plot = row(p,Dg,column(cbar,button_state,button_district))
widgets = column(ty,type_l,El,scl_lvl,pl,sctr,gender,gend,sog,cst,inc,cls)
layout = column(row(widgets,plot))

curdoc().add_root(layout)

print("end ",time.process_time()-start)
