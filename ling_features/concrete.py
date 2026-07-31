import csv
import re
import json
import numpy as np
import pandas as pd
import os
import spacy
nlp = spacy.load('en_core_web_lg')
from config import *


def concrete(data,extra='',is_added=False):
  adj={}
  noun={}
  verb={}
  adv={}
  other={}
  with open(lexicon_dir+"concrete_lexicon.csv",'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
      if int(row['Bigram'])!=0 or str(row['Dom_Pos']) in ['Number','0']:
        continue
      if row['Dom_Pos']=='Adjective':
        adj[row['Word']]=float(row['Conc.M'])
      elif row['Dom_Pos']=='Noun':
        noun[row['Word']]=float(row['Conc.M'])
      elif row['Dom_Pos']=='Verb':
        verb[row['Word']]=float(row['Conc.M'])
      elif row['Dom_Pos']=='Adverb':
        adv[row['Word']]=float(row['Conc.M'])
      else:
        other[row['Word']]=float(row['Conc.M'])
      #lemmas[row['lemma']]=float(row['rating'])
  
  words = {
    'NOUN': noun,
    'VERB': verb,
    'ADJ': adj,
    'ADV': adv,
    'other': other
  }
  all=[]
  results={}
  for d in data:
    word_count=0
    ratings=[]
    for t in d['doc']:
      if t.is_punct:
        continue
      word_count+=1
      if t.pos_ in ['NOUN','VERB','ADJ','ADV']:
        if words[t.pos_].get(t.lower_,None):
          ratings.append(words[t.pos_][t.lower_])
       # else:
        #  print(t.lower_)
      else:
        if words['other'].get(t.lower_,None):
          ratings.append(words['other'][t.lower_])
    all.append({
      'article_id':d['article_id'],
      'sentence':d['doc'].text,
      'rating':np.mean(ratings)
    })  
    r=results.get(d['article_id'],{'article_id':d['article_id'],'ratings':[],'length':0})
    r['ratings']+=ratings
    r['length']+=word_count
    results[d['article_id']]=r
  df = pd.DataFrame(all)
  df.to_csv(OUTPUT_DIR+"all_concreteness_scores.csv",index=False)
  final_data=[]
  for key in results:
    final_data.append({
      'article_id':key,
      'rating':np.mean(results[key]['ratings']),
      'missing': (results[key]['length']-len(results[key]['ratings']))/results[key]['length'],
      'length':results[key]['length']
    })
  df = pd.DataFrame(final_data)
  if is_added:
    old_df =pd.read_csv(OUTPUT_DIR+"concreteness_scores.csv")
    new_df=pd.concat([old_df,df])
    new_df = new_df.drop_duplicates(subset=['article_id'])
    new_df.to_csv(OUTPUT_DIR+"concreteness_scores.csv",index=False)
  else:
    df.to_csv(OUTPUT_DIR+"concreteness_scores"+extra+".csv",index=False)