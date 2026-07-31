import pandas as pd
import re

import math

from config import *
print(OUTPUT_DIR)
import os
import json
import csv
from collections import defaultdict
import argparse

INCREMENT=4

IS_YEAR=True


def setup():
  
#from allennlp.predictors.predictor import Predictor
#import allennlp_models.tagging
  import spacy
  nlp = spacy.load('en_core_web_lg')
  from allennlp_models import pretrained
  #from allennlp_models.structured_prediction.predictors.srl import SemanticRoleLabelerPredictor
  print("a")
  predictor = pretrained.load_predictor('structured-prediction-srl-bert')
  #predictor = Predictor.from_path("https://storage.googleapis.com/allennlp-public-models/structured-prediction-srl-bert.2020.12.15.tar.gz")
  print("b")
  agency={}
  with open(lexicon_dir+"agency_power.csv",'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
      agency[row['verb']]={
        'agency': 1 if row['agency']=='agency_pos' else -1 if row['agency']=='agency_neg' else 0,
        'power': 1 if row['power']=='power_agent' else -1 if row['power']=='power_theme' else 0
      } 
  return predictor,agency

def score_verbs(victim,agent,verbs,counter):
  for verb in verbs:
    v=nlp(verb)[0]
    if agency.get(v.lemma_,None):
      if agent=='agent':
        counter[victim+"_agency"]+=agency[v.lemma_]['agency']
        if agency[v.lemma_]['agency']==1:
          counter[victim+'_high_agency']+=1
        counter[victim+"_agency_total"]+=1
        counter[victim+"_power"]+=agency[v.lemma_]['power']
        counter[victim+"_power_total"]+=1
      else:
        counter[victim+"_power"]+=(-1*agency[v.lemma_]['power'])
        counter[victim+"_power_total"]+=1
  return counter

def parse_commandline():
    """Parse the arguments given on the command-line.
    """
    
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--year",
                       help="year",
                       default=None)
    parser.add_argument("--segment",
                       help="segment",
                       default=None)

    args = parser.parse_args()
    year = int(args.year)  if IS_YEAR else 2014 + int(args.year)//INCREMENT
    
    segment = None if IS_YEAR else int(args.year) % INCREMENT
    return str(year),segment
    #segment = int(args.segment) if args.segment!=None else None
    #return str(args.year),segment


def run(year,segment,predictor,agency):
  print("D",year,segment)          
  data=[]
  counters={}
  arrays={}
  errors=0
  sents=[]
  ids=[]
  for index in range(0,4):
    if segment!=None and segment!=index: continue
    with open(masking_dir+"masked_names_"+year+"_"+str(index)+".csv",'r') as csvfile:
      reader = csv.DictReader(csvfile)
      for i,row in enumerate(reader):
        #if i>2000:
         # break
        if i%500==0:
          print(i)
        
        if 'victim' not in row['text'] and 'shooter' not in row['text'] and 'perpetrator' not in row['text'] and 'attacker' not in row['text'] and 'suspect' not in row['text'] and 'killer' not in row['text'] and 'murderer' not in row['text']:
          #counter = counters.get(row['article_id'],defaultdict(int))
          #counters[row['article_id']]=counter
          continue
        #sents=[]
        #if len(row['text'])>500:
         # doc = nlp(row['text'])
          #for s in doc.sents:
           # sents.append(s.text)
        #else:
         # sents.append(row['text'])
        #for s in sents:
        #try:
        sents.append(row['text'])
        ids.append(row['article_id'])
          #doc = nlp(row['text'])
          #for s in doc.sents:
          #  sents.append(s.text)
           # ids.append(row['article_id'])
            #predictions = predictor.predict_batch_json([{'sentence':s.text} for s in doc.sents]])
            #sentence=row['text'])]
  predictions=[]
  batch_size=100
  print(len(sents))
  for i in range(math.ceil(len(sents)/batch_size)):
    print(i)
    if i*batch_size>len(sents):
      continue
    subset = sents[i*batch_size:min(len(sents),(i+1)*batch_size)]
    try:
      predictions += predictor.predict_batch_json([{'sentence':s} for s in subset])
    except:
      for s in subset:
        try:
          predictions += predictor.predict_batch_json([{'sentence':s}])
        except:
          print(s)
          predictions+=[{'verbs':[]}]
  all=[]
  for i,pred in enumerate(predictions): 
    if i%1000==0:
      print(i) 
    v_a=False
    s_a=False
    v_p=False
    s_p=False
    arr=arrays.get(ids[i],{
        'v_agent':[],
        'v_patient':[],
        's_agent':[],
        's_patient':[]
        })
    new_arr={
        'v_agent':[],
        'v_patient':[],
        's_agent':[],
        's_patient':[]
        }
    counter = counters.get(ids[i],defaultdict(int))
    for v in pred['verbs']:
      t = v['description']
      agent = re.findall(r'\[ARG0: ([^\]]+)\]',t)
      patient = re.findall(r'\[ARG1: ([^\]]+)\]',t)
      for ag in agent:
        a= ag.lower()
        if 'victim' in a:
          arr['v_agent'].append(v['verb'])
          new_arr['v_agent'].append(v['verb'])
          v_a=True
        if 'shooter' in a or 'suspect' in a or 'perpetrator' in a or 'attacker' in a or 'killer' in a or 'murderer' in a:
          arr['s_agent'].append(v['verb'])
          new_arr['s_agent'].append(v['verb'])
          s_a=True
      for ag in patient:
        a=ag.lower()
        if 'victim' in a:
          arr['v_patient'].append(v['verb'])
          new_arr['v_patient'].append(v['verb'])
          v_p=True
        if 'shooter' in a or 'suspect' in a or 'perpetrator' in a or 'attacker' in a or 'killer' in a or 'murderer' in a:
          arr['s_patient'].append(v['verb'])
          new_arr['s_patient'].append(v['verb'])
          s_p=True
    counter['victim_obj']+=1 if v_p else 0 #len(arr['v_patient'])
    counter['victim_subj']+=1 if v_a else 0 #=len(arr['v_agent'])
    counter['shooter_obj']+=1 if s_p else 0 #=len(arr['s_patient'])
    counter['shooter_subj']+=1 if s_a else 0 #=len(arr['s_agent'])
    arrays[ids[i]]=arr
    counters[ids[i]]=counter
    
    c= defaultdict(int)
    c = score_verbs('victim','agent',new_arr['v_agent'],c)
    c = score_verbs('victim','patient',new_arr['v_patient'],c)
    c = score_verbs('shooter','agent',new_arr['s_agent'],c)
    c = score_verbs('shooter','patient',new_arr['s_patient'],c)
    obj={'article_id':ids[i],'sentence':sents[i]}
    for key in ['shooter_agency','shooter_power','victim_agency','victim_power']:
      obj[key]=c[key]
    all.append(obj)
  df = pd.DataFrame(all)
  seg = '' if segment==None else "_"+str(segment)
  df.to_csv(OUTPUT_DIR+"all_agency_power_"+year+seg+"_updated.csv",index=False)
  print(errors)    
  for c in counters:
    counter = counters[c]
    a=arrays.get(c)
    counter = score_verbs('victim','agent',a['v_agent'],counter)
    counter = score_verbs('victim','patient',a['v_patient'],counter)
    counter = score_verbs('shooter','agent',a['s_agent'],counter)
    counter = score_verbs('shooter','patient',a['s_patient'],counter)
    for a in ['shooter','victim']:
      for b in ['power','agency']:
        #print(counter[a+"_"+b])
        #print(counter[a+"_"+b+"_total"])
        if counter[a+"_"+b+"_total"]>0:
          counter[a+"_"+b]=counter[a+"_"+b]/counter[a+"_"+b+"_total"]
      counter[a+'_phrases']=counter[a+"_subj"]+counter[a+"_obj"]
    obj ={
      'article_id':c,
    }
    for a in ['shooter','victim']:
      for key in ['_subj','_obj','_agency','_power','_phrases','_high_agency']:
        obj[a+key]=counter[a+key]
    data.append(obj)
  print(len(data))
  df = pd.DataFrame(data)
  
  df.to_csv(OUTPUT_DIR+"agency_power_"+year+seg+"_updated.csv",index=False)

def run_plus_police(year,predictor=None,agency=None):         
  data=[]
  counters={}
  arrays={}
  errors=0
  sents=[]
  ids=[]
  infile = masking_dir+"masked_"+year+".csv" if IS_VIDEOS else masking_dir+"masked_sents_"+year+".csv"
  with open(infile,'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for i,row in enumerate(reader):
      if i%500==0:
        print(i)    
      if 'victim' not in row['text'] and 'shooter' not in row['text'] and 'perpetrator' not in row['text'] and 'attacker' not in row['text'] and 'suspect' not in row['text'] and 'killer' not in row['text'] and 'murderer' not in row['text'] and 'police_name' not in row['text'] and 'officer' not in row['text'] and 'agent' not in row['text'] and 'policeman' not in row['text']:
        continue
      tokens=row['text'].split(" ")
      if (len(tokens)>=6 and tokens[0]==tokens[1] and tokens[2]==tokens[3] and tokens[4]==tokens[5]) or (len(tokens)>6 and tokens[1]==tokens[2] and tokens[3]==tokens[4] and tokens[5]==tokens[6]):
        continue
      #doc = nlp(row['text'])
      #for s in doc.sents:
       # sents.append(s.text)
      sents.append(row['text'])
      ids.append(row['article_id'])
  predictions=[]
  batch_size=100
  print(len(sents))
  for i in range(math.ceil(len(sents)/batch_size)):
    print(i)
    if i*batch_size>len(sents):
      continue
    subset = sents[i*batch_size:min(len(sents),(i+1)*batch_size)]
    try:
      predictions += predictor.predict_batch_json([{'sentence':s} for s in subset])
    except:
      for s in subset:
        try:
          predictions += predictor.predict_batch_json([{'sentence':s}])
        except:
          print(s)
          predictions+=[{'verbs':[]}]
  all=[]
  for i,pred in enumerate(predictions): 
    if i%1000==0:
      print(i) 
    v_a=False
    s_a=False
    p_a=False
    v_p=False
    s_p=False
    p_p=False    
    new_arr={}
    arr1={}
    for person in ['v','s','p']:
      for role in ['agent','patient']:
        new_arr[person+"_"+role]=[]
        arr1[person+"_"+role]=[]
    arr=arrays.get(ids[i],arr1)
    counter = counters.get(ids[i],defaultdict(int))
    for v in pred['verbs']:
      t = v['description']
      agent = re.findall(r'\[ARG0: ([^\]]+)\]',t)
      patient = re.findall(r'\[ARG1: ([^\]]+)\]',t)
      for ag in agent:
        a= ag.lower()
        if 'victim' in a:
          arr['v_agent'].append(v['verb'])
          new_arr['v_agent'].append(v['verb'])
          v_a=True
        if 'police_name' in a or 'officer' in a or 'agent' in a or 'policeman' in a:
          arr['p_agent'].append(v['verb'])
          new_arr['p_agent'].append(v['verb'])
          p_a=True
        if 'shooter' in a or 'suspect' in a or 'perpetrator' in a or 'attacker' in a or 'killer' in a or 'murderer' in a:
          arr['s_agent'].append(v['verb'])
          new_arr['s_agent'].append(v['verb'])
          s_a=True
      for ag in patient:
        a=ag.lower()
        if 'victim' in a:
          arr['v_patient'].append(v['verb'])
          new_arr['v_patient'].append(v['verb'])
          v_p=True
        if 'police_name' in a or 'officer' in a or 'agent' in a or 'policeman' in a:
          arr['p_patient'].append(v['verb'])
          new_arr['p_patient'].append(v['verb'])
          p_p=True
        if 'shooter' in a or 'suspect' in a or 'perpetrator' in a or 'attacker' in a or 'killer' in a or 'murderer' in a:
          arr['s_patient'].append(v['verb'])
          new_arr['s_patient'].append(v['verb'])
          s_p=True
    counter['victim_obj']+=1 if v_p else 0 #len(arr['v_patient'])
    counter['victim_subj']+=1 if v_a else 0 #=len(arr['v_agent'])
    counter['shooter_obj']+=1 if s_p else 0 #=len(arr['s_patient'])
    counter['shooter_subj']+=1 if s_a else 0 #=len(arr['s_agent'])
    counter['police_obj']+=1 if p_p else 0
    counter['police_subj']+=1 if p_a else 0
    arrays[ids[i]]=arr
    counters[ids[i]]=counter
    
    c= defaultdict(int)
    c = score_verbs('victim','agent',new_arr['v_agent'],c)
    c = score_verbs('victim','patient',new_arr['v_patient'],c)
    c = score_verbs('shooter','agent',new_arr['s_agent'],c)
    c = score_verbs('shooter','patient',new_arr['s_patient'],c)
    c = score_verbs('police','agent',new_arr['p_agent'],c)
    c = score_verbs('police','patient',new_arr['p_patient'],c)
    obj={'article_id':ids[i],'sentence':sents[i]}
    for key in ['shooter_agency','shooter_power','victim_agency','victim_power','police_agency','police_power']:
      obj[key]=c[key]
    all.append(obj)
  df = pd.DataFrame(all)
  df.to_csv(OUTPUT_DIR+"all_agency_power_"+year+"_3groups.csv",index=False)
  print(errors)    
  for c in counters:
    counter = counters[c]
    a=arrays.get(c)
    counter = score_verbs('victim','agent',a['v_agent'],counter)
    counter = score_verbs('victim','patient',a['v_patient'],counter)
    counter = score_verbs('shooter','agent',a['s_agent'],counter)
    counter = score_verbs('shooter','patient',a['s_patient'],counter)
    counter = score_verbs('police','agent',a['p_agent'],counter)
    counter = score_verbs('police','patient',a['p_patient'],counter)
    for a in ['shooter','victim','police']:
      for b in ['power','agency']:
        #print(counter[a+"_"+b])
        #print(counter[a+"_"+b+"_total"])
        if counter[a+"_"+b+"_total"]>0:
          counter[a+"_"+b]=counter[a+"_"+b]/counter[a+"_"+b+"_total"]
      counter[a+'_phrases']=counter[a+"_subj"]+counter[a+"_obj"]
    obj ={
      'article_id':c,
    }
    for a in ['shooter','victim','police']:
      for key in ['_subj','_obj','_agency','_power','_phrases','_high_agency']:
        obj[a+key]=counter[a+key]
    data.append(obj)
  print(len(data))
  df = pd.DataFrame(data)
  
  df.to_csv(OUTPUT_DIR+"agency_power_"+year+"_3groups_updated.csv",index=False)
  
def combine_updated():
  dfs=[]
  for y in range(2014,2024):
    index=0
    year = str(y)
    df = pd.read_csv(OUTPUT_DIR+"agency_power_"+year+"_updated.csv")
    dfs.append(df)
  df = pd.concat(dfs)
  df = df[['article_id','victim_phrases','victim_high_agency','shooter_phrases','shooter_high_agency']]
  df = df.groupby('article_id').agg('sum')
  df['victim_agency_updated']=df['victim_high_agency']/df['victim_phrases']
  df['shooter_agency_updated']=df['shooter_high_agency']/df['shooter_phrases']
  df.to_csv(OUTPUT_DIR+"agency_updated.csv")
  
def combine_police():
  dfs=[]
  for y in range(2014,2024):
    year = str(y)
    try:
      df = pd.read_csv(OUTPUT_DIR+"agency_power_"+year+"_3groups_updated.csv")
      dfs.append(df)
    except:
      print("Missing", year)
  df = pd.concat(dfs)
  df = df[['article_id','victim_phrases','victim_high_agency','shooter_phrases','shooter_high_agency','police_phrases','police_high_agency']]
  df = df.groupby('article_id').agg('sum')
  df['victim_agency_updated']=df['victim_high_agency']/df['victim_phrases']
  df['shooter_agency_updated']=df['shooter_high_agency']/df['shooter_phrases']
  df['police_agency_updated']=df['police_high_agency']/df['police_phrases']
  df.to_csv(OUTPUT_DIR+"agency_police_updated.csv")
            
if __name__ == '__main__':
  predictor,agency = setup()
  #For command line variables
  """
  print("A")
  year,segment = parse_commandline()
  print("B")
  y = year+"_"+str(segment) if segment!=None else year
  
  """
  #With no command line variables:
  
  for y in range(2014,2018):
    year = str(y)
    run_plus_police(year, predictor,agency)
  
  #run(year,segment,predictor,agency)  
  #combine_updated()
  
  run_plus_police(year, predictor,agency)
  combine_police()  
  