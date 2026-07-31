import os
import json
from config import *

import re
#import spacy
import csv
from embeddings import get_name_variants
import argparse

keywords=['police','cop','officer','sheriff','deputy','trooper','detective','sergeant','agent','enforcement','lieutenant','polices','investigator','cops','sheriffs','deputies','troopers','detectives','agents','agency','investigators','officers','patrol','k-9','patrols','department','fbi','pd','911','official','officials','capt','lt','sgt','col','colonel']

def write_masks(year,segment,paragraphs=False,police_group=False):
  #nlp = spacy.load('en_core_web_lg')
  
   
  #for y in range(2014,2024):
   # year = str(y)
  print(year)
  data=[]
  directory = OUTPUT_DIR+year+'/article_data'
  
  for i,filename in enumerate(os.listdir(directory)):
    f = os.path.join(directory,filename)
    if os.path.isfile(f) and (i%4==segment or segment==None):
      with open(f,'r') as infile:
        d=json.load(infile)
        #if len(d['article_metadata']['mentions']['race'])>0: 
        data.append(d)
  print(len(data)) 
  
  masks = []
  for i,d in enumerate(data):
    if i%500==0:
      print(i)
    #if i%4!=segment:
     # continue
    
    shooters=[]
    victims=[]
    police=[]
    for incident in d['incident_metadata']:
      for p in incident['participants']:
        if p.get('name') and p.get('type') and p['name']!='Officer':
          if police_group and any([name for name in ['officer','capt','sgt','police'] if name in p['name'].lower()]):
            police.append(p['name'])
          elif p['type']=='victim':
            victims.append(p['name'])
          else:
            shooters.append(p['name'])
    chunks = d['article_metadata']['sentences']
    if paragraphs:
      chunks = re.split(r'<h>|<p>',d['article_original'])[1:]
    for text in chunks:
      for v in victims:
        v = re.sub("\(|\)|\/|\*|\[.*\]","",v)
        v = v.strip()
        if len(v)>4:
          for variant in sorted(get_name_variants(v),key=len,reverse=True):
            try:
              text = re.sub(re.escape(variant),'victim_name',text,flags=re.IGNORECASE)
            except:
              print(variant)
      for s in shooters:
        s = re.sub("\(|\)|\/|\*|\[.*\]","",s)
        s = s.strip()
        if len(s)>4:
          for variant in sorted(get_name_variants(s),key=len,reverse=True):
            try:
              text=re.sub(re.escape(variant),'shooter_name',text,flags=re.IGNORECASE)
            except:
              print(variant)
      for s in police:
        s = re.sub("\(|\)|\/|\*|\[.*\]","",s)
        s = s.strip()
        if len(s)>4:
          for variant in sorted(get_name_variants(s),key=len,reverse=True):
            try:
              text=re.sub(re.escape(variant),'police_name',text,flags=re.IGNORECASE)
            except:
              print(variant)
      if len(text)>500000:
        print(text[:100])
      if text.count('victim_name')>50:
        print(text)
      elif text.count('shooter_name')>50:
        print(text)
      """
      doc = nlp(text)
      if len(doc)<5:
        continue
      text=[]
      lemmas=[]
      for t in doc:
        if t.lower_ in keywords and police_group:
          text.append('_police_')
          lemmas.append('_police_')
        else:
          text.append(t.text)
          lemmas.append(t.lemma_)
      text = " ".join(text)
      text = re.sub(r'(_police_ )+','_police_ ',text)
      lemmas = " ".join(lemmas)
      lemmas = re.sub(r'(_police_ )+','_police_ ',lemmas)
      """
      obj = {
      'article_id':d['article_id'],
      'text': text#,
      #'lemmas':lemmas
      }
      masks.append(obj)
    
  print(len(masks))
  if not os.path.exists(masking_dir):
    os.makedirs(masking_dir)
  output=masking_dir+"masked_names_"+year+"_"+str(segment)+".csv"
  if paragraphs:
    output=masking_dir+"masked_paragraphs_"+year+".csv"
  if police_group:
    output=masking_dir+"masked_paragraphs_policeparticipants_"+year+".csv"
  with open(output,'w') as csvfile:
    writer = csv.DictWriter(csvfile,fieldnames=['article_id','text'])
    writer.writeheader()
    for m in masks:
      writer.writerow(m)
      #text = re.sub("<p>","",text)
    #text = re.sub("<h>","",text) 
  #  doc = nlp(text)
   # tokens = []
    #for token in doc:
     # if token.text=='victim_name' or token.text=='shooter_name':
      #  tokens.append(token.text)
      #elif token.ent_type_ in ['PERSON','GPE','ORG']:
       # if token.ent_iob_=='B':
        #  tokens.append('_'+token.ent_type_+'_')
      #else:
       # tokens.append(token.text)
        
  #  ents = doc.ents
   # for e in ents:
    #  if e.label_ in ['PERSON','GPE','ORG']:
     #   label = ' _'+e.label_+'_ '
      #  entity = re.escape(e.text)
       # text = re.sub(" "+entity+" ",label,text)

def filter_pieces():
  for y in range(2014,2024):
    year = str(y)
    print(year)
    data=[]
    directory = OUTPUT_DIR+year+'/article_data'
    #directory = '/projects/p31502/projects/gun_violence/community_justice/processed_data/test1/article_data'
    for i,filename in enumerate(os.listdir(directory)):
      f = os.path.join(directory,filename)
      if os.path.isfile(f) and i%4==segment:
        with open(f,'r') as infile:
          d=json.load(infile)
          #if len(d['article_metadata']['mentions']['race'])>0: 
          data.append(d)
    print(len(data)) 

def clean_masked():
  data=[]
  with open("./masked_names_new.csv",'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
      text = row['text'][10:].strip() 
      text = re.sub(" n\'t","n't",text)
      text = re.sub(" \'s","'s",text)
      text = re.sub("s \' ","s' ",text)
      text = re.sub(" \'re","'re",text)
      text = re.sub(" \'ve","'ve",text)
      text = re.sub(" \'d","'d",text)
      text = re.sub(" \. ",". ",text)
      text = re.sub(" , ",", ",text)
      sents = re.split("@ @ @ @ @ @ @ @ @ @|<p>|<h>",text)
      for s in sents:
        if len(s)>2:
          data.append({
            'article_id':row['article_id'],
            'text':s.strip()
          })
  with open("./masked_names_clean.csv",'w') as csvfile:
    writer = csv.DictWriter(csvfile,fieldnames=['article_id','text'])
    writer.writeheader()
    for d in data:
      writer.writerow(d)

#write_masks()
#clean_masked()

def parse_commandline():
    """Parse the arguments given on the command-line.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--year",
                       help="year",
                       default=None)


    args = parser.parse_args()

    return str(args.year)

if __name__ == '__main__':
  #year = parse_commandline()    
  print("masking")
  for y in range(2014,2024):
    year = str(y)
    write_masks(year,None,True,True)
    #for i in range(4):
     # write_masks(year,i)
 
        
      