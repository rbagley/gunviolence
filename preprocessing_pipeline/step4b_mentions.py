from utils import get_name_variants,gather_keywords,last_name
from step4c_dependency_matching import get_matches
import re
import spacy
from config import *
nlp = spacy.load('en_core_web_lg')

var_titles=['Mr','Mrs','Ms','Dr','Sgt','Col','Lt']
exact_titles=['Miss','Officer','Sheriff','Deputy','Detective','Agent','Sergeant','Lieutenant']
titles = [t+"." for t in var_titles]+[t+' .' for t in var_titles]+var_titles+exact_titles

hedges = ["think", "thought", "thinking", "almost","apparent", "apparently", "appear", "appeared", "appears", "approximately", "around","assume", "assumed",  "claim", "claimed", "doubt", "doubtful", "essentially", "estimate","estimated", "feel", "felt", "frequently",  "generally", "guess", "indicate", "indicated","largely", "likely", "mainly", "may", "maybe", "might", "mostly", "often", "ought", "perhaps", "plausible", "plausibly", "possible", "possibly", "postulate","postulated", "presumable", "probable", "probably", "relatively", "roughly", "seems","should", "sometimes", "somewhat", "suggest", "suggested", "suppose", "suspect", "tends to", "typical", "typically", "uncertain", "uncertainly", "unclear", "unclearly","unlikely", "usually", "broadly", "presumably", "suggests", "fairly", "quite", "rather", "argue", "argues", "argued", "claims", "feels", "indicates", "supposed", "supposes", "postulates", "suspected","allege","alleged","allegedly"]

hedging_phrases=["certain amount", "certain extent", "certain level","from our perspective","in general", "in most cases", "in most instances", "in our view","on the whole","tend to","tended to", "from this perspective", "from my perspective", "in my view", "in this view", "in our opinion","in my opinion", "to my knowledge"]

family_keywords=['cousin','aunt','uncle','mother','father','mom','dad','stepmom','stepdad','stepmother','stepfather','sister','stepsister','brother','stepbrother','son','stepson','daughter','stepdaughter','grandmother','grandfather','grandma','grandpa','niece','nephew','sibling','parent','grandparent','child','family','wife','husband','boyfriend','girlfriend','fiancee']

death_keywords=['succumb','suicide','murder','manslaughter','slaughter','bloodshed','coroner','autopsy','funeral','grief','grieve','mourn','bereave','coffin','kill','killer','bury','fatal','dead','execution','death','morgue','die','homicide','demise','massacre','corpse','deceased','lethal','casualty','doa','passing','flatline']

mental_health_keywords = ['schizophrenia','schizophrenic','depression','depressed','anxiety','autism','autistic','insane','psychopath','sociopath','suicide','suicidal','psychiatric','psychological','ptsd','bipolar','asd','bpd','psychotic','psychosis','alcoholic','alcoholism','addict','addiction','ocd']

police_keywords=['police','officer','sheriff','deputy','cop','trooper','policeman','detective','sergeant','enforcement','lieutenant','investigator','patrol','capt','sgt','lt']

medical_keywords=['injury','injure','wound','ambulance','emt','medical','medicine','hospital','blood','bleed','heartbeat','surgery','icu','paramedic','paralysis','paralyze','concussion','tbi','stretcher','bandage','bodybag']

medical_phrases=['life support', 'critical condition', 'intensive care']

def get_mentions(sentences,incidents,text):
  policies=[]
  movements=[]
  organizations=[]
  mental_health=[]
  victims=[]
  shooters=[]
  children=[]
  family=[]
  police=[]
  legal=[]
  gang=[]
  bias=[]
  hedging=[]
  death=[]
  medical=[]
  victim_shooter_mentions={
    'victims':[],
    'shooters':[],
    'both':[]
  }
  about = [0]*len(incidents)
  keywords = [gather_keywords(i) for i in incidents]
  verbose=False
  lemmas=[]
#  if 'Michael Brown' in ' '.join(sentences):
 #   verbose=True
  #if verbose: print("Michael Brown:",keywords)
  for doc in sentences:
    #doc = nlp(text)
    lemmas+=[token.lemma_ for token in doc]
    sents = [sent.text.strip() for sent in doc.sents]
    for s in sents:
      for i,k in enumerate(keywords):
        if any([keyword.lower() in s.lower().split() for keyword in k]):
          about[i]+=1
          #if verbose: print(about[i])
    #print(list(doc.noun_chunks))
    temp_vics=get_vics(doc.noun_chunks,incidents)
    for key in victim_shooter_mentions.keys():
      victim_shooter_mentions[key]+=temp_vics[key]
    for i,token in enumerate(doc):
      if token.text.lower()=='permit'and token.pos_=='NOUN':
        policies.append('permit')
      elif token.lower_=='amendment':
        policies.append('amendment')
      elif token.lower_=='nra':
        organizations.append("NRA")
      elif token.lower_=='aclu':
        organizations.append("ACLU")
      elif token.lower_=='csgv':
        organizations.append("CSGV")
      elif token.lower_=='legislation':
        policies.append("legislation")
      elif token.lower_=='blm':
        movements.append('BLM')
      elif token.lower_ in hedges:
        hedging.append(token.lower_)
      elif token.lemma_ in death_keywords:
        death.append(token.lower_)
      elif token.lemma_ in ['activist','activism','protest']:
        movements.append(token.lower_)
      elif token.lemma_ in ['racism','racist','bias','biased','supremacy','supremacist']:
        bias.append(token.lower_)
      elif token.lemma_ in ['gang','gangster','thug']:
        gang.append(token.lower_)
      elif token.lemma_ in family_keywords:
        family.append(token.lower_)
      elif token.lemma_ in medical_keywords:
        medical.append(token.lower_)
      elif token.lemma_ in ['girl','boy','kid','child','juvenile','youth','teen','teenager','baby'] and token.pos_=='NOUN':
        children.append(token.lower_)
      elif token.lemma_ in police_keywords:
        if i==0 or doc[i-1].lemma_ not in police_keywords:
          if len(doc)>i+1 and doc[i+1].lemma_ in police_keywords:
            police.append(doc[i:i+2].text)
          else:
            police.append(token.lower_)
      elif token.lemma_ in ['judge','attorney','bailiff','lawyer']:
        legal.append(token.lower_)
      elif token.lemma_ in ['shooter','killer','murderer','perpetrator','attacker','assailant']:
        shooters.append(token.lower_)
      elif token.lemma_ in ['victim','casualty','fatality']:
        victims.append(token.lower_)
      elif token.lower_ in mental_health_keywords:
        mental_health.append(token.lower_)
      elif len(doc)>i+1:
        if token.lower_=='open' and doc[i+1].lower_=='carry':
          policies.append('open carry')
        elif token.lower_=='public' and (doc[i+1].lower_=='defender' or doc[i+1].lower_=='defenders'):
          legal.append('public defender')
        elif token.lemma_=='pass' and doc[i+1].lower_ =='away':
          death.append('pass away')
        elif token.lemma_=='life' and doc[i+1].lower_ =='lost':
          death.append('life lost')
        elif token.lemma_=='pronounce' and doc[i+1].lower_=='dead':
          death.append('pronounce dead')
        elif token.lower_=='background' and doc[i+1].lower_=='check':
          policies.append('background check')
        elif token.lower_=='concealed' and doc[i+1].lower_=='carry':
          policies.append('concealed carry')
        elif token.lower_=='gun' and doc[i+1].lower_=='control':
          policies.append('gun control')
        elif token.lower_=='gun' and (doc[i+1].lower_=='law' or doc[i+1].lower_=='laws'):
          policies.append('gun law')
        elif token.lower_=='gun' and doc[i+1].lower_=='rights':
          policies.append('gun rights')
        elif token.lower_=='body' and doc[i+1].lemma_=='bag':
          medical.append('body bag')
        elif token.lower_ in ['operating','emergency'] and doc[i+1].lemma_=='room':
          medical.append(doc[i:i+2].text)
        elif token.lemma_=='social' and doc[i+1].lemma_=='movement':
          movements.append('social movement')
        elif token.lower_=='waiting' and doc[i+1].lower_=='period':
          policies.append('waiting period')
        elif token.lower_=='red' and doc[i+1].lower_=='flag':
          policies.append('red flag')
        elif token.lower_=='proposed' and (doc[i+1].lower_=='bill' or doc[i+1].lower_=='bills'):
          policies.append('proposed bill')
        elif token.lower_=='mental' and doc[i+1].lower_=='health':
          mental_health.append('mental health')
        elif token.lower_=='mental' and doc[i+1].lower_=='hospital':
          mental_health.append('mental hospital')
        elif token.lower_=='mental' and doc[i+1].lower_=='illness':
          mental_health.append('mental illness')
        elif token.lower_=='mentally' and doc[i+1].lower_=='ill':
          mental_health.append('mentally ill')
        elif token.lemma_=='heart' and doc[i+1].lemma_=='stop':
          death.append('heart stopped')
        elif len(doc)>i+2:
          if token.lemma_ in ['loss','lose'] and doc[i+2].lemma_=='life':
            death.append(doc[i:i+3].text)
          elif token.lemma_ in ['find','lose'] and doc[i+2].lemma_=='heartbeat':
            death.append(doc[i:i+3].text)
  text = text.lower()
  for i in range(text.count('black lives matter')):
    movements.append("BLM")
  for i in range(text.count('blue lives matter')):
    movements.append("blue lives matter")
  for i in range(text.count('defund the police')):
    movements.append("defund the police")
  for phrase in hedging_phrases:
    for i in range(text.count(phrase)):
      hedging.append(phrase)
  for phrase in medical_phrases:
    for i in range(text.count(phrase)):
      medical.append(phrase)
  for i in range(text.count('moms demand action')):
    movements.append("moms demand action")
  for i in range(text.count('march for our lives')):
    movements.append("march for our lives")
  for i in range(text.count('national rifle association')):
    organizations.append("national rifle association")
#  if 'black lives matter' in text:
 #   movements.append("BLM")
  #if 'blue lives matter' in text:
   # movements.append("blue lives matter")
#  if 'defund the police' in text:
 #   movements.append('defund the police')
  #if 'moms demand action' in text:
   # movements.append('moms demand action')
#  if 'march for our lives' in text:
 #   movements.append("march for our lives")
  #if 'national rifle association' in text:
   # organizations.append("NRA")
  #if len(victim_shooter_mentions['victims'])==0 and len(victim_shooter_mentions['shooters'])==0:
   # print(keywords)
    #print(' '.join(sentences))
    #print(incidents)
  return policies,movements,organizations,mental_health,victim_shooter_mentions,victims,shooters,about,lemmas,family,children,police,legal,gang,bias,hedging,death,medical


  

def get_vics(nouns,incidents):

  victims=[]
  victims_last=[]
  shooters=[]
  shooters_last=[]
  both=[]
  mentions={
    'victims':[],
    'shooters':[],
    'both':[]
  }
  #print([n for n in nouns])
  for i in incidents:
    for p in i['participants']:
      if 'name' in p.keys() and 'type' in p.keys():
        if p['type']=='victim':
          victims=victims+[n.lower() for n in get_name_variants(p['name'])]
          last=last_name(p['name'])
          if last:
            victims_last.append(last)
            victims+=[t + " " + last for t in titles]
        elif p['name'] and p['type']!='victim':
          shooters=shooters+[n.lower() for n in get_name_variants(p['name'])]
          last=last_name(p['name'])
          if last:
            shooters_last.append(last)
            shooters+=[t + " " + last for t in titles]
      if 'name' in p.keys():
        both = both+[n.lower() for n in get_name_variants(p['name'])]
  
  victims= list(set(victims))
  shooters = list(set(shooters))
  for name in nouns:
    n=name.text.lower()
    found_victim=False
    found_shooter=False
    for v in victims:
      if v.lower() in n:
    #if n in victims:
        #mentions['victims'].append(name.text)
        found_victim=True
    for s in shooters:
      if s.lower() in n:
    #elif n in shooters:
        #mentions['shooters'].append(name.text)
        found_shooter=True
    if n in shooters_last:#any([t.lower_ in shooters_last for t in name]):#n in shooters_last:
      #mentions['shooters'].append(name.text)
      found_shooter=True
    if n in victims_last: #any([t.lower_ in victims_last for t in name]):#n in victims_last:
      #mentions['victims'].append(name.text)
      found_victim=True
    if found_victim:
      mentions['victims'].append(name.text)
    if found_shooter:
      mentions['shooters'].append(name.text)
    if found_victim or found_shooter:
      mentions['both'].append(name.text)
  #print(victims,victims_last,shooters,shooters_last,mentions)
  return mentions

def get_children(noun_results):
  nouns = list(set(noun_results['nouns']+noun_results['entities']+noun_results['speakers']))
  children = []
  for name in nouns:
    n= name.lower()
    if ('year' in n and 'old' in n and parse_age(n,18)):
      children.append(name)
  return children

def parse_age(n,age):
  text = re.split("-| ",n)
  found_age = False
  for t in text:
    if re.fullmatch(r'\d+',t) and int(t)<age:
      found_age = True
  return found_age
      
def get_family(noun_results):
  nouns = list(set(noun_results['nouns']+noun_results['entities']+noun_results['speakers']))
  family = []
  for name in nouns:
    n= name.lower()
    if 'cousin' in n or 'aunt' in n or 'uncle' in n or 'mother' in n or 'father' in n or 'mom' in n or 'dad' in n or 'brother' in n or 'sister' in n or 'niece' in n or 'nephew' in n or 'daughter' in n or 'son' in n:
      family.append(name)
  return family
  
def get_police(noun_results):
  nouns = list(set(noun_results['nouns']+noun_results['entities']+noun_results['speakers']))
  police = []
  legal=[]
  for name in nouns:
    n= name.lower()
    if 'police' in n or 'sheriff' in n or 'deputy' in n:
      police.append(name)
    if 'judge' in n or 'lawyer' in n or 'attorney' in n or 'bailiff' in n or 'public defender' in n:
      legal.append(name)
  return police,legal
  
def get_policy(text):
  mentions=[]
  for n in ['gun control','background check','red flag','gun rights','gun law','concealed carry','permit','legislation','permitless carry','amendment']:
    if n in text.lower():
       mentions.append(n)
  return mentions
  
  
def get_victim_shooter(noun_results,incidents):
  #print(noun_results)
  nouns = (noun_results['nouns']+noun_results['entities']+noun_results['speakers'])
  victims=[]
  shooters=[]
  both=[]
  mentions={
    'victims':[],
    'shooters':[],
    'both':[]
  }
  for i in incidents:
    for p in i['participants']:
      if 'name' in p.keys() and 'type' in p.keys():
        if p['type']=='victim':
          victims=victims+[n.lower() for n in get_name_variants(p['name'])]
        elif p['name'] and p['type']!='victim':
          shooters=shooters+[n.lower() for n in get_name_variants(p['name'])]
      if 'name' in p.keys():
        both = both+[n.lower() for n in get_name_variants(p['name'])]
  #print(victims,shooters, both)
  for name in nouns:
    n=name.lower()
    if n in victims:
      mentions['victims'].append(name)
    elif n in shooters:
      mentions['shooters'].append(name)
    if n in both:
      mentions['both'].append(name)
  #print(mentions)
  return mentions
      
def collect_mentions(text,incidents):
  
  #victims_shooters = get_victim_shooter(results,incidents)
  text = text[10:].strip() if not IS_VIDEOS else text.strip()
  text = re.sub(" n\'t","n't",text)
  text = re.sub(" \'s","'s",text)
  text = re.sub("s \' ","s' ",text)
  text = re.sub(" \'re","'re",text)
  text = re.sub(" \'ve","'ve",text)
  text = re.sub(" \'d","'d",text)
  text = re.sub(" \. ",". ",text)
  text = re.sub(" , ",", ",text)
  text = re.sub(r'Sgt.',r'Sgt',text)
  text = re.sub(r'Lt.',r'Lt',text)
  sents = re.split("@ @ @ @ @ @ @ @ @ @|<p>|<h>",text) if not IS_VIDEOS else re.split(">>|> >",text)
  docs=[]
  sentences=[]
  for s in sents:
    doc = nlp(s)
    docs.append(doc)
    for s in doc.sents:
      sentences.append(s.text)
  results = get_matches(docs,sents)
  policies,movements,organizations,mental_health,victims_shooters,victims,shooters,about,lemmas,family,children, police,legal,gang,bias,hedging,death,medical=get_mentions(docs,incidents,text)
  #police,legal = get_police(results)
  mentions={
    'children':children+get_children(results),
    'family':family,#get_family(results),
    'police':police,
    'legal':legal,
    'victims': victims_shooters['victims'],
    'shooters': victims_shooters['shooters'],
    'nameless_victims':victims,
    'nameless_shooters':shooters,
    'participants': victims_shooters['both'],
    'speakers': results['speakers'],
    'policy': policies,
    'movement':movements,
    'organizations':organizations,
    'mental_health':mental_health,
    'race': results['race'],
    'gangs':gang,
    'bias':bias,
    'aboutness':about,
    'hedging':hedging,
    'death':death,
    'medical':medical
  }
  victims=[]
  shooters=[]
  found_victims=[]
  found_shooters=[]
  for i in incidents:
    for p in i['participants']:
      if p.get('type',None) and p.get('name',None):
        if p['type']=='victim':
          victims.append(p['name'])
        elif p['type']=='perpetrator':
          shooters.append(p['name'])
        else:
          print(p['type'])
  #print(victims,shooters)
  for v in mentions['victims']:
    for vic in victims:
      variants = get_name_variants(vic.lower(),True)
      if v.strip().lower() in variants or any([var in v.strip().lower() for var in variants]):
        found_victims.append(vic)
  for s in mentions['shooters']:
    for sh in shooters:
      variants = get_name_variants(sh.lower(),True)
      if s.strip().lower() in variants or any([var in s.strip().lower() for var in variants]):
        found_shooters.append(sh)
  mentions['victims_set'] = list(set(found_victims))
  mentions['shooters_set']= list(set(found_shooters))
  #print(mentions)
  return mentions,' '.join(lemmas),sentences