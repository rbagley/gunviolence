print("A")
import pandas as pd
from collections import Counter,defaultdict
import datetime
#from scipy.special import softmax
#from notable import get_name_variants
print("B")
import os
import csv
import json
import re
import numpy as np
from race import get_race
from urllib.parse import urlparse
import argparse

from config import *



print(masking_dir)
print("C")

singular_nouns=['prisoner','teen','worker','member','kid','lawyer','victim','officer','wife','american','neighbor','male','population','person','cop','woman','family','boy','girl','mother','daughter','son','father','man','suspect','resident','teenager','parent','child','leader','female','people','women','men','families','children']

filtered_race_nouns=singular_nouns+[x+"s" for x in singular_nouns if x not in ['wife','population','person','woman','man','family','child','people','women','men','families','children']]

legal_keywords=['judge','lawyer','attorney','bailiff','court','courthouse','lawsuit','bail','appeal','arraignment','accused','warrant','felony','conviction','evidence','defendant','jury','parole','parolee','plaintiff','prosecutor','witness']

def get_domain(url):
  a = urlparse(url)
  return re.sub(r'^www\.','',a.netloc)

def get_counts(text,keywords):
  return len([x for x in keywords if x in text.lower().split(" ")])
  
def get_article_info(initial=False,with_ling_features=False):
  inc_df= pd.read_csv(OUTPUT_DIR+"incidents.csv")
  notable_df = inc_df[inc_df['notable']>0][['id','year','month','day']]
  notable_df['date']=notable_df.apply(lambda x: datetime.datetime(x['year'],x['month'],x['day']),axis=1)
  inc_df = inc_df[inc_df['n_killed']>3][['id','year','month','day','metro_area']]
  inc_df['date']=inc_df.apply(lambda x: datetime.datetime(x['year'],x['month'],x['day']),axis=1)
  data=[]
  errors=0

  for y in range(2014,2024):
    year = str(y)
    print(year)
    directory = OUTPUT_DIR+year+'/article_data'
    if not os.path.exists(directory):
      continue
    sent_counts=defaultdict(list)
    with open(masking_dir+"masked_sentences_"+year+".csv",'r') as csvfile:
      reader=csv.DictReader(csvfile)
      for row in reader:
        sent_counts[row['article_id']].append(row['text'])
    count1=0
    count2=0
    
    
    for file_count,filename in enumerate(os.listdir(directory)):
      count1+=1
      if file_count%500==0: 
        print(file_count)
      f = os.path.join(directory,filename)
      if os.path.isfile(f):
        with open(f,'r') as infile:
          d=json.load(infile)
          if len(d['incident_term']['short'])!=1:
            continue
          count2+=1
          obj={}
          white=[]
          shooters=0
          named_shooters=0
          named_victims=0
          victims=0
          days_since=[]
          about=[]
          date=d['article_metadata']['date'].split("-")
          primary_id=None
          art_date=datetime.date(int("20"+date[0]),int(date[1]),int(date[2]))  
          pd_art_date = pd.Timestamp(art_date)
          for index,i in enumerate(d['incident_metadata']):
            for p in i['participants']:
              if p.get('type',None):
                if p['type']=='victim':
                  victims+=1
                  if p.get('name',None):
                    named_victims+=1
                else:
                  shooters+=1
                  if p.get('name',None):
                    named_shooters+=1
            if i['id'] not in d['incident_term']['short']:
              continue
            date2 = i['date'].split("-")
            inc_date = datetime.date(int(date2[0]),int(date2[1]),int(date2[2]))
            diff = (art_date-inc_date).days
            days_since.append(diff)
            if i['white']!='NA' and i['white']!='error' and float(i['white'])>=0:
              white.append(float(i['white']))
            about.append(d['article_metadata']['mentions']['aboutness'][index])
            primary_id=i['id']
          filtered_notables = [n for n in d['article_metadata']['mentions']['notable_ids'] if n not in d["incident_term"]['short'] + d['incident_term'].get('med',[])]
          obj['notable_mention']=len(filtered_notables)
          for feature in ['race','policy','police','speakers','children','family','movement','legal','bias','hedging','death','medical']:
            obj[feature+"_mention"]=len(d['article_metadata']['mentions'][feature])
          obj['policy_plus_mention']=obj['policy_mention']+len([x for x in d['article'].split(" ") if x.lower() in ['policy','policies']])
          obj['length']=len(d['article'].split())
          obj['death_filtered_mention']=len([d for d in d['article_metadata']['mentions']['death'] if any([x for x in ['suicide','murder','manslaughter','slaughter','coroner','autopsy','fatal','execution','morgue','homicide','corpse','lethal','casualty','doa','pronounce','heartbeat'] if x in d])])
          obj['subjective_death_mention']=len([d for d in d['article_metadata']['mentions']['death'] if not any([x for x in ['suicide','murder','manslaughter','slaughter','coroner','autopsy','fatal','execution','morgue','homicide','corpse','lethal','casualty','doa','pronounce','heartbeat'] if x in d])])
          obj['death_mention']=len(d['article_metadata']['mentions']['death'])
          obj['intentional_death_mention']=len([d for d in d['article_metadata']['mentions']['death'] if any([x for x in ['murder','slaughter','homicide','kill','killing','massacre','killed'] if x in d])])
          obj['objective_death_mention']=len([d for d in d['article_metadata']['mentions']['death'] if d not in ['grief','grieve','grieving','grieved','mourn','mourning','mourned','bereave','bereaved','funeral','funerals','grieves','mourns']])
          
          obj['implicit_race_orig_mention']= get_counts(d['article'],['thug','thuggery','thugs','gang','gangs','gangsters','gangster','gangbanger','gangbangers','gangbanging'])
          obj['implicit_race_mention']= get_counts(d['article'],['thug','thuggery','thugs','gang','gangs','gangsters','gangster','gangbanger','gangbangers','gangbanging','terrorist','terrorists'])
          obj['innocent_mention']= get_counts(d['article_metadata']['lemmas'],['innocent','innocence'])
          obj['guilty_mention']= get_counts(d['article_metadata']['lemmas'],['guilt','guilty'])
          obj['blame_mention']=obj['innocent_mention']+obj['guilty_mention']
          obj['police_nonperson_mention']=get_counts(d['article_metadata']['lemmas'],['crime','arrest','handcuff'])+len([x for x in ['crime scene', 'scene of the crime','on the scene'] if x in d['article']])
          obj['criminal_mention']= get_counts(d['article_metadata']['lemmas'],['criminal'])
          obj['criminality_mention']= get_counts(d['article_metadata']['lemmas'],['criminal','guilt','guilty'])
          obj['ordinary_police_mention']=get_counts(d['article_metadata']['lemmas'],['officer','policeman','policewoman','cop','patrol','trooper','corporal'])
          obj['special_police_mention']=get_counts(d['article_metadata']['lemmas'],['sheriff','deputy','detective','captain','lieutenant','investigator'])
          obj['legal_expanded_mention']=get_counts(d['article_metadata']['lemmas'],legal_keywords)+int('public defender' in d['article_metadata']['lemmas'])
          obj['gun_violence_mention']=d['article_metadata']['lemmas'].lower().count('gun violence')
          #1 if 'gun violence' in d['article_metadata']['lemmas'].lower() else 0
          mental=[x for x in d['article_metadata']['mentions']['mental_health'] if x not in ['insane','crazy','addict','addiction']]
          obj['mental_health_mention']= len(mental)
          obj['person_race_mention']=len([n for n in d['article_metadata']['mentions']['race'] if any([k in n.lower().split() for k in filtered_race_nouns])])
          obj['white_mention']=len([r for r in d['article_metadata']['mentions']['race'] if ('white' in r.lower() or 'caucasian' in r.lower())])
          obj['nonwhite_mention']=len([r for r in d['article_metadata']['mentions']['race'] if ('white' not in r.lower() and 'caucasian' not in r.lower())])
          obj['gang_label_mention']=len([x for x in d['article'].split(" ") if x.lower() in ['gang','gangs','gangsters','gangster','gangbanger','gangbangers','gangbanging']])
          obj['suicide_label_mention']=len([x for x in d['article'].split(" ") if x.lower() in ['suicide']])
          obj['dv_label_mention']= len([x for x in ['domestic violence','spousal abuse','intimate partner violence'] if x in d['article'].lower()])
          obj['drug_label_mention']=len([x for x in d['article'].split(" ") if x.lower() in ['drug','drugs']])
          obj['mass_label_mention']=len([x for x in ['mass murder','mass killing','mass shooting'] if x in d['article'].lower()])
          obj['mass_shooting_label_mention']=len([x for x in ['mass shooting'] if x in d['article'].lower()])
          obj['hate_crime_label_mention']=len([x for x in ['hate crime','hate crimes'] if x in d['article'].lower()])
          obj['accident_label_mention']=len([x for x in d['article'].split(" ") if x.lower() in ['accident','accidents','accidental']])
          
          
          rename={
            'shooters_set':'shooters_mention',
            'victims_set':'victims_mention',
            'gangs':'gang_mention',
            'organizations':'organization_mention',
            'victims':'all_victim_mentions',
            'shooters':'all_shooter_mention',
            'nameless_victims':'nameless_victim_mention',
            'nameless_shooters':'nameless_shooters'
          }
          for key, new_name in rename.items():
            obj[new_name]=len(d['article_metadata']['mentions'][key])
          
          obj['sents_shooter_mention']=len([x for x in sent_counts[d['article_id']] if 'shooter_name' in x])
          obj['sents_police_mention']=len([x for x in sent_counts[d['article_id']] if ('officer' in x or 'policeman' in x or 'policewoman' in x or 'cop' in x)])
          obj['sents_policeparticipant_mention']=len([x for x in sent_counts[d['article_id']] if 'police_name' in x])
          obj['sents_victim_mention']=len([x for x in sent_counts[d['article_id']] if 'victim_name' in x])
            
          obj['blm_mention']=len([r for r in d['article_metadata']['mentions']['movement'] if 'blm' in r.lower()])
          
          obj['pct_shooters']=len(d['article_metadata']['mentions']['shooters_set'])/named_shooters if named_shooters!=0 else 1
          obj['pct_victims']=len(d['article_metadata']['mentions']['victims_set'])/named_victims if named_victims!=0 else 1
          obj['named_victims']=named_victims
          obj['named_shooters']=named_shooters
          if len(d['article_metadata']['mentions']['victims_set'])> named_victims:
            print(d['article_metadata']['mentions']['victims_set'], d['article_id'])
          obj['about']=np.mean(about)
          obj['sent_count']=len(d['article_metadata']['sentences'])
          obj['pct_about']=np.mean(about)/len(d['article_metadata']['sentences'])
          obj['mean_about']=np.mean(d['article_metadata']['mentions']['aboutness'])
          obj['total_about']=sum(d['article_metadata']['mentions']['aboutness'])
          obj['num_shooters']=shooters
          obj['num_victims']=victims
          obj['num_incidents']=len(d['incident_ids'])
          for match_type in ['url_match','name_match','address_match']:
            obj[match_type]=d["match_info"][match_type]
          if len(white)>0:
            obj['max_white']=max(white)
            obj['min_white']=min(white)
            obj['avg_white']=np.mean(white)
            a=obj
          else:
            a=None
          if a!=None:
            source=d['article_metadata']['news_source']
            if source!=[] and type(source) is not str and source.get('state',None):
              state = source['state'] if source['zip code']=='no data' or (len(source['zip code'])==5 and source['zip code'] not in ['Maine','Idaho','Texas']) else source['zip code']
              a['source_state']=state
              a['source_city']=source['city'] if state==source['state'] else source['state']
              a['source_scope']=source['scope']
              a['source']=source['source']
              for key in ['source_state','source_city','source_scope']:
                if a[key]=='no data':
                  a[key]='NA'
            else:
              a['source_state']='NA'
              a['source_city']='NA'
              a['source_scope']='NA'
              a['source']=source if type(source) is str else source.get('source','NA')
            a['url']=d['article_metadata']['url']
            a['date']=d['article_metadata']['date']
            date=a['date'].split("-")
            a['year']=int("20"+date[0])
            a['month']=int(date[1])
            a['day']=int(date[2])
            a['incident_ids']=','.join(d['incident_ids'])
            a['primary_incident_id']=primary_id
            a['shortterm']=len(d['incident_term']['short'])
            a['medterm']=len(d['incident_term'].get('med',[]))
            a['longterm']=len(d['incident_term'].get('long',[]))
            a['dayssince']=np.mean(days_since)
            #a['days_since_major'] = days_since_maj
            #a['days_since_notable'] = days_since_notable
            #a['recent_local'] = recent_local
            a['id']=d['article_id']
            data.append(a)
            #if np.sum(d['article_metadata']['mentions']['aboutness'])<2 and a['dayssince']>30:
             # maybe+=1
              #if len(examples)<25:
               # examples.append(d['article_id'])
          else:
            errors+=1
    print(count1,count2)
    print(len(data))
    #print(maybe)
    #print(examples)
  df = pd.DataFrame(data)
  print(df.shape)
  print(errors)
  print(df.columns)
  df.to_csv(OUTPUT_DIR+"articles.csv",index=False)

def incident_chars(chars):
    return {
      'suicide': 1 if 'Suicide' in chars else 0,
      'officer': 1 if 'Officer Involved' in chars else 0,
      'drug': 1 if 'Drug' in chars else 0,
      'gang': 1 if 'Gang' in chars else 0,
      'school': 1 if 'School' in chars else 0,
      'mass': 1 if 'Mass' in chars else 0,
      'accident':1 if 'Accident' in chars else 0,
      'assaultweapon':1 if 'Assault weapon' in chars else 0,
      'child':1 if 'Child' in chars else 0,
      'domestic_violence':1 if 'Domestic Violence' in chars else 0,
      'defensive':1 if 'Defensive' in chars else 0,
      'hate_crime':1 if 'Hate crime' in chars else 0,
      'home_invasion':1 if 'Home Invasion' in chars else 0,
    }

def get_incident_info(initial=False):
  df = pd.read_csv(GVA_INCIDENT_CSV)
  inc_df = df[df['n_killed']>3]
  inc_df['days_since_2010']=inc_df['date'].apply(lambda x: (pd.Timestamp(x)-pd.Timestamp(year=2010,month=1,day=1)).days)
  source_dict={}
  
  
  with open(OUTPUT_DIR+'notable_ids.txt','r') as f:
    notable = f.read().split('\n')  
  if not initial:
    df = pd.read_csv(OUTPUT_DIR+"articles.csv")
    df=df.rename(columns={'id':'article_id'})
    df = df[df['shortterm']==1]
    ids = [str(i) for i in list(df['article_id'])]
    df=df.set_index('article_id')
  incidents={}
  probs=0
  for y in range(2014,2024):
    year = str(y)
    print(year)
    directory = OUTPUT_DIR+year+'/article_data'
    if not os.path.exists(directory):
      continue
    for filename in os.listdir(directory):
      f = os.path.join(directory,filename)
      if os.path.isfile(f) and re.sub('.json','',filename) in ids:
        with open(f,'r') as infile:
          d=json.load(infile)
          id = int(d['article_id'])
          if not initial:
            sent_count = list(df.loc[[id]]['sent_count'])[0]
          if sent_count==0: 
            probs+=1
            print('prob')
            continue
          date=d['article_metadata']['date'].split("-")
          art_date=datetime.date(int("20"+date[0]),int(date[1]),int(date[2]))
          for index,i in enumerate(d['incident_metadata']):
            inc = incidents.get(i['id'],None)
            if not inc:
              inc = i
              for f in ['count','local','wider','unknown_source','national','notable_mentions','shortterm','medterm','longterm']:
                 inc[f]=0
              for f in ['about','num_incidents','article_ids','article_len','article_share','dayssince','race_mention']:
                 inc[f]=[]
            inc['count']+=1
            inc['about'].append(d['article_metadata']['mentions']['aboutness'][index]/sent_count)
            inc['race_mention'].append(1 if len(d['article_metadata']['mentions']['race'])>0 else 0)
            inc['article_ids'].append(d['article_id'])
            inc['article_len'].append(len(d['article'].split(" ")))
            inc['num_incidents'].append(len(d['incident_metadata']))
            inc['article_share'].append(len(d['article'].split(" "))/len(d['incident_metadata']))
            date2 = i['date'].split("-")
            inc_date = datetime.date(int(date2[0]),int(date2[1]),int(date2[2]))
            diff = (art_date-inc_date).days
            inc['dayssince'].append(diff)
            if diff<=7:
              inc['shortterm']+=1
            elif diff<45:
              inc['medterm']+=1
            else:
              inc['longterm']+=1
            source= d['article_metadata']['news_source']
            if type(source) is not str and source.get('state',None):
              state = source['state'] if source['zip code']=='no data' or (len(source['zip code'])==5 and source['zip code'] not in ['Maine','Idaho','Texas']) else source['zip code']
              if source['scope']=='National':
                inc['national']+=1
              elif state!=inc['state']:
                inc['wider']+=1
              else:
                inc['local']+=1         
            else:
              inc['unknown_source']+=1 
            incidents[i['id']]=inc
  print(probs)
  data=[]
  for key in incidents.keys():
    i = incidents[key]
    chars = ' || '.join(i['incident_characteristics'])
    named=0
    named_vic=0
    named_perp=0
    all=0
    female_part=0
    female_vict=0
    for p in i['participants']:
      all+=1
      if p.get('name',None):
        named+=1
        if p.get('type',None) and p['type']=='victim':
          named_vic+=1
        elif p.get('type',None)!=None:
          named_perp+=1
      if p.get('gender',None) and p['gender']=='female':
        female_part+=1
        if p.get('type',None) and p['type']=='victim':
          female_vict+=1
    
    supermajority,majority,plurality = get_race(i)
    comparable = any([a in i['metro_area'] for a in ['Santa Fe','San Francisco','Denver','Birmingham','Las Vegas','Boston','Orlando','Portland']])
    
    obj={
      'month':int(i['date'].split("-")[1]),
      'day':int(i['date'].split("-")[2]),
      'notable_mention':i['notable_mentions'],
      'wider_local':i['wider'],
      'n_killedtract':death.get(i['geoid'],0),
      'n_participants':len(i['participants']),
      'pct_named':named/all,
      'named_vics':named_vic,
      'named_perp':named_perp,
      'income': i['income'] if (i['income']=='NA' or float(i['income'])>=0) else 'NA',
      'comparable_city': comparable,
      'race_majority':majority,
      'race_plurality':plurality,
      'race_supermajority':supermajority,
      'about':np.mean(i['about']),
      'dayssince':np.mean(i['dayssince']),
      'race_mention':np.mean(i['race_mention']),
      'notable':1 if i['id'] in notable else 0,
      'num_characteristics': len(i['incident_characteristics']),
      'article_ids':','.join(i['article_ids']),
      'article_len':np.mean(i['article_len']),
      'article_share':np.mean(i['article_share']),
      'num_incidents':np.mean(i['num_incidents']),
      'female_participants':female_part,
      'female_victims':female_vict
    }
    for f in ['id','date','year','geoid','count','local','national','unknown_source','state','city','n_killed','n_injured','white','black','latinx','nonhispanicwhite','nativeamerican','asian','density','recent_death','metro_area','detroit','milwaukee','shortterm','medterm','longterm']:
        obj[f]=i[f]

    obj.update(incident_chars(chars))
    pd_art_date = (pd.Timestamp(year=int(obj['year']),month=obj['month'],day=obj['day'])-pd.Timestamp(year=2010,month=1,day=1)).days
    diff = inc_df[inc_df['days_since_2010']<=pd_art_date]['days_since_2010']
    obj['days_since_maj'] = pd_art_date-diff.max() if len(diff)>0 else 'NA'

    data.append(obj)
  df = pd.DataFrame(data)
  df.to_csv(OUTPUT_DIR+'incidents.csv',index=False)
  
  
  df = df[df['article_len']<=2000]
  df = df[df['article_len']>=50]
  df = df[(df['nonhispanicwhite']<=40) | (df['nonhispanicwhite']>=60)]
  
  df['since2020']=(df['year']>2019).astype(int)
  df['white_binary']=(df['nonhispanicwhite']>50).astype(int)
  df['national_binary']=(df['national']>0).astype(int)
  df['binary_count']=(df['count']>1).astype(int)
  df['no_named']=(df['pct_named']==0).astype(int)
  df['some_named']=(df['pct_named']>0).astype(int)
  df['no_victims']=(df['num_victims']==0).astype(int)
  df['no_death']=(df['n_killed']==0).astype(int)
  df['mass_death']=(df['n_killed']>=4).astype(int)
  df.to_csv(OUTPUT_DIR+'incidents_for_coverage_regression.csv',index=False)
  print(df.shape)
  
def all_incident_info():
  df = pd.read_csv(GVA_INCIDENT_CSV)
  inc_df = df.copy()
  inc_df = inc_df[inc_df['n_killed']>3]
  inc_df['days_since_2010']=inc_df['date'].apply(lambda x: (pd.Timestamp(x)-pd.Timestamp(year=2010,month=1,day=1)).days)
  
  with open(OUTPUT_DIR+'notable_ids.txt','r') as f:
    notable = f.read().split('\n') 
  mentioned_article={}

  article_national={}
  article_len={}

  checking=0
  with open(OUTPUT_DIR+'/incidents.csv','r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
      row['id']=int(row['id'].strip())
      if int(row['count'])>0: checking+=1
      mentioned_article[row['id']]=int(row['count'])
      article_national[row['id']]=int(row['national'])
      article_len[row['id']]=float(row['article_len'])
  print(checking)
 
  data=[]
  data_dict={}
  print(len(mentioned_article.keys()))
  print("reading incidents")
  with open(GVA_INCIDENT_CSV,'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for index,i in enumerate(reader):
      if index%10000==0:
        print(index)
      i['id']=int(i['id'].strip())
      supermajority,majority,plurality = get_race(i)
      date = i['date'].split("-")
      chars = i['incident_characteristics']
      try:
        art_date=datetime.date(int(i['year']),int(date[0]),int(date[1]))  
      except:
        print(date)
      pd_art_date = (pd.Timestamp(art_date)-pd.Timestamp(year=2010,month=1,day=1)).days
      diff = inc_df[inc_df['days_since_2010']<=pd_art_date]['days_since_2010']
      days_since_maj = pd_art_date-diff.max() if len(diff)>0 else 'NA'
      
      obj={
        'year':int(i['year']),
        'month':int(date[1]),
        'day':int(date[2]),
        'income':i['income'] if i['income'] not in ['NA',''] and float(i['income'])>=0 else 'NA',
        'days_since_major':days_since_maj,
        'nonhispanicwhite':i['nonhispanicwhite'],
        'race_majority':majority,
        'race_plurality':plurality,
        'race_supermajority':supermajority,
        'video_count':mentioned_video.get(i['id'],0),
        'article_count':mentioned_article.get(i['id'],0),
        'article_len':article_len.get(i['id'],0),
        'video_len':video_len.get(i['id'],0),
        'article_national':article_national.get(i['id'],0),
        'video_national':video_national.get(i['id'],0),
        'notable':1 if i['id'] in notable else 0,
        'num_characteristics': len(i['incident_characteristics'].split("||")),
        'n_participants':0,
        'named_participants':0,
        'named_shooters':0,
        'named_victims':0,
        'num_victims':0,
        'n_sources':len(list(filter(lambda x: 'twitter.com' not in x.lower(),i['sources'].split("', '"))))
      }
      
      for f in ['id','geoid','n_killed','n_injured','white','black','latinx','density','recent_death','latitude','longitude']:
        obj[f]=i[f]
      obj.update(incident_chars(chars))
      data_dict[obj['id']]=obj
      #data.append(obj)
  print("reading people")
  errors=0
  with open(GVA_PARTICIPANT_CSV,'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
      inc_id = int(row['Incident ID'].strip())
      match = data_dict.get(inc_id,None)
      if match:
        match['n_participants']+=1
        if row['Type']=='victim':
          match['num_victims']+=1
        if len(row['Name'])>1:
          match['named_participants']+=1
          if row['Type']=='victim':
            match['named_victims']=1
          else:
            match['named_shooters']=1
        errors+=1
  print(errors)
  for key in data_dict.keys():
    obj = data_dict[key]
    obj['pct_named']=obj['named_participants']/obj['n_participants'] if obj['n_participants']>0 else 0
    data.append(obj)
  df = pd.DataFrame(data)

  df.to_csv(OUTPUT_DIR+'incident_stats_updated.csv',index=False)
  print(df.shape)

  print(df[df['article_count']>0].shape)


def combine_article_info():
    df = pd.read_csv(OUTPUT_DIR+"articles.csv")
    
    print(df.shape)
    
    df1 = pd.read_csv(OUTPUT_DIR+"features_updated.csv")
    
    df1 = df1.drop(columns=['Unnamed: 0'])
   
    df=df.merge(df1, left_on='id',right_on='article_id',how='left',suffixes=('','_features'))
    print(df.shape)
   
    df['domain']= df['url'].apply(lambda x: get_domain(x))
    scores = pd.read_csv("./bias_scores.csv")
    scores = scores[['domain','score']]
    scores = scores.rename(columns={'score':'partisan_score'})
    print(df.shape)
    df = df.merge(scores,on='domain')
    df.to_csv(OUTPUT_DIR+"articles_with_features.csv")
    

def categorize(x):
  add_bias=False
  cat=''
  if x.source_scope=='National':
    add_bias=True
    cat='national'
  else:
    cat='local'
  if add_bias:
    cat+= '_left' if x.partisan_score<0 else '_right'
  cat+= '_white' if x.race_majority=='white' else '_poc'
  return cat
    
    
def get_everything():
  df=pd.read_csv(OUTPUT_DIR+"articles_with_features.csv")
 
  df = df.rename(columns={'race_majority':'race_majority_participants'})
  df4 = df[['primary_incident_id','num_victims']].copy()
  df4=df4.drop_duplicates()
  df2 = pd.read_csv(OUTPUT_DIR+"incidents.csv")
  df2 = df2[df2['id'].isin(list(df['primary_incident_id']))]
  print(df2.shape,df3.shape,df4.shape)
  df4 = df4.merge(df2,left_on='primary_incident_id',right_on='id',how='right')
  print(df4.shape)
  df4 = df4.drop_duplicates(subset=['id'])
  print(df4.shape)
  print(df4['count'].mean())

  
  df=df.merge(df2, left_on='primary_incident_id', right_on='id',how='left',suffixes=('','_incident'))
  df=df.drop(columns=[x for x in list(df.columns) if 'Unnamed: 0' in x])
  
  df['category']=df.apply(lambda x: categorize(x),axis=1)
  print(df.shape)
  df.to_csv(OUTPUT_DIR+"articles_with_everything.csv")
  
  
  
def combine_census(with_features=True):
  df = pd.read_csv(OUTPUT_DIR+"census_data.csv")
  features=['pct_hs_grad','families_below_pov','unemployment','female_heads','pct_children','public_assistance']
  for col in features:
      df[col+"_zscore"]=(df[col] - df[col].mean())/df[col].std(ddof=0)
      df[col+"_binary"]=(df[col+"_zscore"]>df[col+"_zscore"].quantile(0.75)).astype(int)
  df['cdi_raw']=df[[x+"_binary" for x in features]].mean(axis=1)
  df['cdi']=(df["cdi_raw"]>df["cdi_raw"].quantile(0.75)).astype(int)
  
  articles=pd.read_csv(OUTPUT_DIR+"articles_with_everything.csv") if with_features else pd.read_csv(OUTPUT_DIR+"articles_with_everything.csv")
  articles['merge_year']=articles['year'].apply(lambda x: 2022 if x==2023 else x)
  
  df = df.rename(columns={'geoid':'geoid_x','year':'merge_year'})
  articles=articles.merge(df,on=['geoid_x','merge_year'],how='left',suffixes=('', '_updated'))
  articles.to_csv(OUTPUT_DIR+"articles_with_updated_census_data.csv",index=False)
  
  incidents=pd.read_csv(OUTPUT_DIR+"incidents.csv")
  incidents['merge_year']=incidents['year'].apply(lambda x: 2022 if x==2023 else x)
  incidents=incidents.merge(df,on=['geoid_x','merge_year'],how='left',suffixes=('', '_updated'))
  incidents.to_csv(OUTPUT_DIR+"incidents_with_updated_census_data.csv",index=False)

def update_articles_paired():
  
  for group in ['_nonhispanicwhitelooser']: #'','_ice','_race_ice','_ice_namedshooters'
    pairs = pd.read_csv(SUBSET_DIR+'article_pairs'+group+'.csv')
    selected = list(pairs['poc'])+list(pairs['white'])
    df = pd.read_csv(OUTPUT_DIR+"articles_with_everything.csv")
    df = df.drop(columns=['Unnamed: 0'])
    #print("selected",selected[5])
    #print(df[['article_id_x']].dtypes)
    sampled = df[df['article_id'].isin(selected)]
    sampled.to_csv(SUBSET_DIR+'articles_paired'+group+'.csv',index=False)
    print(sampled.shape)

def parse_commandline():
    """Parse the arguments given on the command-line.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--with_features",
                       help="with linguistic features",
                       default=None)
    args = parser.parse_args()
    return str(args.with_features)=='True'


if __name__ == '__main__':
  with_features = parse_commandline()
  
  get_incident_info(True)
  get_article_info()
  get_incident_info()
  all_incident_info()
  if with features:
    combine_article_info()
    get_everything()
    combine_census()
  else:
    combine_census(False)
  