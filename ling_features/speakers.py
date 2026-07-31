import json
import os
import re
from analysis_utils import last_name,get_name_variants

OUTPUT_DIR=JSON_DIR
import spacy
nlp = spacy.load('en_core_web_lg')

police_keywords=['police','officer','sheriff','deputy','cop','trooper','policeman','detective','sergeant','enforcement','lieutenant','investigator','patrol','capt','sgt','lt','superintendent']

personal_keywords=['cousin','aunt','uncle','mother','father','mom','dad','stepmom','stepdad','stepmother','stepfather','sister','stepsister','brother','stepbrother','son','stepson','daughter','stepdaughter','grandmother','grandfather','grandma','grandpa','niece','nephew','sibling','parent','grandparent','child','family','wife','husband','boyfriend','girlfriend','fiancee','friend','neighbor','colleague','coworker','boss','employer','employee', 'manager','relative']

#names of mayors of top ~10 most populous cities in US since 2020 (https://en.wikipedia.org/wiki/List_of_mayors_of_the_50_largest_cities_in_the_United_States)
local=['mayor','council']
local_names=['Bill de Blasio','Eric Garcetti','Lori Lightfoot','Sylvester Turner','Kate Gallego','Jim Kenney','Ron Nirenberg','Todd Gloria','Eric Johnson','Sam Liccardo','Steve Adler','Mike Duggan','Eric Adams','Karen Bass','Brandon Johnson','de Blasio']

#Presidents, VPs, majority/minority leaders of house/senate
national=['senator','representative','sen','president','pres','US','United States','U.S.','White House','senate','governor']
national_names=['Biden','Kamala Harris','Trump','Pence','McConnell','Schumer','Scalise','Jeffries','Pelosi']

media=['the daily beast','daily beast','the chronicle','business insider','vice news','the oregonian','good morning america','the inquirer','the herald','daily news','the baltimore sun']





def mask_speakers(d):
  """
  for y in range(2020,2021):
    year = str(y)
    print(year)
    directory = OUTPUT_DIR+year+'/article_data'
    for file_count,filename in enumerate(os.listdir(directory)):
      if file_count%250==0: 
        print(file_count)
      f = os.path.join(directory,filename)
      if os.path.isfile(f):# and int(re.sub('.json','',filename)) in ids:
        with open(f,'r') as infile:
          d=json.load(infile) 
          """
  if len(d['article_metadata']['mentions']['speakers'])==0:
    #continue
    return []
  masked_speakers={}
  replacements={}
  city=[]
  state=[]
  victims=[]
  shooters=[]
  victim_surnames=[]
  shooter_surnames=[]
  for i in d['incident_metadata']:
    if i.get('city',None): city.append(i['city'])
    if i.get('state',None): state.append(i['state'])
    for p in i['participants']:
      if p.get('name',None):
        if p.get('type',None):
          if p['type']=='victim':
            victims+=get_name_variants(p['name'])
            victim_surnames.append(last_name(p['name']))
          else:
            shooters+=get_name_variants(p['name'])
            shooter_surnames.append(last_name(p['name']))
  victim_surnames= list(filter(lambda x: x!=None,victim_surnames))
  shooter_surnames= list(filter(lambda x: x!=None,shooter_surnames))
  victims = list(set(victims))
  victims.sort(key=len, reverse=True)
  shooters = list(set(shooters))
  shooters.sort(key=len, reverse=True)      
  for s in d['article_metadata']['mentions']['speakers']:
    #text = s.strip()
    text = re.sub("\"","",s)
    text = text.strip()
    
    #try:
    
    for c in city:
      text = re.sub(re.escape(c),'incident_city',text, flags=re.IGNORECASE)
    for c in state:
      text = re.sub(re.escape(c),'incident_state',text, flags=re.IGNORECASE)
    for v in victims:
      text = re.sub(re.escape(v),'victim_name',text, flags=re.IGNORECASE)
    for v in shooters:
      text = re.sub(re.escape(v),'shooter_name',text, flags=re.IGNORECASE)
    for n in national_names:
      text = re.sub(re.escape(n),'national_politician',text, flags=re.IGNORECASE)
    for n in local_names:
      text = re.sub(re.escape(n),'local_politician',text, flags=re.IGNORECASE)
    for n in media:
      text = re.sub(re.escape(n),'media_outlet',text, flags=re.IGNORECASE)
    #except:
     # print("error",text)
      #print(text,city,state,victims,shooters,national_names,local_names,media)
    if len(text.split())==2 and last_name(text) in shooter_surnames:
      text = 'shooter_relation'
    if len(text.split())==2 and last_name(text) in victim_surnames:
      text = 'victim_relation'  
    doc = nlp(text)
    tokens = [k.lower_ for k in doc]
    is_police = any([p.lower() in tokens for p in police_keywords])
    is_personal = any([p.lower() in tokens for p in personal_keywords])
    is_local = any([p.lower() in tokens for p in local])
    is_national = any([p.lower() in tokens for p in national])

    #if len(doc.ents)==0 and doc[0].pos_=='PROPN':
     # temp=[t.text if (t.pos_!='PROPN' and "_" in t.text) else 'propn' for t in doc]
      #print("TESTING",text,'-->'," ".join(temp))
    for ent in doc.ents:
      ent_text=re.escape(re.sub('Sgt\.? |Lt\.? |Officer|Capt\.? ','',ent.text))
      if doc[ent.start].ent_type_=='GPE':
        text = re.sub(re.escape(ent.text),'place_name',text)
      elif doc[ent.start].ent_type_=='ORG' and not any([keyword in ent.text.lower() for keyword in ['house','senate','police','white house','department','sheriff','pd']]):
        text = re.sub(ent_text,'org_name',text)
      if doc[ent.start].ent_type_!='PERSON':
        #print(ent.text,doc[ent.start].ent_type_)
        continue
      if is_local:
        replacements[ent.text]='local_politician'
        text = re.sub(ent_text,'local_politician',text)
      elif is_national:
        replacements[ent.text]='national_politician'
        text = re.sub(ent_text,'national_politician',text)
      elif is_police:
        replacements[ent.text]='police_person'
        text = re.sub(ent_text,'police_person',text)
      elif is_personal:
        replacements[ent.text]='personal_connection'
        text = re.sub(ent_text,'personal_connection',text)
      elif any([n in ent.text for n in victim_surnames]):
        replacements[ent.text]='victim_relation'
        text = re.sub(ent_text,'victim_relation',text)
      elif any([n in ent.text for n in shooter_surnames]):
        replacements[ent.text]='shooter_relation'
        text = re.sub(ent_text,'shooter_relation',text)
      else:
        replacements[ent.text]='other_name'
        text = re.sub(ent_text,'other_name',text)
    text = re.sub(r'\w{0,3}pd','pd',text, flags=re.IGNORECASE)
    text = re.sub('\'s\S',' \'s ',text)
    text = re.sub('\'s',' \'s',text)
    text = re.sub(",",'',text)
    text = re.sub("\. ",' ',text)
    
    masked_speakers[s]=text 
  speakers=[]
  for s,text in masked_speakers.items():
    if (len(text.split())<2 and "_" not in text and text.lower() not in ['police','authorities','neighbor','neighbors']):# or any([a in text for a in ['long','hart','herold','beast']]):
      found = [a for a in replacements.keys() if text in a and text!=a]
      if len(found)>0:
        #print(s,"--",text,"--",found[0],"--",replacements[found[0]])
        speakers.append(replacements[found[0]])
    elif len(text.split())==2 and text.split()[0].lower() in ['lt','capt','captain','chief','sgt','sheriff']:
      speakers.append(text.split()[0]+" " + 'police_person')
    else:
      speakers.append(re.sub('white house','white_house',text,flags=re.IGNORECASE))
  #for s in speakers:
   # if "_" not in s and 'police' not in s.lower() and 'county' not in s.lower() and 'department' not in s.lower() or any([a in s.lower().split() for a in ['long','hart','herold','beast']]):
    #  print(s,doc[0].pos_)
  return speakers    

#mask_speakers()