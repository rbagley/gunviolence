import csv
import pandas as pd
import re
import os
from urllib.parse import urlparse
from config import ARTICLE_DIR,OUTPUT_DIR
DIR=OUTPUT_DIR
print(DIR)
GVA_domains=[]
NOW_domains=[]

def new_sources():
  for y in range(2014,2024):
    year = str(y)
    print(year)
    with open("/projects/b1170/corpora/byu_corpora/NOW/sources/sources-"+year+".txt",'r', errors='ignore') as infile:
      for row in infile:
        r = row.split('\t')
        if r[3].lower()=='us':
          sources.append({
            'article_id':r[0],
            'date':r[2],
            'url':r[5]
          })
          
def old_sources():
  for y in range(1,3):
    with open("/projects/b1170/corpora/byu_corpora/old_NOW/now_sources_pt"+str(y)+".txt",'r', errors='ignore') as infile:
      for row in infile:
        r = row.split('\t')
        year = int(r[2].split("-")[0])
        if r[3].lower()=='us' and year>13:
          sources.append({
            'article_id':r[0],
            'date':r[2],
            'url':r[5]
          })
  
  directory = "/projects/b1170/corpora/byu_corpora/old_NOW/sources/"
  for filename in os.listdir(directory):
    year = filename.split("-")
    if int(year[1])<19:
      f = os.path.join(directory,filename)
      with open(f,'r', errors='ignore') as infile:
        for row in infile:
          r = row.split('\t')
          if r[3].lower()=='us':
            sources.append({
              'article_id':r[0],
              'date':r[2],
              'url':r[5]
            })



def fix_url(url,is_GVA):
  res = urlparse(url)
  if is_GVA:
    GVA_domains.append(res.netloc)
  else:
    NOW_domains.append(res.netloc)
  return res.netloc + res.path + '?' + res.query if res.query!='' else res.netloc + res.path
  #canonical += '?' + res.query if res.query!=''

def check_domains():
  missing=[]
  present=[]
  print(len(GVA_domains),len(NOW_domains))
  GVA_list = list(set(GVA_domains))
  NOW_list = list(set(NOW_domains))
  for g in GVA_list:
    if g not in NOW_list:
      missing.append(g)
    else:
      present.append(g)
  print(len(GVA_list),len(present),len(missing))
  print(len(NOW_list))
  print(missing if len(missing)<100 else missing[:100])
  with open('/projects/p31502/projects/gun_violence/community_justice/preprocessing_pipeline/missing_domains.txt','w') as outfile:
      outfile.write('\n'.join(missing))
  with open('/projects/p31502/projects/gun_violence/community_justice/preprocessing_pipeline/existing_domains.txt','w') as outfile:
      outfile.write('\n'.join(present))

def check_urls():
  missing=[]
  existing=[]
  with open('/projects/p31502/projects/gun_violence/community_justice/preprocessing_pipeline/missing_domains.txt','r') as infile:
    for r in infile:
      missing.append(re.sub("\n",'',r))
  with open('/projects/p31502/projects/gun_violence/community_justice/preprocessing_pipeline/existing_domains.txt','r') as infile:
    for r in infile:
      existing.append(re.sub("\n",'',r))
  df = pd.read_csv("/projects/p31502/projects/gun_violence/community_justice/preprocessing_pipeline/url_matches.csv")
  ids = set(list(df['article_id']))
  print(len(missing),missing[:5])
  print(len(existing),existing[:5])
  e=0
  m=0
  error=0
  examples=[]
  with open("/projects/b1170/corpora/GVA/incidents_for_matching.csv",'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
      sources = row['sources_str'].split("||")
      year = int(re.sub('/','-',row['Date']).split('-')[2])
      if year<2020 or year>2022:
        continue
      for s in list(set(sources)):
        res = urlparse(s)
        if res.netloc in existing:
          e+=1
          if row['Incident ID'] not in ids:
            examples.append(s)
        elif res.netloc in missing:
          m+=1 
        else:
          error+=1
  print(e,m,error)
  print(examples[:100])

def get_matches():
#  df = pd.read_csv("/projects/b1170/corpora/GVA/incidents_with_locations.csv")
#  df2=pd.read_csv("/projects/p31502/projects/gun_violence/community_justice/preprocessing_pipeline/incidents_with_locations.csv")
#  combined = df.merge(df2,left_on='Incident ID', right_on='incident_id')
 # print(df.shape,df2.shape,combined.shape)
  #combined.to_csv("/projects/p31502/projects/gun_violence/community_justice/preprocessing_pipeline/overlap.csv")
  urls=[]
  with open("/projects/b1170/corpora/GVA/incidents_for_matching.csv",'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
      sources = row['sources_str'].split("||")
      if int(re.sub('/','-',row['Date']).split('-')[2])<2020:
        continue
      for s in list(set(sources)):
        urls.append({
          'url':fix_url(s,True),
          'incident_id':row['Incident ID'],
          'incident_year':re.sub('/','-',row['Date']).split('-')[2]
        })
  df = pd.DataFrame(urls)
  print(df.shape)
  sources=[]
#  for y in range(2014,2024):
 #   year = str(y)
  #  print(year)
   # with open("/projects/b1170/corpora/byu_corpora/NOW/sources/sources-"+year+".txt",'r', errors='ignore') as infile:
  directory = '/projects/b1170/corpora/byu_corpora/NOW/sources'
  for filename in os.listdir(directory):
    f = os.path.join(directory,filename)
    if os.path.isfile(f) and filename.split("-")[1] in['2020.txt','21','22','23']:# and check_source_dates(filename,year):
      #print(f)
      with open(f, errors='ignore') as infile:
        for row in infile:
          r = row.split('\t')
          if len(r)<4:
            continue
          else:
            if r[3].lower()=='us':
              sources.append({
                'article_id':r[0],
                'date':r[2].split("-")[0],
                'url':fix_url(r[5],False)
              })
    
  
  sources = pd.DataFrame(sources)
  #  try:
  #    df1 = pd.read_csv("/projects/b1170/corpora/byu_corpora/NOW/sources/sources-"+year+".txt",sep='\t',header=None,names=['article_id','len','date','country','source_name','url','headline'])
  #  except:
  #    df1 = pd.read_csv("/projects/b1170/corpora/byu_corpora/NOW/sources/sources-"+year+".txt",sep='\t',header=None,names=['article_id','len','date','country','source_name','url','headline'], encoding= 'unicode_escape')
  #  dfs.append(df1[df1['country']=='US'])
  #sources=pd.concat(dfs)
  print(sources.shape)   
  combined = df.merge(sources,on='url')
  #combined.to_csv("/projects/p31502/projects/gun_violence/community_justice/preprocessing_pipeline/url_matches1.csv",index=False)
  print(combined.shape)
  check_domains()
  #incidents=list(combined['incident_id'])
  #articles=list(combined['article_id'])

def check_matches():
  urls = pd.read_csv("/projects/p31502/projects/gun_violence/community_justice/preprocessing_pipeline/url_matches.csv")
  print(urls.shape)
  urls = urls.drop_duplicates()
  print(urls.shape)
  matches=[]
  #with open("/projects/p31502/projects/gun_violence/community_justice/preprocessing_pipeline/url_matches.csv",'r') as csvfile:
   # reader = csv.DictReader(csvfile)
    #for row in reader:
     # matches.append({
      #  'article_id':row['article_id'],
      #})
  
  for y in range(2014,2024):
    year = str(y)
    directory=DIR+year+"/sorted_articles"
    for filename in os.listdir(DIR+year+"/sorted_articles"):
      f = os.path.join(directory,filename)
      if os.path.isfile(f) and filename.startswith('id_matches'):
        with open(f,'r') as infile:
          for i,row in enumerate(infile):
            r= re.sub(r'\n',r'',row)
            r=r.split("\t")
            s = set(r[1].split(", "))
            for incident in list(s):
              matches.append({
                'article_id':int(r[0]),
                'incident_id':int(incident),
                'has_match':True
              })
  df = pd.DataFrame(matches)
  combined = urls.merge(df,on=['article_id','incident_id'],how='left')
  combined = combined.drop_duplicates(subset=['article_id','incident_id'])
  combined.to_csv("/projects/p31502/projects/gun_violence/community_justice/preprocessing_pipeline/url_matches_new.csv",index=False)
  print(combined.shape)
  print(df.shape)
  print(urls.shape)  
  print(combined['has_match'].value_counts())

def precision():
  

  other=[]
  df = pd.read_csv("/projects/p31502/projects/gun_violence/community_justice/preprocessing_pipeline/url_matches_new.csv")
  print(df.drop_duplicates(subset=['article_id']).shape)
  print(df.drop_duplicates(subset=['article_id'])['date'].value_counts())
  counts=df.drop_duplicates(subset=['article_id'])['date'].value_counts()
  #print(df['date'].value_counts())
  #print(df['incident_year'].value_counts())
  matched_ids=[str(i) for i in list(set(list(df[df['has_match']==True]['article_id'])))]
  unmatched_ids = [str(i) for i in list(set(list(df[df['has_match']!=True]['article_id'])))]
  #print(df[(df['date']==14)])
  print(len(matched_ids), len(unmatched_ids))
  found_ids=[]

  for y in range(2014,2024):
    year = str(y)
    print(year)
    count=0
    matched=0
    unmatched=0
    year_found=0
    with open(DIR+year+"/sorted_articles/initial_sort.txt",'r') as infile:
      for row in infile:
        count+=1
        article_id=row[2:].split()[0]
        if article_id in matched_ids:
          matched+=1
          year_found+=1
          found_ids.append(article_id)
        elif article_id in unmatched_ids:
          unmatched+=1
          year_found+=1
          found_ids.append(article_id)
    print(count,matched,unmatched,counts[int(year[2:])]-(matched+unmatched))
    u=list(filter(lambda x: str(x) not in found_ids,list(df[df['date']==int(year[2:])]['article_id'])))
    print(u if len(u)<10 else u[:10])
    u=list(filter(lambda x: str(x) not in found_ids,list(set(list(df['article_id'])))))
    print(len(u))
    with open('/projects/p31502/projects/gun_violence/community_justice/preprocessing_pipeline/missing_ids.txt','w') as outfile:
      outfile.write('\n'.join([str(i) for i in u]))
  print(matched/len(matched_ids),unmatched/len(unmatched_ids))
  print(matched,unmatched)
  print((matched+unmatched)/len(df.drop_duplicates(subset=['article_id'])))
  
def searching():
  df = pd.read_csv("/projects/p31502/projects/gun_violence/community_justice/preprocessing_pipeline/url_matches_new.csv")
  df = df.drop_duplicates(subset=['article_id'])
  ids = {}
  for y in range(14,24):
    year = str(y)
    ids[year]=[str(i) for i in list(set(list(df[(df['has_match']!=True)&(df['date']==y)]['article_id'])))]
    print(y,df[(df['date']==y)].shape)
  #ids = list(set(ids))
  directory = '/projects/b1170/corpora/byu_corpora/NOW/processed_text/'
  for filename in os.listdir(directory):
    f = os.path.join(directory,filename)
    if ("us" in filename or "US" in filename) and os.path.isfile(f) and int(filename.split("-")[0])>13:
      print(len(ids[filename.split("-")[0]]),f)
      with open(f,'r') as infile:
        for row in infile:
          for r in row.split("@@"):
            for i in ids[filename.split("-")[0]]:
              if r.startswith("@@"+i):
                ids[filename.split("-")[0]].remove(i)
  print([len(ids[i]) for i in ids.keys()])


check_urls()
#get_matches()
#check_matches() 
#precision()
#searching()


#693 713
#2014
#6658 7 3
#2015
#9593 51 20
#2016
#32025 340 157
#2017
#35295 650 426
#2018
#28022 693 472
#1.0 0.6619915848527349
#693 472
#0.736875395319418

#['14536727', '14145562', '19537960', '20822083', '18528338', '13793362', '3694685', '20756593', '14393468', '8405119', '18305154', '18466959', '14362771', '3840167', '14266548']

#['22663170', '15532034', '18558985', '17977353', '3917834', '20371469', '18829326', '18214934', '20850711', '14536727', '13858841', '14145562', '18458653', '20860958', '19537960']


#['3064012', '3694685', '3891192']


    