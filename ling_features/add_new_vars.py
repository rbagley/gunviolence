import json,os,csv
csv.field_size_limit(1000000)
from speakers import mask_speakers
import spacy
nlp = spacy.load('en_core_web_sm')
import pandas as pd

from config import OUTPUT_DIR,path


INPUT_DIR=OUTPUT_DIR
OUTPUT_DIR = path

safety_keywords=['danger','safety','safe','unsafe','security','protect','protection']

family_keywords=['cousin','aunt','uncle','mother','father','mom','dad','stepmom','stepdad','stepmother','stepfather','sister','stepsister','brother','stepbrother','son','stepson','daughter','stepdaughter','grandmother','grandfather','grandma','grandpa','niece','nephew','sibling','parent','grandparent','child','family','wife','husband','boyfriend','girlfriend','fiancee','fiance']

role_keywords=['friend','neighbor','boss','employee','student','teacher','resident','member','coach','teammate','team','mentor','leader','volunteer']

implicit_race=['thug','thuggery','thugs','gang','gangs','gangsters','gangster','gangbanger','gangbangers','terrorist','terrorists','terrorism']

#legal_keywords=['judge','lawyer','attorney','bailiff','court','courthouse','lawsuit','bail','appeal','arraignment','accused','warrant','felony','arrest','conviction','evidence','defendant','jury','parole','parolee','plaintiff','prosecutor','witness','public defender']
legal_keywords=['court','courthouse','lawsuit','bail','appeal','arraignment','warrant','felony','arrest','conviction','evidence','parole','homicide','manslaughter']

legal_people=['judge','lawyer','attorney','bailiff','defendant','jury','parolee','plaintiff','prosecutor','witness','public defender']


def get_speakers(d):
  speakers = mask_speakers(d)
  nat=0
  local=0
  relation=0
  other=0
  police=0
  for s in speakers:
    if 'national_' in s or 'white_house' in s:
      nat+=1
    elif 'local_' in s or 'incident_' in s or 'media_outlet' in s:
      local+=1
    elif 'personal_' in s or 'victim_' in s or 'shooter_' in s:
      relation+=1
    elif any([x for x in ['police','sheriff','pd','sgt','capt','chief','commissioner'] if x in s.lower()]):
      police+=1
    else:
      #print(s)
      other+=1
  return nat,local, relation,other,police


def save_speakers():
  data=[]
  for y in range(2014,2024):
    year = str(y)
    print(year)
    directory = INPUT_DIR+year+'/article_data'
    if not os.path.isdir(directory): continue
    for file_count,filename in enumerate(os.listdir(directory)):
      if file_count%250==0: 
        print(file_count)
      f = os.path.join(directory,filename)
      
      with open(f,'r') as infile:
        d=json.load(infile)
        nat,local, relation,other,police = get_speakers(d)
        #count,safety = get_number_count(d)
        racialized = [x for x in d['article'].split(' ') if x.lower() in implicit_race]
        data.append({
          'article_id': d['article_id'],
          'speakers_national':nat,
          'speakers_local': local,
          'speakers_personal': relation,
          'speakers_police': police,
          'speakers_other': other,
          'racialized_mention':len(racialized)
        })
          
    df = pd.DataFrame(data)
    df.to_csv(OUTPUT_DIR+"speakers_updated.csv",index=False)

def add_new():
  data=[] 
  for y in range(2014,2024):
    year = str(y)
    print(year,len(data))
    if not os.path.isfile(INPUT_DIR+"csvs/masking/masked_"+year+".csv"): continue
    with open(INPUT_DIR+"csvs/masking/masked_"+year+".csv",'r') as csvfile:
      reader = csv.DictReader(csvfile)
      for i,row in enumerate(reader):
        #if i>4200:print(i)
        role=0
        family=0
        safety=0
        legal=0
        legal_person=0
        if 'victim_name' not in row['lemmas'] and 'shooter_name' not in row['lemmas'] and 'police_name' not in row['lemmas']:
          continue
        
        for t in row['lemmas'].split():
          if t.lower() in role_keywords:
            role+=1
          if t.lower() in family_keywords:
            family+=1
          if t.lower() in safety_keywords:
            safety+=1
          if t.lower() in legal_keywords:
            legal+=1
          if t.lower() in legal_people:
            legal_person+=1
         
        data.append({
          'article_id':row['article_id'],
          'role_mention':role,
          'family_strict_mention':family,
          'safety_mention':safety,
          'legal_nonperson_mention':legal,
          'legal_person_mention':legal_person
        })
        """
        role,family,strict_role,strict_family = get_human(row['text'])
        data.append({
          'article_id':row['article_id'],
          'role_mention':role,
          'family_strict_mention':family,
          'role_strict_mention':strict_role,
          'family_stricter_mention':strict_family
        })
        """
  df = pd.DataFrame(data)
  df.to_csv(OUTPUT_DIR+"human_full_updated.csv",index=False)
  
def combine():
  df = pd.read_csv(OUTPUT_DIR+"human_full_updated.csv")
  print(df.shape)
  df=df.groupby('article_id').agg('sum')
  df.to_csv(OUTPUT_DIR+"human.csv")
  print(df.shape)
  
save_speakers()
add_new()
combine()