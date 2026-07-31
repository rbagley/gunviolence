import csv

import argparse
import pandas as pd
import math
import os
import json
import csv
from config import *

def get_scores(year,segment):
  import torch
  import spacy
  nlp = spacy.load('en_core_web_lg')
  from transformers import pipeline
  from scipy.special import softmax
  #from transformers import AutoTokenizer, AutoModelForSequenceClassification
  #from optimum.bettertransformer import BetterTransformer
  
  #tokenizer = AutoTokenizer.from_pretrained("s-nlp/xlmr_formality_classifier")
  
  #model_hf = AutoModelForSequenceClassification.from_pretrained("s-nlp/xlmr_formality_classifier", device_map="auto")
  #model = BetterTransformer.transform(model_hf, keep_original_model=True)
  pipe = pipeline("text-classification", model="s-nlp/xlmr_formality_classifier")
  #for y in range(2014,2024):
   # year = str(y) 
  data=[]
  ids=[]
  sents=[]
  directory = JSON_DIR+year+'/article_data'
  for i,filename in enumerate(os.listdir(directory)):
    f = os.path.join(directory,filename)
    if i%500==0:
      print(i)
    if os.path.isfile(f):
      with open(f,'r') as infile:
        d=json.load(infile)
        for p in d['article_metadata']['sentences']:
          doc = nlp(p)
          for s in doc.sents:
            if len([t for t in s if t.pos_=='VERB'])>0 and len([t for t in s if t.pos_ in ['NOUN','PRON','PROPN']])>0 and s[len(s)-1].is_punct:   
              if len(s)>500:
                print("length problem", len(s))
                continue
              else:
                sents.append(s.text)
                ids.append(d['article_id'])
  lens = [len(s) for s in sents]
  print("done reading",len(sents),max(lens))
  all_logits=[]
  for i in range(math.ceil(len(sents)/10000)):
    print(i)
    if i*10000>len(sents):
      continue
    subset = sents[i*10000:min(len(sents),(i+1)*10000)]
    try:
      output = pipe(subset)
      all_logits+=output
    except:
      for i in range(math.ceil(len(subset)/100)):
        try:
          output = pipe(subset[i*100:min(len(subset),(i+1)*100)])
          all_logits+=output
        except:
          sub = subset[i*100:min(len(subset),(i+1)*100)]
          for item in sub:
            try:
              output = pipe([item])
              all_logits+=output
            except:
              print(item)
              all_logits+=[{'score':0,'label':'invalid'}]
            
    
  for i,r in enumerate(all_logits):
    if r['label']!='invalid':      
      data.append({
        'article_id':ids[i],
        'sentence':sents[i],
        'formality': r['score'] if r['label']=='formal' else (1-r['score']),
        'class':r['label']
      })
  df = pd.DataFrame(data)
  df.to_csv(OUTPUT_DIR+year+"_formality.csv",index=False)  
  

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
    segment = int(args.segment) if args.segment!=None else None
    return str(args.year),segment

def combine():
  full_df=None
  started=None
  for y in range(2014,2024):
    year = str(y)
    df = pd.read_csv(OUTPUT_DIR+year+"_formality.csv")
    new_df = df[['article_id','formality']].groupby('article_id').agg('mean')
    new_df['formal_sent_count']=df.groupby('article_id').size()
    if not started:
      full_df=new_df
      started = True
    else:
      full_df=pd.concat([full_df,new_df])
  full_df.to_csv(OUTPUT_DIR+"formality_scores.csv")
  

if __name__ == '__main__':
  year,segment = parse_commandline()
  get_scores(year,segment)
  #combine()
