import time
start = time.process_time()
print("started",start)
import pandas as pd
import geopandas as gpd
import json
from . import d_files
from bokeh.io import show, save
from bokeh.plotting import figure
from bokeh.models import CheckboxGroup,CustomJS,CheckboxButtonGroup, Button,RadioButtonGroup,RadioGroup,Div, Label, Slider, GeoJSONDataSource,ColumnDataSource,LinearColorMapper, ColorBar, HoverTool, Select
from bokeh.palettes import brewer
from bokeh.io.doc import curdoc
from bokeh.layouts import widgetbox, row, column
from os.path import dirname, join


df, s_shp, d_shp, states_n, district_n = d_files.all_data["data"]


def state_filter(data,shp,bc,inst_type,gen, caste,clas,sector):
    t_df = data[(data["basic_course"] == bc)& data["gender"].isin(gen) & data["social_group"].isin(caste) & data["clas"].isin(clas) & data["place"].isin(sector)]
    f_df = t_df[(t_df["inst_type"] == inst_type)]
    total = t_df.groupby(["state_code"],observed = True).agg({"weight":"sum"}).rename(columns = {"weight":"t_weight"}).reset_index()
    st = f_df.groupby(["state_code","inst_type"], observed =True).agg({"weight":"sum"}).reset_index()
    st = st.merge(total,on = ["state_code"])
    st["percentage"] = round(st.weight/st.t_weight *100,2)
    st.drop(columns = ["weight","t_weight","inst_type"], inplace = True)
    if(len(st.index)<1):
        st = pd.DataFrame(columns=["state_code","district_code","percentage"])
    x = st
    st = shp.merge(st, on = ["state_code"],how = "left")
    return st, x

def district_filter(data,shp,bc,inst_type,gen, caste,clas,sector):
    t_df = data[(data["basic_course"] == bc) & data["gender"].isin(gen) & data["social_group"].isin(caste) & data["clas"].isin(clas) & data["place"].isin(sector)]
    f_df = t_df[(t_df["inst_type"] == inst_type)]
    total = t_df.groupby(["state_code","district_code"]).agg({"weight":"sum"}).rename(columns = {"weight":"t_weight"}).reset_index()
    st = f_df.groupby(["state_code","district_code","inst_type"], observed = True).agg({"weight":"sum"}).reset_index()
    st = st.merge(total,on = ["state_code","district_code"])
    st["percentage"] = round(st.weight/st.t_weight *100,2)
    st.drop(columns = ["weight","t_weight","inst_type"], inplace = True)
    if(len(st.index)<1):
        st = pd.DataFrame(columns=["state_code","district_code","percentage"])
    x = st
    st = shp.merge(st, on = ["state_code","district_code"], how = "left")
    return st, x

gen = list(df.gender.unique())
caste = ['SC', 'ST','OBC', 'Others']
clas = ['Very High','High', 'Middle','Low', 'Very Low']
sector = ["rural","urban"]
edu = ['School','Higher_sec' ,'Higher_edu']
inst_type = list(df.inst_type.unique())

palette = brewer['RdYlGn'][4]
palette = palette[::-1]
color_mapper = LinearColorMapper(palette = palette, low = 0, high = 100)
colormapper1 = LinearColorMapper(palette = palette, low = 0, high = 100)

color_bar_S = ColorBar(color_mapper=color_mapper, label_standoff=8,width = 350, height = 20,border_line_color=None,location = (0,0), orientation = 'horizontal')
color_bar_D = ColorBar(color_mapper=colormapper1, label_standoff=8,width = 350, height = 20,border_line_color=None,location = (0,0), orientation = 'horizontal')

Dist, dist_col = district_filter(df,d_shp,"School","government",gen,caste,clas,sector)
District = GeoJSONDataSource(geojson = Dist.to_json())
dist_source = ColumnDataSource(dist_col)
state,state_col = state_filter(df,s_shp,"School","government",gen,caste,clas,sector)
State = GeoJSONDataSource(geojson = state.to_json())
state_source = ColumnDataSource(state_col)


TOOLS = "pan,wheel_zoom,box_zoom,reset,save"
p = figure(title = 'Percentage of Enrollment in Uttar Pradesh and Bihar', plot_height = 500 , plot_width = 400, tools = TOOLS)
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None
states = p.patches('xs','ys', source = State, fill_color = {'field' :"percentage", 'transform' : color_mapper},
          line_color = 'black', line_width = 0.25, fill_alpha = 1)

Dg = figure(title = 'Percentage of Enrollment in Uttar Pradesh and Bihar District wise', plot_height = 500 , plot_width = 400,  tools = TOOLS)
Dg.xgrid.grid_line_color = None
Dg.ygrid.grid_line_color = None
Districts = Dg.patches('xs','ys', source = District, fill_color = {'field' :"percentage", 'transform' : colormapper1},
          line_color = 'black', line_width = 0.25, fill_alpha = 1)
p.add_tools(HoverTool(renderers = [states],
                       tooltips = [('State_Name','@state_name'),
                                   ('Percentage',"@percentage")]))
Dg.add_tools(HoverTool(renderers = [Districts],
                       tooltips = [('District_Name','@district_name'),
                                   ('Percentage',"@percentage")]))
Dg.add_layout(color_bar_D, 'below')
p.add_layout(color_bar_S, 'below')


# In[11]:


ty = Div(text = """<u>Choose type of institution below <u>""")
type_l = RadioButtonGroup(labels=['Govt','Pvt Unaided','Pvt Aided','Not Known'],active=0)

El = Div(text = """<u>Choose the Education level below<u>""")
scl_lvl = RadioGroup(labels=edu, active=0)

pl = Div(text = """<u>Choose the sector below<u>""")
sctr = CheckboxGroup(labels=["Rural","Urban"], active=[0, 1])

gender = Div(text = """<u>Choose the Gender below<u>""")
gend = CheckboxGroup(labels=["Female","Male"], active=[0, 1])

sog = Div(text = """<u>Choose the Social group below<u>""")
cst = CheckboxGroup(labels=caste, active=[0,1,2,3])

inc = Div(text = """<u>Choose the class group below<u>""")
cls = CheckboxGroup(labels=clas, active=[0,1,2,3,4])

button_district = Button(label="Download district data", button_type="success", width = 150)
button_state = Button(label="Download state data", button_type="success",  width = 150)

cbar = Select(title="Choose a color here", value='RdYlGn',
              options=["Blues","Greens","Greys","Oranges","BuGn","GnBu","OrRd","RdPu","YlGn","Spectral","YlGnBu","RdYlGn","YlGnBu","YlOrBr","YlOrRd"], width=150)



def update_data(attrname, old, new):
    sctor = []
    gr = []
    sg = []
    claas = []
    ins = inst_type[type_l.active]
    bs = edu[scl_lvl.active]
    for i in sctr.active:
        sctor.append(sector[i])
    for i in gend.active:
        gr.append(gen[i])
    for i in cst.active:
        sg.append(caste[i])
    for i in cls.active:
        claas.append(clas[i])
    s_d,state_c = state_filter(df,s_shp,bs,ins,gr,sg,claas,sctor)
    d_d, dist_c= district_filter(df,d_shp,bs,ins,gr,sg,claas,sctor)
    State.geojson = s_d.to_json()
    District.geojson = d_d.to_json()
    state_source.data = state_c
    dist_source.data = dist_c
    palette = brewer[cbar.value][4][::-1]
    color_mapper.palette = palette
    color_bar_S.color_mapper.palette = palette
    color_bar_D.color_mapper.palette = palette
    states.glyph.fill_color = {'field' :"percentage", 'transform' : color_mapper}
    Districts.glyph.fill_color = {'field' :"percentage", 'transform' : color_mapper}
    button_state.button_type = "success"
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
cbar.on_change("value",update_data)

plot = row(p,Dg,column(cbar,button_state,button_district))
widgets = column(ty,type_l,El,scl_lvl,pl,sctr,gender,gend,sog,cst,inc,cls)
layout = column(row(widgets,plot))
curdoc().add_root(layout)
curdoc().title = "The Tale of Two States"
