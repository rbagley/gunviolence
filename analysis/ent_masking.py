import os
import json
from config import *
print(OUTPUT_DIR)
#import torch
#print(torch.cuda.is_available())

import re
import spacy
print("gpu:",spacy.prefer_gpu())
nlp = spacy.load('en_core_web_lg')
import csv
from embeddings import get_name_variants
import argparse
import pandas as pd

keywords=['police','cop','officer','sheriff','deputy','trooper','detective','sergeant','agent','enforcement','lieutenant','polices','investigator','cops','sheriffs','deputies','troopers','detectives','agents','agency','investigators','officers','patrol','k-9','patrols','department','fbi','pd','911','official','officials','capt','lt','sgt','col','colonel']

def filter_list(l):
  filtered=[l[0]]
  for i in l[1:]:
    if filtered[-1]==i and i in ['victim_name','shooter_name','police_name']:
      continue
    else:
      filtered+=i
  return filtered

def write_masks(year,segment,paragraphs=False,police_group=False):
  #nlp = spacy.load('en_core_web_lg')
  
  #for y in range(2014,2024):
   # year = str(y)
  print(year)
  data=[]
  
  directory = OUTPUT_DIR+year+'/article_data'
  #if os.exists(directory):
  
  for i,filename in enumerate(os.listdir(directory)):
    f = os.path.join(directory,filename)
    if os.path.isfile(f) and (i%4==segment or segment==None):
      with open(f,'r') as infile:
        d=json.load(infile)
        #if len(d['article_metadata']['mentions']['race'])>0: 
        data.append(d)
  print(len(data)) 
  sentences=[]
  masks = []
  for i,d in enumerate(data):
    if d['article_id']=='2362909':
      continue
    if i%250==0:
      print(i)
    #if i%4!=segment:
     # continue
    
    names={
      'shooter':[],
      'victim':[],
      'police':[]
    }
    variants={
      'shooter':[],
      'victim':[],
      'police':[]
    }
    titled_variants={
      'shooter':[],
      'victim':[],
      'police':[]
    }
    check_officer=False

    for incident in d['incident_metadata']:
      for p in incident['participants']:
        if p.get('name',None)!=None and p.get('type',None)!=None:
          #print(p['name'].lower(),any([name for name in ['officer','capt','sgt','police'] if name in p['name'].lower()]))
          if 'agent' in p['name'].lower():
              check_officer='agent'
          if police_group and any([name for name in ['officer','capt','sgt','police'] if name in p['name'].lower().split()]):
            if 'officer' in p['name'].lower():
              check_officer='officer'
            names['police'].append(p['name'])
            if p['name'].lower() not in ['officer','detective']:
              namevars,titlevars=get_name_variants(p['name'],p.get('gender',None))
              variants['police']+=namevars
              titled_variants['police']+=titlevars
            #print("police")
          elif p['type']=='victim':
            names['victim'].append(p['name'])
            namevars,titlevars=get_name_variants(p['name'],p.get('gender',None))
            variants['victim']+=namevars
            titled_variants['victim']+=titlevars
            #print("victim")
          else:
            names['shooter'].append(p['name'])
            namevars,titlevars=get_name_variants(p['name'],p.get('gender',None))
            variants['shooter']+=namevars
            titled_variants['shooter']+=titlevars
    if paragraphs:
      text = d['article']
      text= re.sub("< h >","<h>",text)
      text = re.sub("< p >","<p>",text)
      text = re.sub(r'^@@\d+ <[hp]>','',text)
      pieces = re.split(r'<[ph]> (\d+|Your)? [Cc]omments?|<[ph]>[ ?]Thank you for visiting|<[ph]>[ ?]More [Hh]eadlines|<[ph]> Rules of Conduct|This section is for comments|[Oo]ur [Tt]erms of ([Uu]se|[Ss]ervice)|(^|<[ph]> )The views expressed are not those of|<[hp]> To post a comment|<[hp]> We welcome comments|By posting your comments|Top Comments|<[hp]> Recommended for [Yy]ou|<[hp]> Comment policy( :)?',text)
      text = pieces[0]
      chunks = re.split('@ @ @ @ @ @ @ @ @ @|<[hp]>',text)
      #bits=re.split('< [hp] >',text)
    else:
      chunks=[]
      for s in d['article_metadata']['sentences']:
        for piece in s.split("@ @ @ @ @ @ @ @ @ @"):
          chunks.append(piece)
    for text in chunks:
      #if 'Ezell Ford' in text: print(variants)
      if len(text.split())<2:
        continue
      text = text.strip()
      for role in variants.keys():
        for t in titled_variants[role]:
          if IS_VIDEOS:
            text = re.sub(re.escape(t),role+"_name",text, flags=re.I)
          else:
           text = re.sub(re.escape(t),role+"_name",text)
      full_doc = nlp(text)
      for doc in full_doc.sents:
        pos = [t.pos_ for t in doc]
        if ('VERB' not in pos and 'AUX' not in pos) and len(doc)<5:
          continue
        words = [t.text for t in doc]
        #print(doc.ents)
        for role in variants.keys():
          #print(variants[role])
          for ent in doc.ents:
            if ent.text.lower() in [x.lower() for x in variants[role]]:
              for i in range((ent.start-doc.start),(ent.end-doc.start)):
                words[i]=role+'_name'
            #else:
             # if ent.text in variants[role]:
              #  for i in range(ent.start,ent.end):
               #   words[i]=role+'_name'
        if check_officer!=None:
          for i,t in enumerate(doc):
            if t.lower_ == check_officer and (i==len(doc)-1 or doc[i+1].ent_type_==''):
              words[i]='police_name'
              if i>0 and doc[i-1].pos_=='ADJ':
                words[i-1]='police_name'
          for ent in doc.ents:
            if (ent.end-doc.start)<len(words) and words[(ent.end-doc.start)].lower() in ['officer','police_name']:
              for i in range((ent.start-doc.start),(ent.end-doc.start)):
                words[i]='police_name'
            if (ent.end-doc.start)> len(words):
              print((ent.end-doc.start),len(words))
        
        text = " ".join(words)
        text = re.sub("("+role+"_name )+",role+"_name ",text)
      
        masks.append({
          'article_id':d['article_id'],
          'text': text,
          'lemmas':" ".join([x.lemma_ for x in doc])
        })
    if i%500==0:
      df = pd.DataFrame(masks)
      df.to_csv(masking_dir+"masked_sentences_"+year+".csv",index=None)
#def last():            
  print(len(masks),len(sentences))
  if not os.path.exists(masking_dir):
    os.makedirs(masking_dir)
  df = pd.DataFrame(masks)
  df.to_csv(masking_dir+"masked_sentences_"+year+".csv",index=None)

      


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
  year = parse_commandline()    

  write_masks(year,None,True,True)
 
  #for y in range(2014,2024):
   # year = str(y)
    #write_masks(year,None,False,True)
