import re
import csv
import numpy as np
import datetime
from config import *
from collections import Counter
from utils import get_name_variants,get_address_variants

  
def match_names(matches,rev_matches,incidents,articles):
  primary = {}
  matched_articles=[]
  secondary={}
  print("matching names")
  counter = Counter()
  for i,key in enumerate(incidents.keys()):
    row = incidents[key]
    secondary[row['id']]=[row[key] for key in ['state','city','county','place_name'] if row[key]!='']
    incident_names=[]
    for p in row['participants']:
      if p.get('name',None):
        names=[]
        variants = get_name_variants(p['name'])
        for v in variants:
          if len(v.split(" "))>1: 
            #names[v] = row['id']
            counter[v]+=1
            if counter[v]>1:
              secondary[row['id']]=[row[key] for key in ['city','county','place_name'] if row[key]!='']
            names.append(v)
        incident_names.append(names)
    if row.get('address',None) and len(row['address'])>7 and re.search('\d',row['address']) and re.search('\s',row['address']):
      incident_names.append(get_address_variants(row['address']))
    primary[row['id']]=incident_names
  print(counter.most_common(10))
  #  if row['participant_name']:
   #     name_list = row['participant_name']
    #    if "::" in name_list:
     #     name_list = name_list.split("||")
      #    if name_list!='':
       #     for n in name_list:
        #      name = n.split("::")
         #     if len(name[1].split(" "))>1:
          #      variants = get_name_variants(name[1])
           #     for v in variants:
            #      if len(v.split(" "))>1: 
             #       names[v] = row['incident_id']
#        else:
 #         name_list = name_list.split("|")
  #        if name_list!='':
   #         for n in name_list:
    #          name = n.split(":")
     #         if len(name[1].split(" "))>1:
      #          variants = get_name_variants(name[1])
       #         for v in variants:
        #          names[v] = row['incident_id']       
  for i,a_key in enumerate(articles.keys()):
    row = articles[a_key]['article']
    if len(row)>10:
      if i%100==0:
        print(i)
      name_list=[]
      for key in primary.keys():
        found_match=False
        primary_matches = [True for options in primary[key] if any([" "+name.lower()+" " in row.lower() for name in options])]
        if len(primary_matches)>1:
          found_match=True
        elif len(primary_matches)==1 and any([place.lower() in row.lower() for place in secondary[key]]):
          found_match=True
        if found_match:
          article_id = a_key
          match = matches.get(article_id,[])
          rev_match = rev_matches.get(key,[])
          match.append(key)
          rev_match.append(article_id)
          matches[article_id] = match
          rev_matches[key] = rev_match
#      if len(name_list)>0:
#       matched_articles.append(", ".join(name_list)+"\t"+row+"\n")
  
  print(len(matches.keys()),len(rev_matches.keys()))
  return matches,rev_matches
  
def match_urls(matches,rev_matches,incidents,articles,year,write_matches=False):
  urls={}
  ids = []
  count=0
  print("matching urls")
  for key in incidents.keys():
    row = incidents[key]
    url_list = row['sources']#.split('||')
    for u in url_list:
      urls[u] = row['id']
  print(len(urls.keys()))
  #with open('/projects/b1170/corpora/byu_corpora/NOW/sources/sources-17-06.txt', errors='ignore') as infile:
  for i,key in enumerate(articles.keys()):
    r = articles[key].get('metadata',None)
    #if articles.get(r[0],None):
      #articles[r[0]]['metadata'] = r
    if r:
      if i%1000==0:
        print(i)
      if urls.get(r[5],None):
      #for key in urls.keys():
       # if key.lower()==r[5].lower():
          count+=1
          if count%100==0: print(count)
          #matches[r[0]] = urls[key]
          #rev_matches[urls[key]] = r[0]
          match = matches.get(r[0],[])
          rev_match = rev_matches.get(urls[r[5]],[])
          match.append(urls[r[5]])
          rev_match.append(r[0])
          matches[r[0]] = match
          rev_matches[urls[r[5]]] = rev_match
    else:
      print("Metadata problem")
  print(count)
  if write_matches:
    matched_ids=[]
    for key in matches.keys():
      matched_ids.append(key+"\t"+", ".join(matches[key])+"\n")
    with open(OUTPUT_DIR+year+'/sorted_articles/id_matches'+str(INCREMENT)+'.txt','w') as outfile:
      for m in matched_ids:
        outfile.write(re.sub(r'\n+',r'\n',m))
  
  print(len(matches.keys()),len(rev_matches.keys()))
  return matches,rev_matches

def match_addresses(matches,rev_matches,incidents,articles):
  addresses={}
  ids = []
  print("matching addresses")
  for key in incidents.keys():
    row = incidents[key]
    if row['address'] and re.search('\d',row['address']) and (row['city'] or row['county']):
      addresses[key]={'address':row['address'],'city':row['city'] if row['city'] else row['county'],'place':row['place_name']}

  #with open('/projects/b1170/corpora/byu_corpora/NOW/sources/sources-17-06.txt', errors='ignore') as infile:
  for i,key in enumerate(articles.keys()):
    r = articles[key].get('article')
    if r:
      if i%100==0:
        print(i)
      for incident_id in addresses.keys():
        a = addresses[incident_id]
        if (len(a['address'])>5 and (" "+a['address'].lower()+" " in r.lower() or (" " in a['address'] and a['address'][:-1].lower() in r.lower()))) and " "+a['city'].lower()+" " in r.lower():
          article_id = r[2:10].strip()
          match = matches.get(article_id,[])
          rev_match = rev_matches.get(incident_id,[])
          match.append(incident_id)
          rev_match.append(article_id)
          matches[article_id] = match
          rev_matches[incident_id] = rev_match
          ids.append(key)
  
  print(len(matches.keys()),len(rev_matches.keys()))
  return matches,rev_matches

def write_matched_articles(year,s):
  article_ids=[]
  articles = []
  with open(OUTPUT_DIR+year+'/sorted_articles/id_matches'+s+'.txt','r') as infile:
    for row in infile:
      if len(row)>3:
        r = row.split("\t")
        article_ids.append(r[0].strip())
  with open(OUTPUT_DIR+year+'/sorted_articles/incidents'+s+'.txt','r') as infile:
    for row in infile:
      if row[2:10].strip() in article_ids:
        articles.append(row)
  print(len(articles))
  with open(OUTPUT_DIR+year+'/sorted_articles/matched_articles'+s+'.txt','w') as outfile:
    for a in articles:
      outfile.write(a+"\n")

  
def matchAll(incidents,articles,year,segment):
  s=str(segment) if segment else ''
  if 'video' not in OUTPUT_DIR:
    matches,rev_matches = match_urls({},{},incidents,articles,year)
  else:
    matches={}
    rev_matches={}
  print("starting names")
  final_matches,final_rev_matches = match_names(matches,rev_matches,incidents,articles)
  #final_matches,final_rev_matches = match_addresses(temp_matches,temp_rev_matches,incidents,articles)
  #final_matches,final_rev_matches = match_addresses(matches,rev_matches,incidents,articles)
  
  matched_ids=[]
  for key in final_matches.keys():
    matched_ids.append(key+"\t"+", ".join(final_matches[key])+"\n")
  with open(OUTPUT_DIR+year+'/sorted_articles/id_matches'+s+'.txt','w') as outfile:
    for m in matched_ids:
      outfile.write(re.sub(r'\n+',r'\n',m))
      
  matched_ids=[]
  for key in final_rev_matches.keys():
    matched_ids.append(key+"\t"+", ".join(final_rev_matches[key])+"\n")
  with open(OUTPUT_DIR+year+'/sorted_articles/rev_id_matches'+s+'.txt','w') as outfile:
    for m in matched_ids:
      outfile.write(re.sub(r'\n+',r'\n',m))
      
  #write_matched_articles(year,s)
  return final_matches,final_rev_matches
  
