import json,csv
from concrete import concrete
from subjectivity import subj
import os
import spacy
from config import *
import pandas as pd
nlp = spacy.load('en_core_web_lg')


data =[]
number_count=[]

  
def masked():
  for y in range(2014,2024): 
    year = str(y)
    print(year)
    if not os.path.isfile(masking_dir+"masked_"+year+".csv"): continue
    with open(masking_dir+"masked_"+year+".csv",'r') as csvfile:
      reader = csv.DictReader(csvfile)
      for i,row in enumerate(reader):
        p=row['text']
        doc = nlp(p)
        count=0
        for t in doc:
          if t.ent_iob_=='B' and t.ent_type_ in ['DATE','CARDINAL','PERCENT','TIME']:
            count+=1
        number_count.append({
          'article_id':row['article_id'],
          'number_count':count
        })  
        data.append({
          'article_id':row['article_id'],
          'doc':doc
        })
  
  df = pd.DataFrame(number_count)
  df.to_csv(OUTPUT_DIR+"number_count.csv",index=False)
  concrete(data,extra='masked')
  subj(data,extra='masked')

masked()