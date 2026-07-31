import spacy
from spacy_readability import Readability
import json
import os,csv
import pandas as pd
from config import *

nlp = spacy.load('en')
read = Readability()
nlp.add_pipe(read, last=True)
#doc = nlp("I am some really difficult text to read because I use obnoxiously large words.")
#doc._.flesch_kincaid_grade_level
#doc._.flesch_kincaid_reading_ease
#doc._.dale_chall

data =[]
def article_sents():
  for y in range(2014,2024): 
    year = str(y)
    print(year)
    directory = JSON_DIR+year+'/article_data'
    for i,filename in enumerate(os.listdir(directory)):
      f = os.path.join(directory,filename)
      #if i>250:
       # continue
      if i%100==0:
        print(i)
      
      if os.path.isfile(f):
        with open(f,'r') as infile:
          d=json.load(infile)
          if len(d['incident_term']['short'])!=1: continue
          for p in d['article_metadata']['sentences']:
            if len(p)>4:
              doc = nlp(p)
              data.append({
                'article_id':d['article_id'],
                'grade_level':doc._.flesch_kincaid_grade_level,
                'reading_ease':doc._.flesch_kincaid_reading_ease,
                'dale_chall':doc._.dale_chall,
                'length':len(doc),
                'incident':d['incident_term']['short'][0]
              })

for y in range(2014,2024): 
  year = str(y)
  print(year)
  infile=masking_dir+"masked_"+year+".csv" if IS_VIDEOS else masking_dir+"masked_sents_"+year+".csv"
  if not os.path.isfile(infile): continue
  with open(infile,'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for i,row in enumerate(reader):
      if i%1000==0: print(i)
      doc = nlp(row['text'])
      count=0
      for t in doc:
        if t.ent_iob_=='B' and t.ent_type_ in ['DATE','CARDINAL','PERCENT','TIME']:
          count+=1
      data.append({
        'article_id':row['article_id'],
        'grade_level':doc._.flesch_kincaid_grade_level,
        'reading_ease':doc._.flesch_kincaid_reading_ease,
        'dale_chall':doc._.dale_chall,
        'length_readability':len(doc),
        'number_count':count
      })
      """
      subjconc_data.append({
        'article_id':d['article_id'],
        'doc':doc
      })
      """
  
  df = pd.DataFrame(data)
  print(len(df))
  df.to_csv(OUTPUT_DIR+"readability_masked.csv",index=False)
print(df.mean())
print(df.min())
print(df.max())

#concrete(subjconc_data,extra='masked')
#subj(subjconc_data,extra='masked')

