import spacy
nlp = spacy.load('en_core_web_lg')
from collections import defaultdict
import pandas as pd
import re
import os
import json
import csv
from config import *

def reorganize(row):
  #print(row)
  obj={
    'word':row[2].split("=")[1],
    'polarity':re.sub('\n','',row[5].split("=")[1]) if row[5]!='m' else re.sub('\n','',row[6].split("=")[1]),
    'stemmed':row[4].split("=")[1]
  }
  return obj

def get_polarity(token,s,n):
  polarity=None
  s_token=s.get(token.lemma_,None)
  n_token=n.get(token.lower_,None)
  if s_token:
    polarity = s_token['polarity']
  elif n_token:
    polarity = n_token['polarity']
  return polarity

def subj(data,extra='',is_added=False):
  verb_s={}
  verb_n={}
  noun_s={}
  noun_n={}
  adj_s={}
  adj_n={}
  adverb_s={}
  adverb_n={}
  other_s={}
  other_n={}
  
  with open(lexicon_dir+"subjclueslen1-HLTEMNLP05.tff",'r') as infile:
    for row in infile:
      r = row.split(" ")
      if r[0]=='type=strongsubj':
        pos = r[3].split("=")[1]
        obj=reorganize(r)
        word = obj['word']
        if pos == 'verb':
          if obj['stemmed']=='y':
            verb_s[word]=obj
          else:
            verb_n[word]=obj
        elif pos=='noun':
          if obj['stemmed']=='y':
            noun_s[word]=obj
          else:
            noun_n[word]=obj
        elif pos=='adj':
          if obj['stemmed']=='y':
            adj_s[word]=obj
          else:
            adj_n[word]=obj
        elif pos=='adverb':
          if obj['stemmed']=='y':
            adverb_s[word]=obj
          else:
            adverb_n[word]=obj
        elif pos=='anypos':
          if obj['stemmed']=='y':
            verb_s[word]=obj
            noun_s[word]=obj
            adj_s[word]=obj
            adverb_s[word]=obj
            other_s[word]=obj
          else:
            verb_n[word]=obj
            noun_n[word]=obj
            adj_n[word]=obj
            adverb_n[word]=obj
            other_n[word]=obj
  counters = {}
  all=[]
  for d in data:
    counter = counters.get(d['article_id'],defaultdict(int))
    new_counter=defaultdict(int)
    for t in d['doc']:
      if t.is_punct:
        continue
      if t.pos_=='VERB':
        counter[get_polarity(t,verb_s,verb_n)]+=1
        new_counter[get_polarity(t,verb_s,verb_n)]+=1
      elif t.pos_=='NOUN':
        counter[get_polarity(t,noun_s,noun_n)]+=1
        new_counter[get_polarity(t,noun_s,noun_n)]+=1
      elif t.pos_=='ADJ':
        counter[get_polarity(t,adj_s,adj_n)]+=1
        new_counter[get_polarity(t,adj_s,adj_n)]+=1
      elif t.pos_=='ADVERB':
        counter[get_polarity(t,adverb_s,adverb_n)]+=1
        new_counter[get_polarity(t,adverb_s,adverb_n)]+=1
      else:
        counter[get_polarity(t,other_s,other_n)]+=1
        new_counter[get_polarity(t,other_s,other_n)]+=1
      counter['all']+=1
      new_counter['all']+=1
    if new_counter['all']!=0:
      all.append({
        'article_id':d['article_id'],
        'sentence':d['doc'].text,
        'negative':new_counter['negative']/new_counter['all'],
        'positive':new_counter['positive']/new_counter['all'],
        'neutral':new_counter['neutral']/new_counter['all'],
        'subjective':(new_counter['neutral']+new_counter['negative']+new_counter['positive'])/new_counter['all']
      })
    counters[d['article_id']]=counter
  df = pd.DataFrame(all)
  df.to_csv(OUTPUT_DIR+"all_subj_scores"+extra+".csv",index=False)
  final_data=[]
  for key in counters:
    counter = counters[key]
    final_data.append({
      'article_id':key,
      'negative':counter['negative']/counter['all'],
      'positive':counter['positive']/counter['all'],
      'neutral':counter['neutral']/counter['all'],
      'subjective':(counter['neutral']+counter['negative']+counter['positive'])/counter['all'],
      'length':counter['all']
    })
  df = pd.DataFrame(final_data)
  if is_added:
    old_df =pd.read_csv(OUTPUT_DIR+"subj_scores.csv")
    new_df=pd.concat([old_df,df])
    new_df = new_df.drop_duplicates(subset=['article_id'])
    new_df.to_csv(OUTPUT_DIR+"subj_scores.csv",index=False)
  else:
    df.to_csv(OUTPUT_DIR+"subj_scores"+extra+".csv",index=False)