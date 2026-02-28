import json
import os
import datetime
from config import *

def filter_matches(data):
  problems=[]
  filtered_data =[]
  mismatch=0  
  missing =0
  printed=0
  max_length=0
  count=0
  for d in data:
    d['article_id']=d['article_id'].strip()
    if len(d['article'])>max_length:
      max_length=len(d['article'])
    date1 = d['article_metadata']['date'].split("-")
    article= datetime.date(int("20"+date1[0]),int(date1[1]),int(date1[2]))
    #urls=[]
    #found_address=False
    if len(d['incident_metadata'])!=len(d['incident_ids']):
      count+=1
    #for i in d['incident_metadata']:
      #urls=urls+(i['source_url'])
    #  if i['address'].lower() in d['article'].lower() or i['place_name'].lower() in d['article'].lower():
    #    found_address=True
    incidents = []
#    if d['article_metadata']['mentions']['victims']==[] and d['article_metadata']['mentions']['shooters']==[] and not found_address: #d['article_metadata']['url'] not in urls:
 #     problems.append(d)
  #    missing+=1
    #else:
    for i in d['incident_metadata']:
      date2 = i['date'].split("-")
      incident = datetime.date(int(date2[0]),int(date2[1]),int(date2[2]))
      if article>=incident:
        incidents.append(i)
      else:
        print(article,d['article_id'], incident,i['id'])
    if len(incidents)>0:
      d['incident_metadata']=incidents
      filtered_data.append(d)
    else:
      mismatch+=1
        #print(d)
    #print(len(d['incident_metadata']),len(incidents))
  print("missing some incidents",count)
  print("mismatch,missing,correct",mismatch,missing,len(filtered_data))
  return filtered_data,problems


def write_json(data,year):
  filtered_data,problems = filter_matches(data)
  
  count =0
  print(len(data),len(filtered_data))
  path = OUTPUT_DIR+year+"/article_data"
  if not os.path.exists(path):
    os.makedirs(path)
  for d in filtered_data:
    with open(OUTPUT_DIR+year+"/article_data/"+d['article_id'].strip()+'.json','w') as outfile:
      json_obj = json.dumps(d,indent=4)
      outfile.write(json_obj)
      count +=1
  print(count)
