#!/usr/bin/env python
# coding: utf-8


import pandas as pd
import numpy as np
from bokeh.io import output_notebook, show, output_file, save
from bokeh.plotting import figure
from bokeh.models import Legend,NumeralTickFormatter,Panel,CheckboxGroup,FactorRange,LabelSet, RadioGroup,ColumnDataSource, Button, HoverTool,Div, Select, RadioButtonGroup
from bokeh.palettes import brewer, Set1
from bokeh.io.doc import curdoc
from bokeh.layouts import widgetbox, row, column
from bokeh.transform import factor_cmap
from bokeh.models.widgets import Select 
from . import d_files

data = d_files.all_data["data"]





def data_filter(df,cate,level,year,inst_type):
    """Takes five inputs 1) dataframe, 2) the category 3) education level 4) year and 5) instype"""
    df = df[(df.inst_type.isin(inst_type))&(df["edu_lev_gen"] == level) & (df["year"] == year)]
    cleaned = df[["total_expd",cate]]
    Trail = cleaned.groupby(cate, observed = True)
    q1 = Trail.quantile(q=0.25)
    q2 = Trail.quantile(q=0.5)
    q3 = Trail.quantile(q=0.75)
    iqr = q3 - q1
    upper = q3 + 1.5*iqr
    lower = 0
    name = list(q1.columns)
    boxes_data = pd.concat([
        q1.rename(columns={name[0]:"q1"}),
        q2.rename(columns={name[0]:"q2"}),
        q3.rename(columns={name[0]:"q3"}),
        iqr.rename(columns={name[0]:"iqr"}),
        upper.rename(columns={name[0]:"upper"})], axis=1)
    boxes_data['lower'] = 0
    boxes_data.reset_index(inplace = True)
#     def outliers(group):
#         cat = group.name
#         return group[(group[name[0]] > upper.loc[cat][name[0]]) | (group[name[0]] < lower)][name[0]]
#     out = Trail.apply(outliers).dropna()
#     if not out.empty:
#         outx = []
#         outy = []
#         for keys in out.index:
#             outx.append(keys[0])
#             outy.append(out.loc[keys[0]].loc[keys[1]])

#     circles_data = pd.DataFrame([outx,outy]).transpose()
#     circle_col = [cate,"Outliers"]
#     circles_data.columns = circle_col
    
    #circles_data = circles_data[circles_data["Outliers"] < 50]
#     merged = pd.concat([boxes_data,circles_data])
#     merged.replace(np.nan,0, inplace = True)
    boxes_data = boxes_data.astype({"q1":"int","q2":"int","q3":"int","iqr":"int","upper":"int"})
    #merged = merged.astype({"q1":"int","q2":"int","q3":"int","iqr":"int","upper":"int","Outliers":"int"})
    boxes_data= boxes_data.sort_values(boxes_data.columns[0]).reset_index(drop = True)
    return boxes_data

def box_plot(df,title,cat):
    """add dataframe, title and category"""
    source = ColumnDataSource(df)
    x_axis = list(df[cat].unique())
    p = figure(background_fill_color="#efefef", x_range=x_axis,y_range = (0,150000),plot_width = 800,toolbar_location="right")
    p.yaxis.formatter=NumeralTickFormatter(format="0")
    # stems

    s1 = p.segment(cat, "upper", cat, "q3", line_color="black",source = source)
    s2 = p.segment(cat,"lower", cat, "q1", line_color="black",source = source)


    b1 = p.vbar(cat, 0.7, "q2", "q3", fill_color="#4169E1", line_color="black",source = source)
    b2 = p.vbar(cat, 0.7, "q1", "q2", fill_color="#2AAA8A", line_color="black",source = source)

    r1 =p.rect(cat, "lower", 0.2, 0.01, line_color="black",source = source)
    r2 = p.rect(cat, "upper", 0.2, 0.01, line_color="black",source = source)

#     if not df.Outliers.empty:
#         c = p.circle(cat, "Outliers", size=2, color="#F38630", fill_alpha=0.6,source = source)


    p.add_tools(HoverTool(renderers = [s1,s2,b1,b2,r1,r2],tooltips =[('q1', '@q1'),
                                 ('q3', '@q3'),
                                 ('iqr', '@iqr'),
                                ("upper",'@upper')]))
#     p.add_tools(HoverTool(renderers = [c],tooltips = [("Expenditure","@Outliers")]))
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = "white"
    p.grid.grid_line_width = 2
    p.xaxis.major_label_text_font_size="16px"
    p.title.text = title
    return p


# In[ ]:





# In[ ]:





# In[20]:


cat = ["Social group", "Region","Religion","Gender","Class","Sector"]
RG = ['upto primary (5th)','upto secondary (6-10)','higher_sec','higher_edu']
inst_type = ["Govt","Private unaided","Private aided","Not known"]
year_l = ["2007","2014","2017"]
year = [2007,2014,2017]

## Inside df
Edu_list = ['Upto Primary','Upto Secondary','Higher Secondary','Higher Edu']
categories = ['social_group','region','religion','gender','clas','place']
itp = ['government', 'private unaided', 'private aided', 'not known']
#titles
title = ["Caste wise expenditure on","Region wise expenditure on ","Religion wise expenditure on ","Gender wise expenditure on ","Class wise expenditure on ","Sector wise expenditure on "]
#title_he = ["Caste wise expenditure on higher education","Region wise expenditure on higher education","Religion wise expenditure on higher education","Gender wise expenditure on higher education","Class wise expenditure on higher education","Sector wise expenditure on higher education"]

title_f = title[2] + "education: "+str(Edu_list[0]) 
x = data_filter(data,categories[2],RG[0],year[0],itp)
p = box_plot(x,title_f,categories[2])

inst = CheckboxGroup(labels=inst_type, active=[0,1,2,3])
SG = RadioGroup(labels = cat, active = 2)
yr = RadioGroup(labels = year_l, active = 0)
E_level = RadioGroup(labels=Edu_list, active=0)
#div_mh = Div(text = """<h3/> The below visualisation provides information on expenditure spent on education with respect to social group, religion, region and gender. <h3/> """)
E_t = Div(text = """<u/> Choose the educational level by selecting the option below<u/>""")
E_S = Div(text = """<u/> Choose the categories of plots below <u/>""")
E_y = Div(text = """<u/> Choose the year below <u/>""")
ins_type = Div(text = """<u/> Choose the type of institution below <u/>""")

def update_data(attrname, old, new):
    inst_ty = []
    for i in inst.active:
        inst_ty.append(itp[i])
    CV = SG.active
    R = E_level.active
    y = yr.active
    print("length of year",year[y])
    cd = data_filter(data,categories[CV],RG[R],year[y],inst_ty)
    print("Length of dataframe",len(cd))
    title_f = title[CV]+ "education: "+str(Edu_list[R])
    ch = box_plot(cd,title_f,categories[CV])
    inputs.children[0] = ch

inst.on_change("active",update_data)
SG.on_change("active",update_data)
E_level.on_change("active",update_data)
yr.on_change("active",update_data)

inputs = column(p)
level = column(ins_type,inst,E_y,yr,E_t,E_level,E_S,SG)
layout = column(row(level,inputs))
curdoc().add_root(layout)
curdoc().title = "NSSO Analysis"

#money = [140000,140000,160000,120000,160000,140000]

#sum(money)/5


#show(layout)



