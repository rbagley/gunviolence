import csv
import json
import os
import ast
import datetime
#import requests
import pandas as pd
from collections import defaultdict

from config import *

#### Update 'data_request' and use 'get_acs_data' and 'combine_data' to get updated census data

def process_date_old(date):
  d=  date.split("-")
  months={
    'Jan':"01",
    'Feb':'02',
    'Mar':'03',
    'Apr':'04',
    'May':'05',
    'Jun':'06',
    'Jul':'07',
    'Aug':'08',
    'Sep':'09',
    'Oct':'10',
    'Nov':'11',
    'Dec':'12'
  }
  return "20"+d[2]+"-"+months[d[1]]+"-"+d[0]

def process_date(date):
  d=  date.split("-")
  return d[2]+"-"+d[0]+"-"+d[1]

def data_request(y,year,state,count):
  if y<2017:
    r = requests.get('https://api.census.gov/data/'+year+'/acs/acs5/profile?get=DP05_0032PE,DP05_0066PE,DP05_0060PE,DP05_0072PE,DP05_0061PE,DP05_0062PE,DP03_0062E,DP05_0001E,DP02_0066PE,DP03_0119PE,DP03_0005PE,DP02_0008PE,DP05_0018PE,DP03_0072PE&for=tract:*&in=state:'+state+'%20county:*&key='+CENSUS_KEY)
  elif y<2019:
    r = requests.get('https://api.census.gov/data/'+year+'/acs/acs5/profile?get=DP05_0037PE,DP05_0071PE,DP05_0065PE,DP05_0077PE,DP05_0066PE,DP05_0067PE,DP03_0062E,DP05_0001E,DP02_0066PE,DP03_0119PE,DP03_0005PE,DP02_0008PE,DP05_0021PE,DP03_0072PE&for=tract:*&in=state:'+state+'%20county:*&key='+CENSUS_KEY)
  else:
    r = requests.get('https://api.census.gov/data/'+year+'/acs/acs5/profile?get=DP05_0037PE,DP05_0071PE,DP05_0065PE,DP05_0077PE,DP05_0066PE,DP05_0067PE,DP03_0062E,DP05_0001E,DP02_0067PE,DP03_0119PE,DP03_0005PE,DP02_0010PE,DP05_0021PE,DP03_0072PE&for=tract:*&in=state:'+state+'%20county:*&key='+CENSUS_KEY)
  try:
    results = r.json()
    return results
  except:
    print(year,state,"error",count)
    if count<3:
      return data_request(y,year,state,count+1)
    else:
      return None
    
  
def get_acs_data():
  d={}
  data=[]
  for y in range(2014,2023):
    year = str(y)
    d[year]={}
    print(y)
    for s in range(1,57):
      state = str(s) if s>9 else "0"+str(s)
      if s not in [3,7,14,43,52]:
        results = data_request(y,year,state,0)
        if results!=None:
          for i,r in enumerate(results):  
            if i!=0:
              geoid=r[14]+r[15]+r[16]
              d[year][geoid] = {
                'white': float(r[0]),
                'latinx':float(r[1]),
                'black':float(r[2]),
                'nonhispanicwhite':float(r[3]),
                'nativeamerican':float(r[4]),
                'asian':float(r[5]),
                'income':float(r[6]),
                'population':float(r[7]),
                'pct_hs_grad':float(r[8]),
                'families_below_pov':float(r[9]),
                'unemployment':float(r[10]),
                'female_heads':float(r[11]),
                'pct_adults':float(r[12]),
                'public_assistance':float(r[13])
              }
              row={
                'white': float(r[0]),
                'latinx':float(r[1]),
                'black':float(r[2]),
                'nonhispanicwhite':float(r[3]),
                'nativeamerican':float(r[4]),
                'asian':float(r[5]),
                'income':float(r[6]),
                'population':float(r[7]),
                'pct_hs_grad':float(r[8]),
                'families_below_pov':float(r[9]),
                'unemployment':float(r[10]),
                'female_heads':float(r[11]),
                'pct_adults':float(r[12]),
                'public_assistance':float(r[13]),
                'geoid':geoid,
                'year':year
              }
              for key in row.keys():
                if key not in ['geoid','year']:
                  if row[key]<0:
                    row[key]='NA'
              row['pct_children']=100-row['pct_adults'] if row['pct_adults']!='NA' else 'NA'
              data.append(row)
        else:
          print(year,state,"error")
  df = pd.DataFrame(data)
  df.to_csv(OUTPUT_DIR+"census_data.csv")
  return d


def combine_data():
  df = pd.read_csv(OUTPUT_DIR+"census_data.csv")
  features=['pct_hs_grad','families_below_pov','unemployment','female_heads','pct_children','public_assistance']
  for col in features:
      df[col+"_zscore"]=(df[col] - df[col].mean())/df[col].std(ddof=0)
      df[col+"_binary"]=(df[col+"_zscore"]>df[col+"_zscore"].quantile(0.75)).astype(int)
  df['cdi_raw']=df[[x+"_binary" for x in features]].mean(axis=1)
  df['cdi']=(df["cdi_raw"]>df["cdi_raw"].quantile(0.75)).astype(int)
 
  articles=pd.read_csv(OUTPUT_DIR+"articles_with_everything.csv")
  articles['merge_year']=articles['year'].apply(lambda x: 2022 if x==2023 else x)

  df = df.rename(columns={'geoid':'geoid_x','year':'merge_year'})
  articles=articles.merge(df,on=['geoid_x','merge_year'],how='left',suffixes=('', '_updated'))
  articles.to_csv(OUTPUT_DIR+"articles_with_updated_census_data.csv",index=False)
  
  incidents=pd.read_csv(OUTPUT_DIR+"/incidents_with_ice.csv")
  incidents['merge_year']=incidents['year'].apply(lambda x: 2022 if x==2023 else x)
  incidents=incidents.merge(df,on=['geoid_x','merge_year'],how='left',suffixes=('', '_updated'))
  incidents.to_csv(OUTPUT_DIR+"incidents_with_updated_census_data.csv",index=False)
  


get_acs_data()

#combine_data()   
