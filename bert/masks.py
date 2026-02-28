import os,json,re 
import spacy
import csv
import sys
import pandas as pd
from spacy.matcher import DependencyMatcher
csv.field_size_limit(sys.maxsize)
nlp = spacy.load('en_core_web_lg')

INPUT_DIR = "/projects/p31502/projects/gun_violence/community_justice/processed/"
OUTPUT_DIR = "/projects/p31502/projects/gun_violence/community_justice/bert/masks/"


nouns=['prisoner','counterpart','teen','people','worker','member','kid','lawyer','victim','officer','wife','american','americans','neighbor','male','population','person','cop','woman','supremacist','family','community','church','mayor','boy','girl','mother','daughter','son','father','man','suspect','resident','teenager','parent','youth','child','leader','female','nationalism','supremacy','lives','life']

racial_identification = [
  {
    "RIGHT_ID": "race",
    #previously, LOWER was ORTH
    "RIGHT_ATTRS": {"POS": "ADJ","LOWER":{"IN":['white','black','asian','hispanic','latin','african','caucasian','latino','latina']},"DEP":"amod"}
  },
  {
    "RIGHT_ID": "entity",
    "RIGHT_ATTRS": {"POS":{"IN":["NOUN","PROPN"]},'LEMMA':{"IN":nouns}},
    "LEFT_ID": "race",
    "REL_OP": "<"
  }
]
racial_identification_prop = [
  {
    "RIGHT_ID": "race",
    #previously, LOWER was ORTH
    "RIGHT_ATTRS": {"POS": "PROPN","LOWER":{"IN":['white','black','asian','hispanic','latin','african','caucasian','latino','latina']},"DEP":"compound"}
  },
  {
    "RIGHT_ID": "entity",
    "RIGHT_ATTRS": {"POS":{"IN":["NOUN","PROPN"]},'LEMMA':{"IN":nouns}},
    "LEFT_ID": "race",
    "REL_OP": "<"
  }
]

matcher = DependencyMatcher(nlp.vocab)
matcher.add("race",[racial_identification,racial_identification_prop])



def get_data():
  for y in range(2014,2024):
    year = str(y)
    print(year)
    data=[]
    directory = INPUT_DIR+year+'/article_data'
    #directory = '/projects/p31502/projects/gun_violence/community_justice/processed_data/test1/article_data'
    for i,filename in enumerate(os.listdir(directory)):
      f = os.path.join(directory,filename)
      if os.path.isfile(f):# and i%4==segment:
        with open(f,'r') as infile:
          if i%1000==0: print(i)
          
          d=json.load(infile)
          if len(d["incident_term"]["short"])!=1:
            continue
          primary_id = d["incident_term"]["short"][0]
          
          text = d['article']
          text = re.sub('<p>','',text)
          text = re.sub("@ @ @ @ @ @ @ @ @ @","at_mask",text)
          text = re.sub(r'^@@\d+ ','',text)
          text = re.sub(r'\* \* \d+;\d+;TOOLONG',"",text)
          text = re.sub("& amp ;","&",text)
          text = re.sub("&lt;","<",text)
          text = re.sub("&gt;",">",text)
          text = re.sub('<h>','',text)
          words = text.split()
          words = [w if not w.isupper() else w.capitalize() for w in words]
          text = " ".join(words)
          #print(d['incident_metadata'])
          inc = [i for i in d['incident_metadata'] if i['id']==primary_id]
          if len(inc)<1 or d['article_metadata']['news_source'].get('scope',None)==None: 
            print(d['article_id'])
            continue
          white = float(inc[0]['nonhispanicwhite'])
          if white>40 and white<60:
            continue
            
          doc = nlp(text)
          matches = matcher(doc)
          race_tokens = [m[1][0] for m in matches]    
          #print(race_tokens)
          tokens = []
          for i,token in enumerate(doc):
            if i in race_tokens:
              tokens.append('race_mask')
            elif token.ent_type_ in ['PERSON','GPE','ORG','LOC','NORP']: 
              if token.ent_iob_=='B':
                tokens.append(token.ent_type_.lower()+"_mask")
            else:
              tokens.append(token.text)
          text = " ".join(tokens)
          text = re.sub("[ ]+",' ',text)
          """
          text = re.sub(" \. ",". ",text)
          text = re.sub(" , ",", ",text)
          text = re.sub(" : ",": ",text)
          text = re.sub(" - ","-",text)
          text = re.sub(" n\'t","n't",text)
          text = re.sub(" \'s","'s",text)
          text = re.sub("s \' ","s' ",text)
          text = re.sub(" \'re","'re",text)
          text = re.sub(" \'ve","'ve",text)
          text = re.sub(" \'d","'d",text) 
          """
          
          data.append({
            'article_id':d['article_id'],
            'text':text,
            'white':white,
            })
          
  
    df = pd.DataFrame(data)
    df['race']=df['white'].apply(lambda x: 0 if x<50 else 1)
    df.to_csv(OUTPUT_DIR+"updated_masks_"+year+'.csv',index=False)


get_data()