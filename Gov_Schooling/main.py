import time
start = time.process_time()
print("started",start)
import pandas as pd
import numpy as np
from bokeh.io import curdoc, show
from bokeh.layouts import column, row
from bokeh.models import (Button, ColumnDataSource, CustomJS, DataTable,
                          NumberFormatter,RadioButtonGroup,CheckboxGroup,CheckboxButtonGroup,TableColumn,Div,HTMLTemplateFormatter)
from os.path import dirname, join
from . import d_files
loaded_packages = time.process_time()
print("loaded packages",time.process_time()-start)

data, states = d_files.all_data["data"]
print("loaded files ",time.process_time()-loaded_packages)

def get_govt_enrolment_state(x, states, typel,level_l, sector_l, gender_l, caste_l, class_l):
    data = x.loc[(x['level'].isin(level_l)) & (x['sector'].isin(sector_l)) & (x['gender'].isin(gender_l)) & (x['caste'].isin(caste_l)) & (x['Class'].isin(class_l))]
    total=data.groupby(['round','state_code']).agg({'moi_weight':'sum'}).rename(columns={'moi_weight':'total'})
    govt=data.loc[data['type'].isin(typel)].groupby(['round','state_code']).agg({'moi_weight':'sum'}).rename(columns={'moi_weight':'govt'})
    x = total.merge(govt,on=['round','state_code']).reset_index()
    x['proportion']=round(x.govt/x.total,2)
    x=x[['round','state_code','proportion']]
    x=pd.pivot(x,index=['state_code'],values=['proportion'],columns=['round'])
    if(len(x.index)<1):
        x=pd.DataFrame(columns=['state_code','NSSO_64','NSSO_71','NSSO_75'])
    x=states.merge(x,on=['state_code'],how='left')
#    x=states.merge(x,on=['state_code'])
    x=x.rename(columns={x.columns[2]:'NSSO_64',x.columns[3]:'NSSO_71',x.columns[4]:'NSSO_75'})
    cols = x.columns.drop('State_Name')
    x[cols] = x[cols].apply(pd.to_numeric, errors='coerce')
    x["change"] = x["NSSO_75"]-x["NSSO_64"]
    x["change"] = x["change"].round(2)
    x=x[['State_Name','NSSO_64','NSSO_71','NSSO_75','change']]
    x=x.sort_values(['change'])
    return(x)

typel = ['Government','Private Aided','Private Unaided','Not Known']
school_level = ['Pre-Primary','Primary','Middle', 'Secondary','Higher Secondary','Higher Education', 'NFE']
sector = list(data.sector.unique())
gen = ['Male','Female']
caste = ['Others', 'OBC', 'ST', 'SC']
cls = ['Very High','High', 'Middle','Low', 'Very Low']

d = get_govt_enrolment_state(data, states,['Government'],['Pre-Primary','Primary','Middle','Secondary','Higher Secondary'], ['Urban','Rural'], ['Male','Female'], ['Others', 'OBC', 'ST', 'SC'], ['Very High','High', 'Middle','Low', 'Very Low'])
d = d.replace(np.nan,"NaN")
source = ColumnDataSource(d)

template_75="""
            <div style="background:<%= 
                (function colorfromint(){
                    if(NSSO_75 > 0.7)
                        {return('#31a354')}
                    else if (NSSO_75 < 0.35)
                        {return ('#e5f5e0')}
		    else if (NSSO_75 == "NaN")
			{return ("white")}
                    else {return('#a1d99b')}
                        }())
                        %>;
                color: black">
                <%= value %>
                </font> 
            </div>
            """
template_71 = """
            <div style="background:<%= 
                (function colorfromint(){
                    if(NSSO_71 > 0.7)
                        {return('#31a354')}
                    else if (NSSO_71 < 0.35)
                        {return ("#e5f5e0")}
		    else if (NSSO_71 == "NaN")
			{return ("white")}
                    else {return('#a1d99b')}
                        }())
                        %>;
                color: black">
                <%= value %>
                </font> 
            </div>
            """
template_64 = """
            <div style="background:<%= 
                (function colorfromint(){
                    if(NSSO_64 > 0.7)
                        {return('#31a354')}
                    else if (NSSO_64 < 0.35)
                        {return ('#e5f5e0')}
		    else if (NSSO_64 == "NaN")
			{return ("white")} 
                    else {return('#a1d99b')}
                        }())
                        %>;
                color: black">
                <%= value %>
                </font> 
            </div>
            """
template_change = """
            <div style="background:<%= 
                (function colorfromint(){
                    if(change < -0.1)
                        {return('red')}
                    else if (change < 0)
                        {return ('yellow')}
                    else {return('green')}
                        }())
                        %>;
                color: black">
                <%= value %>
                </font> 
            </div>
            """
formatter_75 =  HTMLTemplateFormatter(template=template_75)
formatter_71 = HTMLTemplateFormatter(template=template_71)
formatter_64 = HTMLTemplateFormatter(template=template_64)
formatter_change = HTMLTemplateFormatter(template=template_change)

columns = [
    TableColumn(field="State_Name", title="State_Name"),
    TableColumn(field="NSSO_64", title="NSSO_64",formatter = formatter_64),
    TableColumn(field='NSSO_71', title='NSSO_71',formatter = formatter_71),
    TableColumn(field='NSSO_75', title='NSSO_75',formatter = formatter_75),
    TableColumn(field='change', title='Change(75-64)',formatter = formatter_change)
    ]
 
dt = DataTable(source=source,columns=columns, fit_columns=True,
                       selectable = True,
                       sortable = True,width=940,height = 930)

#title = Div(text = """<b>Proportion of Enrolment</b>: The table below provides information on the percentage of enrolment in different types of institutions across all states. The data used for the below table is from NSSO survey of 64th (2007), 71st (2014) and 75th (2017) rounds. You can use the buttons given to select and filter through the data. To sort by column click on the column header.""")

ty = Div(text = """<u>Institution type: <u>""")
type_l = RadioButtonGroup(labels=['Govt','Pvt Aided','Pvt Unaided','Not Known'],active=0)
El = Div(text = """<u>Choose the Education level below<u>""")
scl_lvl = CheckboxGroup(labels=school_level, active=[0,1,2,3,4])
pl = Div(text = """<u>Choose the sector below<u>""")
sctr = CheckboxGroup(labels=sector, active=[0, 1])
gender = Div(text = """<u>Choose the Gender below<u>""")
gend = CheckboxGroup(labels=gen, active=[0, 1])
sog = Div(text = """<u>Choose the Social group below<u>""")
cst = CheckboxGroup(labels=caste, active=[0,1,2,3])
inc = Div(text = """<u>Choose the class group below<u>""")
clas = CheckboxGroup(labels=cls, active=[0,1,2,3,4])
button_text = Div(text = """<u>Download the data below <u>""")
button = Button(label="Download", button_type="success",width = 150)

def update_data(attrname, old, new):
    ty_l = []
    sl = []
    sctor = []
    gr = []
    sg = []
    claas = []

    ty_l.append(typel[type_l.active])
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
    cd = get_govt_enrolment_state(data,states,ty_l,sl,sctor,gr,sg,claas)
    cd = cd.replace(np.nan,"NaN")
    source.data = cd


button.js_on_click(CustomJS(args=dict(source=source),
                            code=open(join(dirname(__file__),"download.js")).read()))

type_l.on_change("active",update_data)
scl_lvl.on_change("active",update_data)
sctr.on_change("active",update_data)
gend.on_change("active",update_data)
cst.on_change("active",update_data)
clas.on_change("active",update_data)

widgets = column(ty,type_l,El,scl_lvl,pl,sctr,gender,gend,sog,cst,inc,clas,button_text,button)
layout = column(row(widgets,dt))
curdoc().add_root(layout)
curdoc().title = "NSSO Analysis"
print("end ",time.process_time()-start)
