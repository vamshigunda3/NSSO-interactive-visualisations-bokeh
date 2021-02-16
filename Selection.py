#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import geopandas as gpd


# In[2]:


import os
os.chdir("/home/vamshi/Documents/Education Project/Codes")
import Data_Cleaning_Auto


# In[3]:


path = ('/home/vamshi/Documents/Education Project/Layout Files/Level5.csv')


# In[4]:


file = ('/home/vamshi/Documents/Education Project/Data/R75252L05.TXT')


# In[5]:


Data = Data_Cleaning_Auto.data_cleaning(file,path)


# In[6]:


x = Data.changed_values()


# In[7]:


Nss_csv = pd.read_csv("/home/vamshi/Documents/Education Project/Layout Files/NSSO_GIS - NSSO_GIS.csv")


# In[12]:


A = x[["Common-ID",'State_Code','District_Code',"Type of institution"]]


# In[16]:


A = A.astype({"State_Code":"int","District_Code":"int"})


# In[19]:


merged = pd.merge(A,Nss_csv, how = "left", on = ['State_Code','District_Code'])
merged.drop(columns = ["Unnamed: 0","S_No"],inplace = True)


# In[35]:


Analysis_Districts = merged.groupby(["State_Code","State_Name","District_Code","District_Name","GIS_District_Code"]).size().to_frame("Enrollment").reset_index()


# In[155]:


Analysis_State = merged.groupby(["State_Name"]).size().to_frame("Enrollment").reset_index()


# In[156]:


Analysis_State["State_Name"] = Analysis_State["State_Name"].str.upper()


# In[84]:


file_GIS = gpd.read_file('/home/vamshi/Documents/Education Project/India_Districts/Indian_Districts.shp')


# In[85]:


file_GIS['geometry'] = file_GIS['geometry'].simplify(tolerance = 0.05)


# In[87]:


file_GIS.rename(columns = {"distcode":"GIS_District_Code", 'statename':'State_Name'}, inplace = True)


# In[88]:


file_GIS = file_GIS.astype({"GIS_District_Code":"int"})


# In[91]:


file_GIS['geometry'] = file_GIS['geometry'].buffer(0.01)


# In[92]:


dfile = file_GIS[['statecode',"geometry","State_Name"]]


# In[95]:


dfile = dfile.dissolve(by = "statecode").reset_index()


# In[168]:


dfile["State_Name"] = dfile["State_Name"].replace({"DADRA & NAGAR HAVE":"DADRA & NAGAR HAVELI","UTTARAKHAND":"UTTARAKAND"})


# In[169]:


F_state = pd.merge(dfile,Analysis_State, how = "left", on = ["State_Name"])


# In[55]:


Final = pd.merge(file_GIS,Analysis_Districts, how = "left", on = ["GIS_District_Code"])


# In[56]:


Final.drop(columns = ['objectid','statecode','State_Name_x','state_ut','GIS_District_Code','distname', 'st_area(sh', 'st_length(',
       'countrynam',"State_Code",'District_Code'],inplace = True)


# In[177]:


Final.rename(columns = {"State_Name_y":"State_Name"}, inplace = True)


# In[181]:


Final["State_Name"] = Final["State_Name"].str.upper()


# In[218]:


def change_data(file, State_Name):
    """import the file and the name of the state in Capital"""
    #State_Name = State_Name.upper()
    c_data = file[file["State_Name"] == State_Name]
    return c_data


# In[239]:


Dist = change_data(Final, "MAHARASHTRA")


# In[238]:


from bokeh.io import output_notebook, show, output_file, save
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar, HoverTool, Select
from bokeh.palettes import brewer
from bokeh.io.doc import curdoc
from bokeh.layouts import widgetbox, row, column
from bokeh.models.widgets import Select
import json

palette = brewer['Blues'][8]
#Reverse color order so that dark blue is highest obesity.
palette = palette[::-1]
#Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors.
color_mapper = LinearColorMapper(palette = palette, low = F_state["Enrollment"].min(), high = F_state["Enrollment"].max())
colormapper1 = LinearColorMapper(palette = palette, low = 0, high = 1400)

tick_labels = {'50': '50', '350':'350', '700':'700', '1050':'1050','1400': '>1400%'}
tick_labels1 = {'50': '50', '350':'350', '700':'700', '1050':'1050','1400': '>1400%'}
color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8,width = 500, height = 20,border_line_color=None,location = (0,0), orientation = 'horizontal', major_label_overrides = tick_labels)


color_barDg = ColorBar(color_mapper=colormapper1, label_standoff=8,width = 500, height = 20,border_line_color=None,location = (0,0), orientation = 'horizontal', major_label_overrides = tick_labels1)




Dist_geo = GeoJSONDataSource(geojson = Dist.to_json())

State_geo = GeoJSONDataSource(geojson = F_state.to_json())
p = figure(title = 'Enrollment in school statewise', plot_height = 600 , plot_width = 750, tools = "tap")
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None
states = p.patches('xs','ys', source = State_geo, fill_color = {'field' :'Enrollment', 'transform' : color_mapper},
          line_color = 'black', line_width = 0.25, fill_alpha = 1)

Dg = figure(title = 'Enrollment in school District wise', plot_height = 600 , plot_width = 550, toolbar_location = None)
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None
Districts = Dg.patches('xs','ys', source = Dist_geo, fill_color = {'field' :'Enrollment', 'transform' : colormapper1},
          line_color = 'black', line_width = 0.25, fill_alpha = 1)



p.add_tools(HoverTool(renderers = [states],
                       tooltips = [('State_Name','@State_Name'),
                                   ('Enrollment','@Enrollment')]))
Dg.add_tools(HoverTool(renderers = [Districts],
                       tooltips = [('District_Name','@District_Name'),
                                   ('Enrollment','@Enrollment')]))

p.add_layout(color_bar, 'below')
Dg.add_layout(color_barDg, 'below')

def my_tap_handler(attr, old, new):
    D = F_state["State_Name"][new]
    for i in D:
        t = i
    State_df = change_data(Final, t)
    Dist_geo.geojson = State_df.to_json()
    Dg.title.text = t

#p.toolbar.active_tap = poly_select
State_geo.selected.on_change("indices",my_tap_handler)

layout = row(p, Dg)
curdoc().add_root(layout)
show(layout)


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# from bokeh.io import curdoc
# from bokeh.layouts import column
# from bokeh.models import ColumnDataSource
# from bokeh.plotting import figure
# 
# plot = figure(height=400, width=600, title='Select a point', tools='tap')
# plot_source = ColumnDataSource(data=dict(x=[0, 1], y=[0, 1]))
# renderer = plot.circle('x', 'y', source=plot_source, size=30)
# 
# master_data = [{'x_values': [1, 2, 3, 4, 5], 'y_values': [6, 7, 2, 3, 6]},
#                {'x_values': [1, 2, 3, 4, 5], 'y_values': [6, 5, 4, 3, 2]}]
# 
# plot_source2 = ColumnDataSource(data=dict(x_values_s=[], y_values_s=[]))
# c = figure(title="test", x_axis_label='numbers', y_axis_label='more numbers')
# c.multi_line(xs='x_values_s', ys='y_values_s', source=plot_source2, line_width=2)
# 
# 
# def my_tap_handler(attr, old, new):
#     print(new)
#     plot_source2.data = dict(x_values_s=[master_data[i]['x_values'] for i in new],
#                              y_values_s=[master_data[i]['y_values'] for i in new])
# 
# 
# plot_source.selected.on_change("indices", my_tap_handler)
# 
# curdoc().add_root(column(plot, c))
# curdoc().title = 'Select experiment'
# 

# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




