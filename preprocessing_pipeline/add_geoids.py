from state_codes import state_codes
import pandas as pd
import re
import requests
import csv
import json
import geopandas
from config import *

def get_geoids():

  incident_dict = {}
  incidents = []
  with open(GVA_CSV,'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
      incident_dict[row['Incident ID']]=row
      if row['Latitude']!='' and row['Longitude']!='':
        row['Incident Characteristics']=re.sub('\n','||',row['Incident Characteristics'])
        incidents.append(row)
  
  print(len(incidents))
  
  df = pd.DataFrame(incidents)
  df.to_csv(GVA_WITH_GEOID,index=False)
  
      
  df = geopandas.read_file(GVA_WITH_GEOID)
  geometry = geopandas.points_from_xy(df.Longitude, df.Latitude,crs = 'EPSG:4269')
  incidents = geopandas.GeoDataFrame(data = df,geometry = geometry)
  
  for state_name in state_codes.keys():
    state = state_codes[state_name]
    print(state,state_name)
    map_path = GIS_PATH+state+'/tl_2018_'+state+'_tract.shp'
    state_map = geopandas.read_file(map_path)
    
    combined = geopandas.sjoin(incidents,state_map)
    
    for i in combined.index.values:
      incident_id = str(combined.at[i,'Incident ID'])
      if len(incident_id)>9:
        incident_id = incident_id.split('\n')[0].split(' ')
        incident_id = incident_id[len(incident_id)-1]
      geoid = str(combined.at[i,'GEOID'])
      geoid = geoid.split('\n')[0].split(' ')
      incident_dict[incident_id]['geoid']=str(geoid[0])
      #data[post_id]['GEOID'] = str(geoid)#str(round(float(geoid)))
  
  count = 0
  missing=0
  for i,key in enumerate(incident_dict.keys()):
    if i%1000==0:
      print(i)
    if not incident_dict[key].get('geoid',None):  
      incident_dict[key]['geoid']='NA'
      #incident_dict[key]['white']='NA'
      count +=1
    #else:
     # incident_dict[key]['white']=get_census_data(incident_dict[key])
      #if incident_dict[key]['white']=='NA':
       # missing+=1
  print(count,missing)
  
  data=[]
  for key in incident_dict:
    data.append(incident_dict[key])
  new_df = pd.DataFrame(data)
  new_df.to_csv(GVA_WITH_GEOID,index=False)
  
      