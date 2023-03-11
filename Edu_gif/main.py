import time
import pandas as pd
import geopandas as gpd
from bokeh.io import output_notebook, show, output_file, save, curdoc
from bokeh.models import Button,CheckboxGroup, CustomJS,RadioButtonGroup,Div, Label, Slider, GeoJSONDataSource, ColumnDataSource,LinearColorMapper, ColorBar, HoverTool, Select
from bokeh.plotting import figure
from bokeh.palettes import brewer
from bokeh.layouts import widgetbox, row, column
from bokeh.themes import Theme
import json
from . import d_files
from os.path import dirname, join

data, states_g,states_n = d_files.all_data["data"]

def get_govt_enrolment_state(x, states,states_names,typel, level_l, sector_l, gender_l, caste_l, class_l,rounds):
    data = x.loc[(x['level'].isin(level_l)) & (x['sector'].isin(sector_l)) & (x['gender'].isin(gender_l)) & (x['caste'].isin(caste_l)) & (x['Class'].isin(class_l))]
    total=data.groupby(['round','state_code']).agg({'moi_weight':'sum'}).rename(columns={'moi_weight':'total'})
    govt=data.loc[data['type'].isin(typel)].groupby(['round','state_code']).agg({'moi_weight':'sum'}).rename(columns={'moi_weight':'govt'})
    x = total.merge(govt,on=['round','state_code']).reset_index()
    x['proportion']=round(x.govt/x.total,2)
    x=x[['round','state_code','proportion']]
    x=pd.pivot(x,index=['state_code'],values=['proportion'],columns=['round'])
    if(len(x.index)<1):
        x=pd.DataFrame(columns=['state_code','NSSO_64','NSSO_71','NSSO_75'])
        w = pd.merge(states_names,x, on = ["state_code"], how = "outer")
        w = w[w.columns[1:]]
        w.columns = ["State_Name","NSSO_64","NSS0_71","NSS0_75"]
    else:
        w = pd.merge(states_names,x, on = ["state_code"])
        w = w[w.columns[1:]]
        w.columns = ["State_Name","NSSO_64","NSS0_71","NSS0_75"]
    x=states.merge(x,on=['state_code'],how='left')
    x=x.rename(columns={x.columns[3]:'NSSO_64',x.columns[4]:'NSSO_71',x.columns[5]:'NSSO_75'})
    yr = ['NSSO_64','NSSO_71','NSSO_75']
    if str(rounds) == yr[0][-2:]:
        x = x[["geometry",'state_name','NSSO_64']]
    elif str(rounds) == yr[1][-2:]:
        x=x[["geometry",'state_name','NSSO_71']]
    else:
        x=x[["geometry",'state_name','NSSO_75']]
    x.columns = ["geometry",'state_name','proportion']
    return x, w



years = [64,71,75]
a_years = [2007,2014,2017]
typ = ['Government','Private Aided','Private Unaided','Not Known']
school_level = ['Pre-Primary','Primary','Middle', 'Secondary','Higher Secondary','Higher Education', 'NFE']
sector = list(data.sector.unique())
gen = ['Female', 'Male']
caste = ['Others', 'OBC', 'ST', 'SC']
cls = ['Very High','High', 'Middle','Low', 'Very Low']




d,w = get_govt_enrolment_state(data, states_g,states_n,[typ[0]],['Pre-Primary','Middle','Secondary'], ['Urban','Rural'], ["Male","Female"], ['Others', 'OBC', 'ST', 'SC'], ['Very High','High', 'Middle','Low', 'Very Low'],years[0])

source = ColumnDataSource(w)
palette = brewer['BuPu'][4][::-1]
#Reverse color order so that dark blue is highest obesity.
#Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors.
color_mapper = LinearColorMapper(palette = palette, low = 0, high = 1)
#colormapper1 = LinearColorMapper(palette = palette, low = 5, high = 1400)
color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8,width = 500, height = 20,border_line_color="yellow",location = (0,0), orientation = 'horizontal')
state_source = GeoJSONDataSource(geojson = d.to_json())


p = figure(title = 'Enrollment in education Statewise', plot_height = 550 , plot_width = 550, tools = "pan,wheel_zoom,box_zoom,reset,save")
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None
states = p.patches('xs','ys', source = state_source, fill_color = {'field' :'proportion', 'transform' : color_mapper},
          line_color = 'black', line_width = 0.25, fill_alpha = 1)
label = Label(x = 68,y = 7, text=str(a_years[0]), text_font_size='40px', text_color='#666262')
p.add_tools(HoverTool(renderers = [states],
                       tooltips = [('State_Name','@state_name'),
                                   ('Enrollment','@proportion')]))
p.background_fill_color="#F5F5DC"
# #d3d3d3#b8b09b
p.title.text_font = "cambria"
p.title.text_font_size="16px"
p.add_layout(color_bar, 'below')
p.add_layout(label)
p.yaxis.visible = False
p.xaxis.visible = False


title = Div(text = """<P/> The below Visualisation provides information on the percentage of enrollment in government 
institutions from the three nsso rounds 64, 71 and 75 across all states with multiple other filters<P/> """)

ty = Div(text = """<u>Institution type: <u>""")

type_l = RadioButtonGroup(labels=['Govt','Pvt Aided','Pvt Unaided','Not Known'],active=0)
El = Div(text = """<u>Choose the Education level below<u>""")
scl_lvl = CheckboxGroup(labels=school_level, active=[0,2,3])
pl = Div(text = """<u>Choose the sector below<u>""")
sctr = CheckboxGroup(labels=sector, active=[0, 1])
gender = Div(text = """<u>Choose the Gender below<u>""")
gend = CheckboxGroup(labels=gen, active=[0, 1])
sog = Div(text = """<u>Choose the Social group below<u>""")
cst = CheckboxGroup(labels=caste, active=[0,1,2,3])
inc = Div(text = """<u>Choose the class group below<u>""")
clas = CheckboxGroup(labels=cls, active=[0,1,2,3,4])
slider = Slider(start=0, end=2, value=0, step=1, title="Rounds")
button = Button(label='► Play', width=40)
button_D = Button(label="Download data", button_type="success", width = 150)
cbar = Select(title="Choose a color here", value='BuPu',
              options=["Blues","Greens","Greys","Oranges","BuGn","BuPu","GnBu","OrRd","RdPu","YlGn","Spectral","YlGnBu","RdYlGn","YlGnBu","YlOrBr","YlOrRd"], width=150)


def animate_update():
    val = slider.value + 1
    if val > 2:
        val = 0
    slider.value = val
    

def update_data(attrname, old, new):
    ty_l = []
    sl = []
    sctor = []
    gr = []
    sg = []
    claas = []
    ty_l.append(typ[type_l.active])
    rounds = years[slider.value]
    ar = a_years[slider.value]
    for i in scl_lvl.active:
        sl.append(school_level[i])
    for i in sctr.active:
        sctor.append(sector[i])
    for i in gend.active:
        gr.append(gen[i])
    for i in cst.active:
        sg.append(caste[i])
    for i in clas.active:
        claas.append(cls[i])
    cd,w = get_govt_enrolment_state(data,states_g,states_n,ty_l,sl,sctor,gr,sg,claas,rounds)
    state_source.geojson = cd.to_json()
    source.data = w
    label.text = str(ar)
    palette = brewer[cbar.value][4][::-1]
    color_mapper.palette = palette
    color_bar.color_mapper.palette = palette
    states.glyph.fill_color = {'field' :"proportion", 'transform' : color_mapper}

callback_id = None
def animate():
    global callback_id
    if button.label == '► Play':
        button.label = '❚❚ Pause'
        callback_id = curdoc().add_periodic_callback(animate_update, 1000)
    else:
        button.label = '► Play'
        curdoc().remove_periodic_callback(callback_id)

button_D.js_on_click(CustomJS(args=dict(source=source),
                            code=open(join(dirname(__file__),"download.js")).read()))
button.on_click(animate)
slider.on_change('value', update_data)
scl_lvl.on_change("active",update_data)
sctr.on_change("active",update_data)
gend.on_change("active",update_data)
cst.on_change("active",update_data)
clas.on_change("active",update_data)
type_l.on_change("active",update_data)
cbar.on_change("value",update_data)

plot = column(row(p,column(cbar,button_D)),row(slider,button),)
widgets = column(ty,type_l,El,scl_lvl,pl,sctr,gender,gend,sog,cst,inc,clas)
layout = column(row(widgets,plot),background="beige")
layout.sizing_mode = 'scale_width'
curdoc().add_root(layout)
curdoc().title = "NSSO Analysis"
curdoc().theme = Theme(filename = join(dirname(__file__),"theme.yml"))
