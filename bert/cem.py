import pandas as pd
import csv
from collections import defaultdict 
import numpy as np

ignore_frequency=False

inpath="/projects/p31502/projects/gun_violence/community_justice/processed/"
outpath='/projects/p31502/projects/gun_violence/community_justice/subset_curation/'

few_chars=['major','low_death','year']
all_chars=['major','low_death','year','officer','drug','gang','suicide','mass','accident','assaultweapon','domestic_violence','school']

def match_on_articles(var_name='race_majority',use_all_chars=True,extra=''):
  characteristics=all_chars if use_all_chars else few_chars
  df = pd.read_csv(inpath+"articles_with_everything.csv")
  df = df[(df['nonhispanicwhite']<=40) | (df['nonhispanicwhite']>=60)]
  id_name='article_id'
  #print([x for x in list(df.columns) if 'id' in x])
  print(df.shape)
  df = df[df['shortterm']>0]
  print(df.shape)
  #df = df[df['named_perp']>0]
  print(df.shape)
  if var_name=='race_majority':
    df['is_poc'] = df['race_majority'].apply(lambda x: x!='white')
  elif var_name=='nonhispanicwhite':
    df['is_poc']=df['nonhispanicwhite']<=60
  else:
    df['is_poc']=df[var_name]<0
  df['major']=df['n_killed'].apply(lambda x : x>4)
  df['precovid']=df['year_incident'].apply(lambda x : x<2020)
  #df['art_count']=df['count'].apply(lambda x : 'one' if x<3 else 'some' if x<=10 else 'many')
  #print(df['year'].value_counts())
  print(df['is_poc'].value_counts())
  df['low_death']=df['n_killed'].apply(lambda x: x<2)
  df = df[['primary_incident_id','year_incident','major','low_death','precovid','is_poc','officer','drug','gang','suicide','mass','accident','assaultweapon','domestic_violence','school',id_name]]
  
  df = df.rename(columns={'article_id_x':'article_id','year_incident':'year'})
  df['vector'] = df[characteristics].apply(lambda x: str([x[a] for a in x.keys()]),axis=1)
  d = df
  df = d[['vector','is_poc','primary_incident_id','article_id']]
  df.to_csv(outpath+'article_vectors_'+var_name+extra+'.csv')
  df = d[['vector','is_poc','article_id']]
  
  new_df = df.groupby(['vector']).count()
  
  df1=df[['vector','is_poc']][df['is_poc']==False].groupby('vector').agg('count')
  df2=df[['vector','is_poc']][df['is_poc']==True].groupby('vector').agg('count')
  #print(df1.shape,df2.shape)
  new_df = df1.merge(df2,left_index=True,right_index=True,suffixes=('_white','_poc'))
  #print(new_df.shape)
  new_df['min']=new_df[['is_poc_white','is_poc_poc']].min(axis=1)
  new_df.to_csv(outpath+'article_counts_'+var_name+extra+'.csv')
  print(sum(new_df['min'])*2)
  counts={}
  white=defaultdict(list)
  poc=defaultdict(list)
  with open(outpath+'article_counts_'+var_name+extra+'.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
      counts[row['vector']]=int(row['min'])
  
  #art_count={}
  missing=0
  with open(outpath+'article_vectors_'+var_name+extra+'.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
      d = poc if row['is_poc']=='True' else white
      if IS_VIDEOS:
        d[row['vector']].append(row['article_id'])
      else:
        if row['article_id']=='':
          missing+=1
        else:
          d[row['vector']].append(int(float(row['article_id'])))
      #art_count[int(row['id'])]=int(row['count'])
  print(missing)
  
  selected=[]
  pair_frames=[]
  to_select=defaultdict(list)
  for i,key in enumerate(counts.keys()):
    #if counts[key]<5:
    #print(np.random.choice(white[key],counts[key],replace=False))
    selection_size=min(len(white[key]),len(poc[key]))
    if len(white[key])<counts[key]:
      print('white',counts[key],len(white[key]))
    if len(poc[key])<counts[key]:
      print('poc',counts[key],len(poc[key]))
    white_ids = np.random.choice(white[key],selection_size,replace=False).tolist()
    poc_ids =np.random.choice(poc[key],selection_size,replace=False).tolist()
    pair_frames.append(pd.DataFrame({'poc':poc_ids,'white':white_ids}))
    selected+=white_ids
    selected+=poc_ids
  pairs = pd.concat(pair_frames)
  print("PAIRS",len(selected))
  pairs.to_csv(outpath+'article_pairs_'+var_name+extra+'.csv',index=False)
  
  df = pd.read_csv(inpath+"articles_with_everything.csv")
  df = df.drop(columns=['Unnamed: 0'])
  #print("selected",selected[5])
  print(df[[id_name]].dtypes)
  sampled = df[df[id_name].isin(selected)]
  sampled.to_csv(outpath+'articles_paired_'+var_name+extra+'.csv',index=False)

def update_articles_paired():
  pairs = pd.read_csv(outpath+'article_pairs.csv')
  selected = list(pairs['poc'])+list(pairs['white'])
  df = pd.read_csv(inpath+"articles_with_everything.csv")
  df = df.drop(columns=['Unnamed: 0'])
  #print("selected",selected[5])
  #print(df[['article_id_x']].dtypes)
  sampled = df[df['article_id_x'].isin(selected)]
  sampled.to_csv(outpath+'articles_paired.csv',index=False)
  print(sampled.shape)
  print([s for s in list(sampled.columns) if 'partisan' in s])
  
def get_art_count(df,id):
  return df[df['primary_incident_id']==id].shape[0]


  
match_on_articles('nonhispanicwhite',True,'strict')

