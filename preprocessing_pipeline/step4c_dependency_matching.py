from spacy.matcher import DependencyMatcher
import spacy
import re
nlp = spacy.load('en_core_web_lg')

verbs = ['say','state','add','identify','call','tell','observe','describe','report','mention','remark','discuss','acknowledge','demonstrate','support', 'clarify','recognize','accept']


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


entity_said = [
  {
    "RIGHT_ID": "being",
    "RIGHT_ATTRS": {"POS": "NOUN","DEP":"nsubj"}
  },
  {
    "RIGHT_ID": "verb",
    "RIGHT_ATTRS": {"POS":"VERB","LEMMA":{"IN":verbs},"DEP":"ROOT"},
    "LEFT_ID": "being",
    "REL_OP": "<"
  }
]

full_name=[
  # anchor token: compound name
  {
    "RIGHT_ID": "lastname",
    "RIGHT_ATTRS": {"POS": "PROPN"}
  },
  # lastname -> firstname
  {  # firstname < lastname
    "LEFT_ID": "lastname",
    "REL_OP": ";",
    "RIGHT_ID": "middlename",
    "RIGHT_ATTRS": {"DEP": "compound", "POS":"PROPN"}
  }, 
  {  # firstname < lastname
    "LEFT_ID": "lastname",
    "REL_OP": ">",
    "RIGHT_ID": "firstname",
    "RIGHT_ATTRS": {"DEP": "compound", "POS":"PROPN"}
  }
]


fname_lname=[
  # anchor token: compound name
  {
    "RIGHT_ID": "lastname",
    "RIGHT_ATTRS": {"POS": "PROPN"}
  },
  # lastname -> firstname
  {  # firstname < lastname
    "LEFT_ID": "lastname",
    "REL_OP": ">",
    "RIGHT_ID": "firstname",
    "RIGHT_ATTRS": {"DEP": "compound", "POS":"PROPN"}
  }
]

name_said = [
  # anchor token: compound name
  {
    "RIGHT_ID": "lastname",
    "RIGHT_ATTRS": {"POS": "PROPN","DEP":"nsubj"}
  },
    {
        "RIGHT_ID": "verb",
        "RIGHT_ATTRS": {"POS":"VERB","LEMMA":{"IN":verbs}},
        "LEFT_ID": "lastname",
        "REL_OP": "<"
        }
]

fname_lname_said = [
  # anchor token: compound name
  {
    "RIGHT_ID": "lastname",
    "RIGHT_ATTRS": {"POS": "PROPN",'DEP':{'NOT_IN':['nsubjpass']}}
  },
  # lastname -> firstname
  {  # firstname < lastname
    "LEFT_ID": "lastname",
    "REL_OP": ">",
    "RIGHT_ID": "firstname",
    "RIGHT_ATTRS": {"DEP": "compound", "POS":"PROPN"}
  },
    {
        "RIGHT_ID": "verb",
        "RIGHT_ATTRS": {"POS":"VERB","LEMMA":{"IN":verbs}},
        "LEFT_ID": "lastname",
        "REL_OP": "<"
        }
]


person_appositive = [
  # anchor token: compound name
  {
    "RIGHT_ID": "lastname",
    "RIGHT_ATTRS": {"POS": "PROPN",'DEP':{'NOT_IN':['nsubjpass']}}
  },
  # lastname -> firstname
  {  # firstname < lastname
    "LEFT_ID": "lastname",
    "REL_OP": ">",
    "RIGHT_ID": "firstname",
    "RIGHT_ATTRS": {"DEP": "compound", "POS":"PROPN"}
  },
  {
    "RIGHT_ID": "verb",
    "RIGHT_ATTRS": {"POS":"VERB","LEMMA":{"IN":verbs}},
    "LEFT_ID": "lastname",
    "REL_OP": "<"
  },
  {
    "RIGHT_ID": "app",
    "RIGHT_ATTRS": {"DEP":"appos"},
    "LEFT_ID": "lastname",
    "REL_OP": ">"
  },
  {
    "RIGHT_ID": "modifier",
    "RIGHT_ATTRS": {"DEP":"compound"},
    "LEFT_ID": "app",
    "REL_OP": ">"
  }
]

person_title = [
  # anchor token: compound name
  {
    "RIGHT_ID": "lastname",
    "RIGHT_ATTRS": {"POS": "PROPN",'DEP':{'NOT_IN':['nsubjpass']}}
  },
  # lastname -> firstname
  {  # firstname < lastname
    "LEFT_ID": "lastname",
    "REL_OP": ">",
    "RIGHT_ID": "firstname",
    "RIGHT_ATTRS": {"DEP": "compound", "POS":"PROPN"}
  },
  {
    "RIGHT_ID": "verb",
    "RIGHT_ATTRS": {"POS":"VERB","LEMMA":{"IN":verbs}},
    "LEFT_ID": "lastname",
    "REL_OP": "<"
  },
  {
    "RIGHT_ID": "title",
    "RIGHT_ATTRS": {"DEP":"nmod"},
    "LEFT_ID": "lastname",
    "REL_OP": ">"
  }
]

person_of_group_said = [
  # anchor token: compound name
  {
    "RIGHT_ID": "lastname",
    "RIGHT_ATTRS": {"POS": "PROPN",'DEP':{'NOT_IN':['nsubjpass']}}
  },
  # lastname -> firstname
  {  # firstname < lastname
    "LEFT_ID": "lastname",
    "REL_OP": ">",
    "RIGHT_ID": "firstname",
    "RIGHT_ATTRS": {"DEP": "compound", "POS":"PROPN"}
  },
  {
    "RIGHT_ID": "verb",
    "RIGHT_ATTRS": {"POS":"VERB","LEMMA":{"IN":verbs}},
    "LEFT_ID": "lastname",
    "REL_OP": "<"
  },
  {
    "RIGHT_ID": "prep",
    "RIGHT_ATTRS": {"DEP":"prep","POS":"ADP"},
    "LEFT_ID": "lastname",
    "REL_OP": ">"
  },
  {
    "RIGHT_ID": "org",
    "RIGHT_ATTRS": {"DEP":'pobj'},
    "LEFT_ID": "prep",
    "REL_OP": ">"
  },
  {
    "RIGHT_ID": "org_modifier",
    "RIGHT_ATTRS": {"DEP":'compound'},
    "LEFT_ID": "org",
    "REL_OP": ">"
  }
]

person_verbing_group=[
  # anchor token: compound name
  {
    "RIGHT_ID": "lastname",
    "RIGHT_ATTRS": {"POS": "PROPN",'DEP':{'NOT_IN':['nsubjpass']}}
  },
  # lastname -> firstname
  {  # firstname < lastname
    "LEFT_ID": "lastname",
    "REL_OP": ">",
    "RIGHT_ID": "firstname",
    "RIGHT_ATTRS": {"DEP": "compound", "POS":"PROPN"}
  },
  {
    "RIGHT_ID": "verb",
    "RIGHT_ATTRS": {"POS":"VERB","LEMMA":{"IN":verbs}},
    "LEFT_ID": "lastname",
    "REL_OP": "<"
  },
  {
    "RIGHT_ID": "relcl",
    "RIGHT_ATTRS": {"DEP":"relcl","POS":"VERB"},
    "LEFT_ID": "lastname",
    "REL_OP": ">"
  },
  {
    "RIGHT_ID": "org",
    "RIGHT_ATTRS": {"DEP":'dobj'},
    "LEFT_ID": "relcl",
    "REL_OP": ">"
  },
  {
    "RIGHT_ID": "org_modifier",
    "RIGHT_ATTRS": {"DEP":'compound'},
    "LEFT_ID": "org",
    "REL_OP": ">"
  }
]

#records = []
#with open("/projects/p31502/projects/gun_violence/sorted_articles/quotes.txt",'r') as infile:
 # for row in infile:
  #  records.append(row)

def format_names(doc,matches):
  names = []
  for m in matches:
    names.append(str(doc[m[1][1]]).lower()+" "+str(doc[m[1][0]]).lower())
  return names
  
def check_for_names(t,names):
  found = t
  for n in names:
    if n in t:
      found = True
  return found
  
def get_nouns(doc):
  nouns=[]
  noun_chunks = doc.noun_chunks
  matcher = DependencyMatcher(nlp.vocab)
  matcher.add("nouns",[entity_said])
  matches = matcher(doc)
  for m in matches:
    index = m[1][0]
    match = doc[index].text
    if len(doc)>index+2 and index-2>=0:
      phrase = doc[index-2].text+" "+doc[index-1].text+" "+doc[index].text+" "+doc[index+1].text+" "+doc[index+2].text
    else:
      phrase = doc[index].text
    for n in noun_chunks:
      if n.text.lower() in phrase.lower() and doc[index].text.lower() in n.text.lower() and len(n.text)>len(match):
        match = n.text
    nouns.append(match.lower())
  nouns = nouns+get_names(doc)
  return list(set(nouns))
  
def get_names(doc):
  matcher = DependencyMatcher(nlp.vocab)
  matcher.add("names",[fname_lname,full_name])
  matches = matcher(doc)
  names3indices=[]
  names2indices=[]
  names3= []
  names2=[]
  for m in matches:
    if len(m[1])==3 and m[1][1]!=m[1][2]:
      name = str(doc[m[1][2]])+" "+str(doc[m[1][1]])+" "+str(doc[m[1][0]])
      names3.append(name.lower())
      names3indices.append(m[1][0])
  for m in matches:
    if len(m[1])==2 and m[1][0] not in names3indices:
      name = str(doc[m[1][1]])+" "+str(doc[m[1][0]])
      names2.append(name.lower())
      names2indices.append(m[1][0])
  names = names2+names3#format_names(doc,matches)
  return list(set(names))
    
  
def get_entities(doc):
  entities =[]
  entity=''
  for token in doc:
    if token.ent_type_=='ORG' or token.ent_type_=='PERSON':
      if token.ent_iob_=='B':
        if entity!='':
          entities.append(entity.lower())
        entity = token.text
      elif token.ent_iob_=='I': 
        entity = entity+' '+token.text
  #print(list(set(entities)))
  return list(set(entities))
  
def get_speakers(doc,text):
  name_matcher = DependencyMatcher(nlp.vocab)
  name_matcher.add("names", [fname_lname])
  matcher = DependencyMatcher(nlp.vocab)
  matcher.add("person said", [name_said,person_of_group_said,person_verbing_group,fname_lname_said,person_appositive,person_title])
  #for text in records[:50]:
  
  
  nouns = [np.text for np in doc.noun_chunks]
  #print(nouns)
  names = format_names(doc,name_matcher(doc))
  matches = matcher(doc)
  speakers=[]
  for m in matches:
    if len(m[1])==6:
      name_identifier = str(doc[m[1][1]])+" "+str(doc[m[1][0]])
      group_identifier = str(doc[m[1][5]])+" "+str(doc[m[1][4]])
      name=name_identifier if name_identifier in text else ''
      group=group_identifier if group_identifier in text else ''
      #print(name+" "+group)
      for n in nouns:
        if name_identifier in n and len(n)>len(name):
          #print(n, doc[m[1][1]], doc[m[1][0]], '\t', m)
          name = n
        if group_identifier in n and len(n)>len(group) and not check_for_names(n,names):
          group=n
      if name!="" and group!="":
        #print(name,group)
        speakers.append(name+", "+group)
    elif len(m[1])==5:
      identifier = str(doc[m[1][1]])+" "+str(doc[m[1][0]])
      group_identifier = str(doc[m[1][4]])+" "+str(doc[m[1][3]])
      name=identifier if identifier in text else ''
      group=group_identifier if group_identifier in text else ''
      #print(name+" "+group)
      for n in nouns:
        if identifier in n and len(n)>len(name):
          #print(n, doc[m[1][1]], doc[m[1][0]], '\t', m)
          name = n
        if group_identifier in n and len(n)>len(group) and not check_for_names(n,names):
          group=n
      if name!="" and group!="":
        #print(name,group)
        speakers.append(name+", "+group)
    elif len(m[1])==3:
      identifier = str(doc[m[1][1]])+" "+str(doc[m[1][0]])
      #print(doc[m[1][1]].text+" "+doc[m[1][0]].text+" "+doc[m[1][2]].text)
      name=identifier if identifier in text else ''
      for n in nouns:
        if identifier in n and identifier+" '" not in n and len(n)>len(name):
          #print(n, doc[m[1][1]], doc[m[1][0]], '\t', m)
          name = n
      if name!='':
        speakers.append(name)
    elif len(m[1])==2:
      #print(doc[m[1][1]].text+" "+doc[m[1][0]].text)
      identifier = str(doc[m[1][0]]) 
      name=''
      for n in nouns:
        if len(n)>len(name) and identifier in n and identifier+" '"  not in n and identifier+" family" not in n and identifier+" home" not in n and identifier+" house" not in n:
            #print(n, doc[m[1][1]], doc[m[1][0]], '\t', m)
            name = n
        for n in names:
          if len(n)> len(name) and identifier in n:
            name = n
        if name!='':
          speakers.append(name)
  final_speakers=[]

  for s in speakers:
    found = False
    for comparison in speakers:
      if s in comparison and s!=comparison:
        found = True
    if not found:
      final_speakers.append(s.strip())
  return list(set(final_speakers))
  
def get_race(doc):
  matcher = DependencyMatcher(nlp.vocab)
  matcher.add("race",[racial_identification])
  #doc = nlp(lemmas)
  matches = matcher(doc)
  race=[]
  for m in matches:
    race.append(str(doc[m[1][0]])+" "+str(doc[m[1][1]]))
  return race

def get_matches_old(t):
  text = t[10:] if not IS_VIDEOS else t
  text = re.sub(r'Sgt.',r'Sgt',text)
  text = re.sub(r'Lt.',r'Lt',text)
  text = re.sub(r'<h>|<p>',r'',text)
  text = text.strip()
  doc = nlp(text)
  noun_results = {
    'speakers':list(set(get_speakers(doc,text))),
    'entities': list(set(get_entities(doc))),
    'nouns':list(set(get_nouns(doc))),
    'race':list(set(get_race(doc)))
  }
  #print(noun_results)
  return noun_results
      
  #print(list(set(final_speakers)))
  return list(set(final_speakers))

def get_matches(docs,texts):
  noun_results = {
    'speakers':[],
    'entities': [],
    'nouns':[],
    'race':[]
  }
  for i,doc in enumerate(docs):
    noun_results['speakers']+=get_speakers(doc,texts[i])
    noun_results['entities']+=get_entities(doc)
    noun_results['nouns']+=get_nouns(doc)
    noun_results['race']+=get_race(doc)
  for key in noun_results.keys():
    noun_results[key]=list(set(noun_results[key]))
  #print(noun_results)
  return noun_results


"""
FOR TESTING:
matcher = DependencyMatcher(nlp.vocab)
matcher.add("person said", [fname_lname_said])
matches = matcher(doc)
for m in matches: print(m)
"""
          
