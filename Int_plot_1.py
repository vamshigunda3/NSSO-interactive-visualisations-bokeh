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


x["hhid"] = x["Common-ID"].str.slice(3,34)
x['NSS_Region']= x["hhid"].str.slice(12,15)
x["statecode"] = x['NSS_Region'].str.slice(0,2)
x["distcode"] = x["hhid"].str.slice(15,17)


# In[8]:


A = x[["Common-ID",'statecode','distcode',"Type of institution"]]
A[['statecode','distcode']] = A[['statecode','distcode']].astype(int)


# In[9]:


Nss_csv = pd.read_csv("/home/vamshi/Documents/Education Project/Layout Files/NSSO_GIS - NSSO_GIS.csv")


# In[10]:


Nss_csv.rename(columns = {"State_Code":"statecode","District_Code":'distcode'},inplace = True)


# In[11]:


Nss_csv.drop(columns = ["Unnamed: 0"],inplace = True)


# In[12]:


Nss_merged = pd.merge(Nss_csv,A, how = "right", on =['statecode','distcode'] )


# In[13]:


Analysis = Nss_merged.groupby(["statecode","State_Name","distcode","District_Name","GIS_District_Code"]).size().to_frame("Enrollment")


# In[14]:


Analysis.reset_index(inplace = True)


# In[15]:


#Analysis['Type of institution'].value_counts()
Analysis[['statecode','distcode']] = Analysis[['statecode','distcode']].astype(int)


# In[16]:


file_GIS = gpd.read_file('/home/vamshi/Documents/Education Project/India_Districts/Indian_Districts.shp')


# In[17]:


file_GIS['geometry'] = file_GIS['geometry'].simplify(tolerance = 0.05)


# In[18]:


file_GIS.rename(columns = {"distcode":"GIS_District_Code", 'statename':'State_Name'}, inplace = True)


# In[19]:


#file_GIS[["statecode","GIS_District_Code"]].dtypes


# In[20]:


file_GIS[["statecode","GIS_District_Code"]] = file_GIS[["statecode","GIS_District_Code"]].astype(int)


# In[21]:


#A = file_GIS.loc[(file_GIS["statecode"]== 1)]
#A


# In[22]:


Final = file_GIS.merge(Analysis, on = ["GIS_District_Code"], how = "left")
#F2 = Final.merge(A, how = "right", on = ["statecode"])


# In[23]:


Final.drop(columns = ["objectid","State_Name_y","state_ut","countrynam","distname","statecode_x",'statecode_y','distcode','GIS_District_Code'], inplace = True)


# In[24]:


Final.rename(columns = {"State_Name_x":'State_Name'},inplace = True)


# In[25]:


#Telangana = Final[Final.State_Name == 'TELANGANA']


# In[ ]:





# In[26]:


def con_json(file):
    import json
    from bokeh.models import GeoJSONDataSource
    geosource = GeoJSONDataSource(geojson = file.to_json())
    return geosource


# In[27]:


state_names = Final['State_Name'].unique().tolist()


# In[28]:


##   Functions  ##
def change_data(file, State_Name):
    """import the file and the name of the state in Capital"""
    State_Name = State_Name.upper()
    c_data = file[file["State_Name"] == State_Name]
    return c_data


# In[29]:


c = change_data(Final,'TELANGANA')


# In[30]:


c


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[35]:


from bokeh.io import output_notebook, show, output_file, save
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar, HoverTool, Select
from bokeh.palettes import brewer
from bokeh.io.doc import curdoc
from bokeh.layouts import widgetbox, row, column
from bokeh.models.widgets import Select
import json

#Input GeoJSON source that contains features for plotting.
#geosource = GeoJSONDataSource(geojson = json_data)
State_df = change_data(Final,state_names[0])
State_geo = GeoJSONDataSource(geojson = State_df.to_json())

#Define a sequential multi-hue color palette.
palette = brewer['Blues'][8]
#Reverse color order so that dark blue is highest obesity.
palette = palette[::-1]
#Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors.
color_mapper = LinearColorMapper(palette = palette, low = 10, high = 1500)

tick_labels = {'50': '50', '350':'350', '700':'700', '1050':'1050','1400': '>1400%'}

color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8,width = 500, height = 20,border_line_color=None,location = (0,0), orientation = 'horizontal', major_label_overrides = tick_labels)

p = figure(title = 'Enrollment in school statewise', plot_height = 600 , plot_width = 950, toolbar_location = None)
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None

states = p.patches('xs','ys', source = State_geo, fill_color = {'field' :'Enrollment', 'transform' : color_mapper},
          line_color = 'black', line_width = 0.25, fill_alpha = 1)
p.add_tools(HoverTool(renderers = [states],
                       tooltips = [('District_Name','@District_Name'),
                                  ('State_Name','@State_Name'),
                                   ('Enrollment','@Enrollment')]))
p.add_layout(color_bar, 'below')
select = Select(title="Select a state here:", value = state_names[0], options= state_names)

def update_plot(attrname, old, new):
    cr = select.value
    State_df = change_data(Final, cr)
    State_geo.geojson = State_df.to_json()
    
    p.title.text = cr
    
select.on_change('value', update_plot)
layout = row(p, select)
curdoc().add_root(layout)
show(layout)


# from bokeh.io import output_notebook, show, output_file, save
# from bokeh.plotting import figure
# from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar, HoverTool, Select
# from bokeh.palettes import brewer
# from bokeh.io.doc import curdoc
# from bokeh.layouts import widgetbox, row, column
# from bokeh.models.widgets import Select
# 
# def plot(input_field):
#     low = input_field.min()
#     high = input_field.max()
#     color_mapper = LinearColorMapper(palette = palette, low = low, high = high)
#     tick_labels = {'0': '0', '100': '100', '300':'300', '600':'600', '900':'900', '1200':'1200', '1400': '>1400%'}
#     color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8,width = 500, height = 20,
#     border_line_color=None,location = (0,0), orientation = 'horizontal', major_label_overrides = tick_labels)
#     p = figure(title = 'Enrollment in school statewise', plot_height = 600 , plot_width = 950, toolbar_location = "right")
#     p.xgrid.grid_line_color = None
#     p.ygrid.grid_line_color = None
#     source = con_json(input_field)
#     states = p.patches('xs','ys', source = source,fill_color = {'field' :'Enrollment', 'transform' : color_mapper},
#           line_color = 'black', line_width = 0.25, fill_alpha = 1)
#     p.add_tools(HoverTool(renderers = [states],
#                        tooltips = [('District_Name','@District_Name'),
#                                   ('State_Name','@State_Name'),
#                                    ('Enrollment','@Enrollment')]))
#     p.add_layout(color_bar, 'below')
#     return p
#      
# 
# def update_plot(attr, old, new):
#     cr = select.value
#     input_field = Final.loc[Final['State_Name'] == cr]
#     p = plot(input_field)
#     layout = column(p, widgetbox(select))
#     curdoc().clear()
#     curdoc().add_root(layout)
#     
#     
#     
# 
# 
# 
# 

# from bokeh.io import output_notebook, show, output_file, save
# from bokeh.plotting import figure
# from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar, HoverTool
# from bokeh.palettes import brewer
# 
# #Input GeoJSON source that contains features for plotting.
# geosource = GeoJSONDataSource(geojson = json_data)
# #Define a sequential multi-hue color palette.
# palette = brewer['Blues'][8]
# #Reverse color order so that dark blue is highest obesity.
# palette = palette[::-1]
# #Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors.
# color_mapper = LinearColorMapper(palette = palette, low = 0, high = 1500)
# 
# tick_labels = {'0': '0', '100': '100', '300':'300', '600':'600', '900':'900', '1200':'1200', '1400': '>1400%'}
# 
# color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8,width = 500, height = 20,
# border_line_color=None,location = (0,0), orientation = 'horizontal', major_label_overrides = tick_labels)
# 
# p = figure(title = 'Enrollment in school statewise', plot_height = 600 , plot_width = 950, toolbar_location = None)
# p.xgrid.grid_line_color = None
# p.ygrid.grid_line_color = None
# 
# states = p.patches('xs','ys', source = geosource,fill_color = {'field' :'Enrollment', 'transform' : color_mapper},
#           line_color = 'black', line_width = 0.25, fill_alpha = 1)
# p.add_tools(HoverTool(renderers = [states],
#                        tooltips = [('District_Name','@District_Name'),
#                                   ('State_Name','@State_Name'),
#                                    ('Enrollment','@Enrollment')]))
# p.add_layout(color_bar, 'below')
# # select = Select(title="Select a state here:", value = state_names[0], options= state_names)
# # select.on_change('value', update_plot)
# # layout = row(p, select)
# # curdoc().clear()
# # curdoc().add_root(layout)
# output_file('India.html', mode='inline')
# output_notebook()
# show(p)
# 

# In[ ]:




