from collections import Counter
import re
import os
import json
from config import OUTPUT_DIR
import shutil
import pandas as pd


def get_notables():
  incidents=[]
  for y in range(2014,2024):
    year = str(y)
    directory = OUTPUT_DIR+year+'/article_data'
    if not os.path.exists(directory):
      continue
   
    print(year)
    all_incidents=[]
    
    for filename in os.listdir(directory):
      f = os.path.join(directory,filename)
      if os.path.isfile(f):
        with open(f,'r') as infile:
          d=json.load(infile)
          all_incidents+=d['incident_ids']
    all_incidents = [i for i in all_incidents if i not in ['589234','1755098','583473','1407045','1546656','1405325','1498150']]
    c = Counter(all_incidents)
    top = c.most_common(int(len(c)*.05))
    incidents+=[i[0] for i in top]
  
  with open(OUTPUT_DIR+'notable_ids.txt', 'w') as f:
    f.write('\n'.join(incidents))
  print(len(incidents))
  return incidents


def get_special_coverage():
  high_incidents=[]
  sustained_incidents=[]
  sustained=Counter()
  for y in range(2014,2024):
    year = str(y)
    directory = OUTPUT_DIR+year+'/article_data'
    if not os.path.exists(directory):
      continue
   
    print(year)
    shortterm=[]
    longterm=[]
    err=0
    
    for filename in os.listdir(directory):
      f = os.path.join(directory,filename)
      if os.path.isfile(f):
        with open(f,'r') as infile:
          d=json.load(infile)
          if len(d['incident_term'].get('short',[]))!=1:
            err+=1
            continue
          shortterm+=d['incident_term']['short']
          longterm+=d['incident_term'].get('med',[])
          longterm+=d['incident_term'].get('long',[])
    #all_incidents = [i for i in all_incidents if i not in ['589234','1755098','583473','1407045','1546656','1405325','1498150']]
    print(len(shortterm),len(longterm),err)
    longterm = [i for i in longterm if i in shortterm or i in high_incidents]
    high = Counter(shortterm)
    sustained.update(longterm)
    top_high = high.most_common(int(len(high)*.05))
    high_incidents+=[i[0] for i in top_high]
    #sustained_incidents+=[i[0] for i in top_sustained]
  
 # for elem,count in sustained.items():
  #  if count
  sustained = sustained-Counter(list(sustained.keys()))
  sustained_incidents=[i for i in sustained]
  #top_sustained = sustained.most_common(int(len(sustained)*.2))
  #sustained_incidents=[i[0] for i in top_sustained]
  with open(OUTPUT_DIR+'highcoverage_ids.txt', 'w') as f:
    f.write('\n'.join(high_incidents))
  with open(OUTPUT_DIR+'sustainedcoverage_ids.txt', 'w') as f:
    f.write('\n'.join(sustained_incidents))
  print(len(high_incidents), len(sustained_incidents))
  return high_incidents,sustained_incidents

def get_name_variants(name,ignorecase=False):
  names = [name]
  name = re.sub(r'photo by [A-Z][a-z]+ [A-Z][a-z]+',r'',name,re.IGNORECASE)
  name = re.sub(r'[A-Z][a-z]+ [A-Z][a-z]+\s*[/]\s*getty images',r'',name,re.IGNORECASE)
  names.append(re.sub(r'Deputy|Officer|Lt|Lt.|Dr|Dr.|Detective|Special Agent|Sgt|Sgt.',r'',name).strip())
  names.append(re.sub(r' [a-zA-Z][\.]? ',r' ',name).strip())
  n = name.split(" ")
  if '"' in name:
    if " aka " in name:
      aka = name.split('"')
      for m in aka:
        if ' aka ' not in m and len(m)>2:
          names.append(m)
    else:
      a=''
      found = False
      for m in n:
        if '"' in m:
          a = a+ re.sub(r'\"',r'',m)
          found = True
        elif found:
          a = a+ " " + m
      names.append(a)
  if len(n)==3 and n[2] not in ['Jr', 'Jr.', 'III', 'IV', 'II'] and n[0] not in ['Dr','Dr.','Lt','Lt.','Detective','Officer']:
    names.append(n[0]+" "+n[2])
  names = list(set(names))
  final_list=[]
  for n in names:
    n=n.strip()
    
    if len(n)>1 and len(n.split(" "))>1 and n.lower() not in ['store employee','security officer','police officer','security guard','corrections officer','not given','delivery driver','fbi agent','atf agent','swat officer','chp officer','unborn child','federal agent','unidentified suspect','dea agent','family dollar store','family dollar','shell gas station','circle k','rite aid','chase bank','special agent']:
      if not ignorecase:
        if n[0].lower()!=n[0]:
          final_list.append(n)
      else:
        final_list.append(n)
  #if len(list(filter(lambda name_piece: name_piece!='',name.split(" "))))<2:
   # print(name,final_list)
  return final_list

def write_matches(var_name):
  with open(OUTPUT_DIR+var_name+'_ids.txt','r') as f:
    notable = f.read().split('\n')
  incidents=[]
  primary_flat={}
  primary={}
  secondary={}
  counts=Counter()
  for y in range(2014,2024):
    year = str(y)
    directory = OUTPUT_DIR+year+'/article_data'
    if not os.path.exists(directory):
      continue

    print(year)
  with open(GVA_CSV,'r') as infile:
    reader = csv.DictReader(infile)
    for row in reader:
      incidents[row['id']]=row
      incidents[row['id']]['participants']=[]
  with open(GVA_PARTICIPANT_CSV,'r') as infile:
    reader=csv.DictReader(infile):
    for row in reader:
      incidents[row['id']]['participants'].append(row)
  print(len(incidents))
  for row in incidents:
    secondary[row['id']]=[row[key] for key in ['state','city','county','place_name'] if row[key]!='']
    incident_names=[]
    participants=[]
    for p in row['participants']:
      if p.get('name',None):
        participants.append(p['name'])
        names=[]
        variants = get_name_variants(p['name'])
        for v in variants:
          if len(v.split(" "))>1: 
            #names[v] = row['id']
            names.append(v)
        incident_names.append(names)
    if row.get('address',None) and len(row['address'])>7 and re.search('\d',row['address']) and re.search('\s',row['address']):
      incident_names.append([row['address']])
      participants.append(row['address'])
    primary[row['id']]=incident_names
    primary_flat[row['id']]=participants
  print(len(list(primary.keys())))
  data=[]
  skips=0
  nonskips=0
  for y in range(2014,2024):
    year = str(y)
    directory = OUTPUT_DIR+year+'/article_data'
    if not os.path.exists(directory):
      continue
    #year = str(y)
    print(year)
    print(skips,nonskips)
    directory = OUTPUT_DIR+year+'/article_data'
    for i,filename in enumerate(os.listdir(directory)):
      f = os.path.join(directory,filename)
      if os.path.isfile(f):
        d=None
        with open(f,'r') as infile:
          nonskips+=1
          d=json.load(infile)
          a = d['article'].lower()
          notables=[]
          notable_ids=[]
          for key in primary.keys():
            if key in d['incident_term']['short']:
              skips+=1
              continue
            
            found_match=False
            primary_matches = [any([" "+name.lower()+" " in a for name in options]) for options in primary[key]]
            num_matches=list(filter(lambda x: x,primary_matches))
            if len(num_matches)>1:
              found_match=True
            elif len(num_matches)==1 and any([place.lower() in a for place in secondary[key]]):
              found_match=True
            if found_match:
              notables+=[primary_flat[key][i] for i,n in enumerate(primary_matches) if n==True]
              notable_ids.append(key)
          notables = list(set(notables))
          notable_ids = list(set(notable_ids))
          counts.update(notable_ids)
          #if i<50 and len(notables)>0:
           # print(notables)
          d['article_metadata']['mentions'][var_name]=notables
          d['article_metadata']['mentions'][var_name+'_ids']=notable_ids
          data.append({
            'article_id':d['article_id'],
            'notables_mention':len(notables),
            'notables_mention_ids':notable_ids
          })
        #with open(f,'w') as outfile:
         # json_obj = json.dumps(d,indent=4)
          #outfile.write(json_obj)
  """
  d=[]
  for elem,c in counts.items():
    d.append({
      'id':elem,
      'count':c
    })
  df = pd.DataFrame(d)
  df.to_csv(OUTPUT_DIR+var_name+"_counts.csv",index=False)
  """
  df = pd.DataFrame(data)
  df.to_csv(OUTPUT_DIR+"notable.csv",index=False)
    
          
print(OUTPUT_DIR)
#get_special_coverage()
notable = get_notables()
with open(OUTPUT_DIR+'notable_ids.txt','r') as f:
  notable = f.read().split('\n')
  #print(len(notable))
#write_notables_to_folder(notable) 
#write_matches('sustainedcoverage') 
write_matches('notable')   

#from generate_csvs import get_article_info,get_incident_info
#get_article_info()
#get_incident_info()