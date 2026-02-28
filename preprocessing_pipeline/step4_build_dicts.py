from step4b_mentions import collect_mentions
from step4d_nlp_processing import process_text
from utils import get_address_variants,get_name_variants
#from add_census_data import get_census_data
import re
import csv
import numpy as np
import datetime
import json
from config import *

mismatches=[]

def create_data_structures(incidents,articles,matches):#,rev_matches):
  data = []
  num_incidents = []
  num_articles=[]
  missing = 0
  mismatch = 0
  errors=0
  timing=0
  no_short=0
  sources={}
  with open(SOURCE_CSV,'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
      sources[row['source']]=row
  print(len(articles.keys()))
  for i,key in enumerate(matches.keys()):
    if i%100==0:
      print(i)
    stripped_key = key.strip()
    #print(stripped_key,(not IS_VIDEOS and re.fullmatch(r'\d+',stripped_key)),articles.get(stripped_key,None) and articles[stripped_key].get('metadata',None))
    if (IS_VIDEOS or re.fullmatch(r'\d+',stripped_key)) and articles.get(stripped_key,None) and articles[stripped_key].get('metadata',None):
      date1 = articles[stripped_key]['metadata'][2].split("-") if not IS_VIDEOS else articles[stripped_key]['metadata']['date'].split("-")
      article_date= datetime.date(int("20"+date1[0]),int(date1[1]),int(date1[2]))
      
      parsed_incidents,e,term=parse_incident_metadata(incidents,matches[key],article_date)
      errors+=e
      if len(parsed_incidents)==0:
        timing+=1
        continue
      elif len(term.get('short',[]))<1:
        no_short+=1
        continue
      num_incidents.append(len(parsed_incidents))
      
      obj = {
        'incident_ids':[i['id'] for i in parsed_incidents],
        'incident_term':term,
        'article_id':key.strip(),
        'article_original': articles[stripped_key]['article'],
        'article_metadata':[],
        'incident_metadata':parsed_incidents
      } 
      text = obj['article_original']
      text = re.sub(r'<h>[ ]+<','<',text)
      text = re.sub(r'<p>[ ]+<','<',text)
      text = re.sub(r'<h>[ ]+Comments[ ]+<','<',text)
      text = re.sub(r'<h> \( \d \) comment[s]? <','<',text)
      text = text.strip()
      obj['article']=text
      obj['article_metadata']= parse_article_metadata(articles[stripped_key],obj['incident_metadata'],sources) if not IS_VIDEOS else parse_video_metadata(articles[stripped_key],obj['incident_metadata'],sources)
      obj['match_info']=get_match_info(obj)
      text = " ".join(obj['article'].split()[1:]).strip() if not IS_VIDEOS else obj['article'].strip()
      text = re.sub(" n\'t","n't",text)
      text = re.sub(" \'s","'s",text)
      text = re.sub("s \' ","s' ",text)
      text = re.sub(" \'re","'re",text)
      text = re.sub(" \'ve","'ve",text)
      text = re.sub(" \'d","'d",text)
      text = re.sub(" \. ",". ",text)
      text = re.sub(" , ",", ",text)
      text = re.sub("> >",">>",text)
      sents = re.split("@ @ @ @ @ @ @ @ @ @|<p>|<h>",text) if not IS_VIDEOS else re.split(">>",text)
      obj['article_metadata']['clean_pieces']=[s for s in sents if s!='']
      if len(matches[key])>12: print("lots of matches",key)
      if len(obj['incident_metadata'])>0:
        data.append(obj)
      else: 
        mismatch+=1
    else:
      missing+=1
      print("MISSING",stripped_key)
  print("timing errors:",errors)
  print("timing examples:",mismatches[:15] if len(mismatches)>15 else mismatches)
  print("data structures missing, mismatch, no incidents, no shortterm, valid",missing,mismatch,timing,no_short,len(data))
  #for key in rev_matches.key:
  #  num_articles.append(len(rev_matches[key]))
  print(np.mean(num_incidents),np.median(num_incidents),max(num_incidents))
  return data

def get_match_info(obj):
  matches={
    'url_match':False,
    'address_match':False,
    'name_match':False
  }
  verbose = False#(obj['article_id'] in ['2077942','2225977'])
  if verbose: print(len(obj['incident_metadata']))
  for i in obj['incident_metadata']:
    if i['id'] not in obj['incident_term']['short']:
      if verbose: print("skipping ", i['id'])
      continue
    if verbose: print("trying to match")
    if obj['article_metadata']['url'] in i['sources']:
      if verbose: print("found url")
      matches['url_match']=True
    if len(i['address'])>7 and re.search('\d',i['address']) and re.search('\s',i['address']):
      addresses = get_address_variants(i['address'])
      if any([" "+a.lower()+" " in obj['article'].lower() for a in addresses]):
        if verbose: print("found address")
        matches['address_match']=True
    for p in i['participants']:
      if p.get('name',None):
        variants = get_name_variants(p['name'],True)
        if verbose: print(variants)
        for v in variants:
          if verbose: print(v,len(v.split(" "))>1, v.lower() in obj['article'].lower())
          if len(v.split(" "))>1 and v.lower() in obj['article'].lower():
            matches['name_match']=True
            if verbose: print("found name")
  if all(matches[key]==False for key in matches.keys()):
    print(verbose, obj['article_id'])
  return matches
          
  
def parse_article_metadata(article,incidents,sources):
  data=article['metadata']
  text = article['article']
  #doc,lemmas = process_text(text)
  mentions,lemmas,sentences = collect_mentions(text,incidents)
  sentences = list(filter(lambda x: len(x)>2,sentences))
  return {
    'id':data[0].strip(),
    'date':data[2],
    'news_source':sources.get(data[4],{'source':data[4]}),
    'url':data[5],
    'headline':data[6],
    'mentions':mentions,
    'sentences':sentences,
    #'spacy':doc,
    'lemmas':lemmas
  }

def parse_video_metadata(article,incidents,sources):
  data=article['metadata']
  text = article['article']
  #print(data)
  mentions,lemmas,sentences = collect_mentions(text,incidents)
  sentences = list(filter(lambda x: len(x)>2,sentences))
  data['mentions']=mentions
  data['lemmas']=lemmas
  data['sentences']=sentences
  #data['news_source']=[]
  #doc,lemmas = process_text(text)
  #data['mentions']=collect_mentions(text,incidents,lemmas)
  #data['lemmas']=lemmas
  return data
  {
    'id':data[0].strip(),
    'date':data[2],
    'news_source':sources.get(data[4],{'source':data[4]}),
    'url':data[5],
    'headline':data[6],
    #'mentions':collect_mentions(text,incidents,lemmas),
    #'spacy':doc,
    'lemmas':lemmas
  }

def parse_incident_metadata(incident_dict,data_list,article_date):
  incidents = []
  errors=0
  term={}
  if len(list(set(data_list)))==0:
    print("problem")
  for d in list(set(data_list)):
    data = incident_dict[d]
    date2 = data['date'].split("-")
    incident = datetime.date(int(date2[0]),int(date2[1]),int(date2[2]))
    diff = (article_date-incident).days
    if article_date>=incident and diff<TIMEFRAME:
      incidents.append(data)
      if diff<=7:
        t = 'short'
      elif diff<45:
        t='med'
      else:
        t='long'
      arr = term.get(t,[])
      arr.append(data['id'])
      term[t]=arr
    else:
      mismatches.append(data['id'])
      errors+=1
    #data['incident_characteristics']=data['incident_characteristics'][0].split("||")
    #if WITH_CENSUS_DATA:
    #  try:
    #    data['white']=get_census_data(data)
    #  except:
    #    data['white']='error'
    #    errors+=1
    #incidents.append(data)
  return incidents,errors,term

def parse_incident_metadata_old(incident_dict,data_list):
  incidents = []
  for d in data_list:
    data = incident_dict[d]
    obj = {
      'id': data['incident_id'],
      'date': data['date'],
      'state': data['state'],
      'city_or_county' : data['city_or_county'],
      'address': data['address'],
      'n_killed': data['n_killed'],
      'n_injured': data['n_injured'],
      'incident_url': data['incident_url'],
      'source_url': data['sources'].split("||"),
      'latitude': data['latitude'],
      'longitude': data['longitude'],
      'incident_characteristics': data['incident_characteristics'].split("||"),
      'notes': data['notes'],
      'guns': parse_gun_data(data),
      'participants':parse_participants(data),
      'districts':{
        'congressional':data['congressional_district'],
        'state_house':data['state_house_district'],
        'state_senate':data['state_senate_district']
      }
    }
    if WITH_CENSUS_DATA:
      obj['geoid']=data['geoid']
      obj['white']=get_census_data(data)
    incidents.append(obj)
  return incidents
  
def parse_info(p,length):
  d = p.split("::")
  if len(d)<2: 
    d=p.split(":")
  if len(d)<2 or int(d[0])>=length:
    print(p,length)
  return d

def parse_participants(data):
  divider = "|" if len(data['participant_type'].split("||"))==1 and len(data['participant_type'].split("|"))>1 else "||"
  participants = [{} for i in range(len(data['participant_type'].split(divider)))]
  if data['participant_type']!='':
    for p in data['participant_type'].split(divider):
      d = parse_info(p,len(participants))
      participants[int(d[0])]['type'] = d[1]
  if data['participant_age']!='':
    for p in data['participant_age'].split(divider):
      d = parse_info(p,len(participants))
      participants[int(d[0])]['age'] = d[1]
  if data['participant_age_group']!='':
    for p in data['participant_age_group'].split(divider):
      d = parse_info(p,len(participants))
      participants[int(d[0])]['age_group'] = d[1]
  if data['participant_gender']!='':
    for p in data['participant_gender'].split(divider):
      d = parse_info(p,len(participants))
      participants[int(d[0])]['gender'] = d[1]
  if data['participant_status']!='':
    for p in data['participant_status'].split(divider):
      d = parse_info(p,len(participants))
      participants[int(d[0])]['status'] = d[1]
  if data['participant_relationship']!='':
    for p in data['participant_relationship'].split(divider):
      d = parse_info(p,len(participants))
      participants[int(d[0])]['relationship'] = d[1]
  if data['participant_name']!='':
    for p in data['participant_name'].split(divider):
      d = parse_info(p,len(participants))
      participants[int(d[0])]['name'] = d[1]
  return participants
  

def parse_gun_data(data):
  guns = []
  if data['n_guns_involved']:
    for i in range(int(data['n_guns_involved'])):
      guns.append({})
  if data['gun_type']:
    types = data['gun_type'].split("||")
    if len(types)==1:
      types = data['gun_type'].split("|")
    for g in types:
      t = parse_info(g,len(guns))
      guns[int(t[0])]['type'] = t[1]
  if data['gun_stolen']:
    stolen = data['gun_stolen'].split("||")
    if len(stolen)==1:
      stolen = data['gun_stolen'].split("|")
    for s in stolen:
      t = parse_info(g,len(guns))
      guns[int(t[0])]['stolen'] = t[1]
  return guns