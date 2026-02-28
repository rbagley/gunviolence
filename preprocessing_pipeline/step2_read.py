import re
import json
import csv
import os
import numpy as np
import pandas as pd
from collections import defaultdict
from utils import check_incident_dates,check_article_dates,check_source_dates
from config import *


def add_data(year,segment=None):
  incidents = {}
  articles = {}
 
  with open(GVA_CSV,'r') as infile:
    reader = csv.DictReader(infile)
    for row in reader:
      incidents[row['id']]=row
      incidents[row['id']]['participants']=[]
  with open(GVA_PARTICIPANT_CSV,'r') as infile:
    reader=csv.DictReader(infile):
    for row in reader:
      incidents[row['id']]['participants'].append(row)
  
  
      
#  print(year,str(int(year)-1))
 # directory = GVA_JSON_DIR
  #for y in [year,str(int(year)-1)]:
   # if int(y)>2013:
    #  print(y)
     # for i,filename in enumerate(os.listdir(directory+y)):
      #  f = os.path.join(directory+y,filename)
       # if os.path.isfile(f):
        #  with open(f,'r') as infile:
         #   d=json.load(infile)
          #  incidents[d['id']]=d
    print(len(incidents.keys()))

#  if not WITH_CENSUS_DATA:
 #   with open(GVA_DATA) as infile:
  #    csv_reader = csv.DictReader(infile)
   #   for row in csv_reader:
    #    if check_incident_dates(row['date']) and not no_participants(row):
     #     incidents[row['incident_id']] = row
#  else:
 #   with open(GVA_WITH_CENSUS) as infile:
  #    csv_reader = csv.DictReader(infile)
   #   for row in csv_reader:
    #    if check_incident_dates(row['date']) and not no_participants(row) and 'Non-Shooting Incident' not in row['incident_characteristics']:
     #     incidents[row['incident_id']] = row
  
  count = 0
  with open(OUTPUT_DIR+year+'/sorted_articles/'+ARTICLE_SUBSET+'.txt','r') as infile:
    for i,row in enumerate(infile):
      if segment==None or (segment!=None and i % INCREMENT==segment):# or (not segment):
        if row[0]=='@' and re.match(r'\d+',row[2:10].strip()):
          count += 1
          articles[row[2:].split()[0]] = {'article':row}
  print("# articles in group:",count)
  
  
#  directory = ARTICLE_DIR
 # for filename in os.listdir(directory):
  #  f = os.path.join(directory,filename)
   # if ("us" in filename or "US" in filename) and os.path.isfile(f) and check_article_dates(filename,year):
    #  with open(f,'r') as infile:
     #   for row in infile:
      #    article = articles.get(row[2:10].strip(),None)
       #   if article:
        #    d = filename.split("-")
         #   article['year'] = re.sub('text_','',d[0])
          #  article['month'] = d[1]
           # article['country'] = 'US'
            #articles[row[2:10].strip()] = article
  
#  for i in range (1,3):
 #   with open('/projects/b1170/corpora/byu_corpora/NOW/now_sources_pt'+str(i)+'.txt', errors='ignore') as infile:
  #    for row in infile:
   #     r = row.split('\t')
    #    if check_article_dates(r[2]) and articles.get(r[0],None):
     #     articles[r[0]]['metadata'] = r
  
     
  directory = ARTICLE_SOURCE_DIR
  for filename in os.listdir(directory):
    f = os.path.join(directory,filename)
    if os.path.isfile(f) and check_source_dates(filename,year):
      #print(f)
      with open(f, errors='ignore') as infile:
        for row in infile:
          r = row.split('\t')
          if articles.get(r[0],None) and r[3].lower()=='us':
            date = r[2].split("-")
            articles[r[0]]['year']=date[0]
            articles[r[0]]['month']=date[1]
            articles[r[0]]['country']=r[3]
            articles[r[0]]['metadata'] = r
  
  missing=0
  mismatch=0
  correct =0
  for key in articles.keys():
    a = articles[key]
    if a.get('metadata',None) and a.get('year',None):
      metadata = a['metadata']
      date = metadata[2]
      d = date.split("-")
      if d[0]!=a['year'] or d[1] != a['month'] or metadata[3].lower()!='us':
        print("mismatch",key, d[0], a['year'],d[1],a['month'],metadata[3])
        mismatch+=1
      else:
        correct+=1 
    else:
      print("missing",key)
      missing +=1
  print("Missing, mismatch,correct",missing,mismatch,correct)
  
  return incidents,articles

def no_participants(i):
  return i['participant_name']=='' and i['participant_gender']=='' and i['participant_type']==''