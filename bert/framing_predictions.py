import csv,re,os
import pandas as pd
print("A")
import argparse
from collections import defaultdict
import numpy as np
#import spacy
#nlp = spacy.load('en_core_web_lg')
print("B")
IS_VIDEOS=False

if IS_VIDEOS:
  folder = "/projects/p31502/projects/gun_violence/community_justice/processed_videos/"
  OUTPUT_DIR = "/projects/p31502/projects/gun_violence/community_justice/processed_videos/csvs/ling_features/"
  masking_dir = "/projects/p31502/projects/gun_violence/community_justice/processed_videos/csvs/masking/"
  path="/projects/p31502/projects/gun_violence/community_justice/bert/video_csvs/"
else:
  folder = "/projects/p31502/projects/gun_violence/community_justice/processed/"
  OUTPUT_DIR = '/projects/p31502/projects/gun_violence/community_justice/analysis/ling_features/csvs/'
  masking_dir = "/projects/p31502/projects/gun_violence/community_justice/processed/csvs/masking/"
  path="/projects/p31502/projects/gun_violence/community_justice/bert/csvs/"

police_words=['hero','savior','protector','superhero']  #,'guardian'

shooter_words=['criminal','felon','fugitive','convict','thug','gangster','terrorist']

victim_words=['cousin','aunt','uncle','mother','father','mom','dad','stepmom','stepdad','stepmother','stepfather','sister','stepsister','brother','stepbrother','son','stepson','daughter','stepdaughter','grandmother','grandfather','grandma','grandpa','niece','nephew','sibling','parent','grandparent','family','wife','husband','boyfriend','girlfriend','fiancee','fiance','friend','neighbor','student','teacher','resident','member','coach','teammate','team','mentor','leader','volunteer','victim']
complex_person_words=['cousin','aunt','uncle','mother','father','mom','dad','stepmom','stepdad','stepmother','stepfather','sister','stepsister','brother','stepbrother','son','stepson','daughter','stepdaughter','grandmother','grandfather','grandma','grandpa','niece','nephew','sibling','parent','grandparent','wife','husband','boyfriend','girlfriend','fiancee','fiance','friend','student','teacher','coach','teammate','mentor','leader','volunteer'] #'member',resident,'team','neighbor'
family_words=['cousin','aunt','uncle','mother','father','mom','dad','stepmom','stepdad','stepmother','stepfather','sister','stepsister','brother','stepbrother','son','stepson','daughter','stepdaughter','grandmother','grandfather','grandma','grandpa','niece','nephew','sibling','parent','grandparent','wife','husband','fiancee','fiance','friend','boyfriend','girlfriend']
social_role_words=['neighbor','student','teacher','resident','member','coach','teammate','team','mentor','leader','volunteer','boyfriend','girlfriend','friend']

#victim_words=['aunt','uncle','mother','father','mom','dad','brother','son','daughter','parent','wife','husband','girlfriend','student','member','leader']
#shooter_words=['criminal','terrorist']
#police_words=['hero']

def prep_data():
  lists={
    'police':[]#,
  #  'victim':[],
   # 'shooter':[]
  }
  count=0
  multimask=0
  unimask=0
  for y in range(2014,2024):
    year = str(y)
    if not os.path.exists(masking_dir+"masked_sentences_"+year+".csv"):
      continue
    print("YEAR: ",year)
    with open(masking_dir+"masked_sentences_"+year+".csv",'r') as csvfile:
      reader = csv.DictReader(csvfile)
      for row in reader:
        for role in lists.keys():
          #result = mask(row,role)
          if role=='police' and 'police_name' in row['text']:
            t=re.sub("police police_name","police_name",row['text'],flags=re.IGNORECASE)
            t=re.sub("police_name officer","police_name",t,flags=re.IGNORECASE)
            t=re.sub("police_name officer","police_name",t,flags=re.IGNORECASE)
          else:
            t=row['text']
          t = re.sub(role+'_name','<mask>',t)
          t=re.sub('(<mask> )+','<mask> ',t)
          s=t.split()
          if '<mask>' not in t or len(s)<6 or ((s[0]==s[1] and s[2]==s[3]) or (s[2]==s[1] and s[4]==s[3]) or (s[2]==s[3] and s[4]==s[5])):
            continue
          
          if len(s)>200:
            count+=1
          if len([x for x in s if x=='<mask>'])>1:
            multimask+=1
          else:
            unimask+=1
          lists[role].append({
            'article_id':row['article_id'],
            'text':t
          })
    print(count)
    print(multimask,unimask)
  for role,data in lists.items():
    print(role,len(data))
    df = pd.DataFrame(data)
    df.to_csv(path+"3groups_sentences_"+role+"_updated.csv",index=False)

def inference(model_name,with_the=False,group="police"):
  
  import torch
  import logging
  logging.basicConfig(level=logging.INFO)# OPTIONAL
  if model_name=='deberta':
    from transformers import AutoTokenizer,DebertaV2ForMaskedLM#DebertaV2TokenizerFast, DebertaForMaskedLM#AutoModel#AutoTokenizer,DebertaForMaskedLM #
    
    #model=AutoModel.from_pretrained("microsoft/deberta-v3-large")
    #config = AutoConfig.from_pretrained("microsoft/deberta-v3-large")
    #tokenizer = AutoTokenizer.from_pretrained("microsoft/deberta-v3-large")
    tokenizer = AutoTokenizer.from_pretrained("microsoft/deberta-v2-xlarge")
    model = DebertaV2ForMaskedLM.from_pretrained("microsoft/deberta-v2-xlarge")
    #tokenizer = AutoTokenizer.from_pretrained("lsanochkin/deberta-large-feedback")
    #model = DebertaForMaskedLM.from_pretrained("lsanochkin/deberta-large-feedback")
    unk='[UNK]'
    mask_token='[MASK]'
  elif model_name=='modernbert':
    from transformers import AutoTokenizer,AutoModelForMaskedLM
    model_id = "answerdotai/ModernBERT-base"
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForMaskedLM.from_pretrained(model_id)
    unk='[UNK]'
    mask_token='[MASK]'
  elif model_name=='bert':
    from transformers import AutoTokenizer, BertForMaskedLM
    tokenizer = AutoTokenizer.from_pretrained("google-bert/bert-base-uncased")
    model = BertForMaskedLM.from_pretrained("google-bert/bert-base-uncased")
    unk='[UNK]'
    mask_token='[MASK]'
  else:
    from transformers import AutoTokenizer, RobertaForMaskedLM #DebertaForMaskedLM #
    tokenizer = AutoTokenizer.from_pretrained("FacebookAI/roberta-base")
    model = RobertaForMaskedLM.from_pretrained("FacebookAI/roberta-base") 
    unk='<unk>'
    mask_token='<mask>'
  #text = "When I grow up, I want to be a "+mask_token+"."
  #tokenized_text = tokenizer(text, return_tensors="pt")
  use_cuda = torch.cuda.is_available()
   
  related_words=victim_words+shooter_words+police_words
  word_ids = tokenizer.convert_tokens_to_ids(related_words) 
  word_ids=[x for x in word_ids if tokenizer.convert_ids_to_tokens(x)!=unk]
  mask_id=tokenizer.convert_tokens_to_ids(mask_token)
  print(mask_id)
  #for i,x in enumerate(word_ids):
   # print(tokenizer.convert_ids_to_tokens(x))
  #print(tokenizer.convert_ids_to_tokens(word_ids))
  
  model.eval()
  if use_cuda:
    model.to('cuda')  # if you have gpu
  for role in ['victim','shooter','police']: # #[group]:#'victim','shooter',
    role_name= 'police_updated' if role=='police' else role
    torch.cuda.empty_cache()
    print(role)
    data=[]
    many_masks=0
    missing=0
    with open(path+"3groups_sentences_"+role+".csv",'r') as csvfile:
    #with open(path+"sentences_3groups_"+role+".csv",'r') as csvfile:
      reader = csv.DictReader(csvfile)
      for row in reader:
        if len([x for x in row['text'].split() if x=='<mask>'])>1:
          continue
        #print('row')
        text = re.sub("<mask>","masked_name",row['text'])
        text = re.sub("masked_name family","masked_name 's family",text)
        text = re.sub("[Oo]fficer masked_name","masked_name",text)
        text = re.sub("[Pp]olice masked_name","masked_name",text)
        #t = text.split("@ @ @ @ @ @ @ @ @ @")
        #text = [x for x in t if 'masked_name' in x][0]
        if with_the:
          #text = re.sub("(<mask> )+","<mask> ",row['text'])
          doc = nlp(text)
          for i,t in enumerate(doc):
            if t.text=="masked_name":
              add_the= i==0 or (doc[i-1].pos_ not in ['ADJ','DET','PROPN','NUM'] and doc[i-1].lower_ not in ['veteran','rookie'])#i==0 or doc[i-1].pos_ not in ['ADJ','DET','PROPN','NUM'] or doc[i-1].lower_ not in ['veteran','rookie']
              continue
          if add_the:
            text = re.sub("masked_name","the "+mask_token,text)
          else:
            text = re.sub("masked_name",mask_token,text)
        else:
        #  text = re.sub("<mask>","[MASK]",row['text'])
        #  text = re.sub("\[MASK\] family","[MASK] 's family",text)
        #  text = re.sub("[Oo]fficer \[MASK\]","[MASK]",text)
          text = re.sub("masked_name",mask_token,text)
        if use_cuda:
          tokenized_text = tokenizer(text, return_tensors="pt").to('cuda')
        else:
          tokenized_text = tokenizer(text, return_tensors="pt")
        masked_index = [i for i,x in enumerate(tokenized_text['input_ids'][0]) if x==mask_id]
        if len(masked_index)==0:
          missing+=1
        if len(masked_index)>1:
          many_masks+=1

        # Predict all tokens
        with torch.no_grad():
            outputs = model(**tokenized_text)
            predictions = outputs.logits
        #print(len(predictions))
        for masked_idx in masked_index:
          obj={'article_id':row['article_id'],'text':text}
          probs = torch.nn.functional.softmax(predictions[0, masked_idx], dim=-1)
          #top_k_weights, top_k_indices = torch.topk(probs, top_k, sorted=True)
          for i, pred_idx in enumerate(word_ids):
            
              predicted_token = tokenizer.convert_ids_to_tokens([pred_idx])[0]
              prob=probs[pred_idx]
              obj[predicted_token]=prob
              #print("[MASK]: '%s'"%predicted_token, " | weights:", float(prob))
          data.append(obj)
        torch.cuda.empty_cache()
    print("missing",missing)
    print("multiple masks",many_masks)  
    df = pd.DataFrame(data)
    extra = "_"+model_name if model_name else ''
    if not with_the:
      extra+='_no_the'
    df.to_csv(path+role+"_predictions"+extra+".csv",index=False)
    #df.to_csv(path+role+"_predictions"+extra+"_named.csv",index=False)

  
def trim_tensors(t):
  text=re.sub("^tensor\(","",t)
  t = text.split(",")
  text=t[0]
  return float(text)

def combine(model):
  sent_counts=defaultdict(int)
  for y in range(2014,2024):
    year =str(y)
    if not os.path.exists(masking_dir+"/masked_sentences_"+year+".csv"):
      continue
    with open(masking_dir+"/masked_sentences_"+year+".csv",'r') as csvfile:
      reader=csv.DictReader(csvfile)
      for row in reader:
        if IS_VIDEOS:
          sent_counts[row['article_id']]+=1
        else:
          sent_counts[int(row['article_id'])]+=1
  totals=[]
  for key in sent_counts.keys():
    totals.append({'article_id':key,'total_participant_sents':sent_counts[key]})
  total_df = pd.DataFrame(totals)
  role_features={
    #'complex_person':victim_words,
    'criminal':shooter_words,
    'hero':police_words,
    'complex_person':complex_person_words,
    'family_member':family_words
  }
  for role in ['police','shooter','victim']:
    if role =='police':
      df = pd.read_csv(path+role+"_predictions"+model+"_updated.csv")
    else:
      df = pd.read_csv(path+role+"_predictions"+model+".csv")
    print(df.shape)
    print(df['article_id'].nunique())
    for f in list(df.columns):
      if f not in ['article_id','text']:
        df[f]=df[f].apply(lambda x: trim_tensors(x))
    df['text']=df['text'].astype(str)
    df = df.drop_duplicates(subset=['text'])
    for key in role_features.keys():
      role_features[key]=[x for x in role_features[key] if x in list(df.columns)]
      df[key]=df[role_features[key]].sum(axis=1)
    df = df[['article_id','criminal','hero','complex_person','family_member']]
    #df = df.rename(columns={'criminal':'criminal_max','hero':'hero_max','complex_person':'complex_person_max'})
    df = df.groupby('article_id').agg('mean')
    rename={}
    for key in list(df.columns):
      if key!='article_id':
        rename[key]=role+"_"+key
    df = df.rename(columns=rename)
    print(role,df.shape)
    total_df = total_df.merge(df,on='article_id',how = 'left')
  #total_df=total_df.rename({'criminal':"police_criminal",'hero':'police_hero','complex_person':'police_complex_person'})
  total_df.to_csv(OUTPUT_DIR+"participant_framing_new.csv")
    

def add_metadata(model='deberta'):
  if model!='':
    model="_"+model
  for role in ['police','shooter','victim']:
    df = pd.read_csv(path+role+"_predictions"+model+".csv")
    for f in list(df.columns):
      if f not in ['article_id','text']:
        df[f]=df[f].apply(lambda x: trim_tensors(x))
    df['text']=df['text'].astype(str)
    df = df.drop_duplicates(subset=['text'])
    df1 = pd.read_csv(folder+"articles_with_everything.csv")
    #df1['racial_categories']=df1.apply(lambda x:categorize(x),axis=1)
    #print(df1['racial_categories'].value_counts())
    #df1=pd.read_csv("/projects/p31502/projects/gun_violence/community_justice/subset_curation/articles_paired_nonhispanicwhitelooser.csv")  
    #df1['white_binary']=(df1['ice']>0).astype(int)
    df1['n_casualties']=df1['n_killed']+df1['n_injured']
    df1['white_binary']=(df1['nonhispanicwhite']>50).astype(int)
    df1['national']=(df1['source_scope']=='National').astype(int)
    df1['republican']=(df1['partisan_score']>0).astype(int)
    df1 = df1[['article_id','year','white_binary','republican','national','length','mass', 'hate_crime', 'child', 'school', 'gang', 'drug', 'officer', 'suicide', 'domestic_violence', 'home_invasion', 'accident', 'assaultweapon','n_killed','nonhispanicwhite','n_casualties','ice','num_victims']]
    df = df.merge(df1,on='article_id',how='left')
    df = df.dropna(subset='white_binary')
    #print(df['white_binary'].value_counts())
    #df=df.groupby('white_binary').sample(n= min(list(df['white_binary'].value_counts())),random_state=0)
    #df= pd.concat(dfs,axis=1)
    # = df.merge(df1,left_on='article_id',right_on='article_id_x',how='left')
    print(role,df.shape)
    df.to_csv(path+"predictions_with_metadata_"+role+model+".csv",index=False)
    #print(list(df.columns),df.shape)

def get_stars(pval_adj):
  stars = ''
  if pval_adj < 0.001:
      stars = '***'
  elif pval_adj < 0.01:
      stars = '**'
  elif pval_adj < 0.05:
      stars = '*'
  return stars
  
def log_odds(model='deberta'):
  if model !='':
    model='_'+model
  print(model)
  import numpy as np
  import statsmodels.formula.api as smf

  from sklearn.preprocessing import StandardScaler
  
  std_scaler = StandardScaler()
  
  inpath = "/projects/p31502/projects/gun_violence/community_justice/bert/csvs/"
  outpath = "/projects/p31502/projects/gun_violence/community_justice/bert/regression/"
  
  role_features = {
    'family':['cousin','aunt', 'uncle', 'mother', 'father', 'mom', 'dad', 'sister','brother', 'son', 'daughter', 'grandmother','grandfather','niece','nephew','parent', 'wife', 'husband', 'boyfriend', 'girlfriend','fiance'],
    'social':['friend','neighbor','coach','mentor','volunteer', 'student', 'resident', 'member', 'team', 'leader'],
    'shooter': ['criminal','convict','terrorist'],
    'police': ['hero','guardian']
  }
  role_features={
    #'complex_person':victim_words,
    'criminal':shooter_words,
    'hero':police_words,
    'complex_person':family_words #complex_person_words
  }
  """
  role_features = {
    'family':['aunt', 'uncle', 'mother', 'father', 'mom', 'dad','brother', 'son', 'daughter', 'parent', 'family', 'wife', 'husband', 'girlfriend','friend','student', 'resident', 'member', 'team', 'leader'],
    'shooter': ['criminal'],
    'police': ['hero']
  }
  """
  features = ['criminal','hero','complex_person'] #,'social','family'
  #features = ['hero','criminal']
  #features = ['aunt', 'uncle', 'mother', 'father', 'mom', 'dad', 'brother', 'son', 'daughter', 'parent', 'family', 'wife', 'husband', 'girlfriend', 'friend', 'student', 'resident', 'member', 'team', 'leader','criminal','terrorist','hero']
  lr_outputs = {}
  lo_outputs = {}
  
  for role in ['police','shooter','victim']:
    print(role.upper())
    infile = inpath+"predictions_with_metadata_"+role+model+".csv"
    #print(infile)
  
    df = pd.read_csv(infile)
    df['white_binary']=(df['nonhispanicwhite']>60).astype(int)
    df['race_cat_aligns']= df.apply(lambda x: binary_category(x),axis=1)
    print(df.shape)
    #df=df[df['race_cat_aligns']==True]
    df=df[df['num_victims']>0]
    print(df.shape)
    #df['any_vics']=(df['num_victims']>0).astype(int)
    #df['national']=(df['source_scope']=='National').astype(int)
    basic_ivars = ['white_binary','national']
    #ivars = ['white_binary', 'length', 'mass', 'officer', 'school', 'gang', 'child']
    ivars = ['white_binary', 'national','mass', 'hate_crime', 'child', 'school', 'gang', 'drug', 'officer', 'suicide', 'domestic_violence', 'home_invasion', 'accident', 'assaultweapon']#,'any_vics']#,'n_killed'] #'national',
    #df[variable]=(df[variable]
    #df=df.groupby('white_binary').sample(n= min(list(df['white_binary'].value_counts())))
    df['length'] = df['length'].apply(np.log1p)
    #df['named_shooters']=(df['named_shooters']>0).astype(int)
    #df['named_victims']=(df['named_victims']>0).astype(int)
    for key in role_features.keys():
      role_features[key]=[x for x in role_features[key] if x in list(df.columns)]
      df[key]=df[role_features[key]].sum(axis=1)
    #df['family']=df[role_features['family']].sum(axis=1)
    #df['social']=df[role_features['social']].sum(axis=1)
    #df['complex_person']=df['family']+df['social']
    
    #df['criminal']=df[role_features['shooter']].sum(axis=1)
    #df['hero']=df[role_features['police']].sum(axis=1)
    
    #df['complex_person']=df[role_features['complex_person']].sum(axis=1)
    #print(df['hero'].mean(),df['police_assn'].mean())
    #print(df['hero'].isna().sum(),df[['hero']].sum(axis=1).isna().sum())
    #print((df['hero']==df['police_assn']).value_counts())
    #print(df['hero'].mean())
    Xtrain = df[ivars]
    
    
    for feature in role_features.keys(): #
      #print(df['police_assn']==df['hero'])
      print(feature.upper())
      f=role+"_"+feature
      #print(df[feature].value_counts())
      
      
      df[[feature]] = std_scaler.fit_transform(df[[feature]])
      logreg = smf.ols(feature + ' ~ ' + ' + '.join(ivars), df).fit()
      
      print(feature, logreg.params['white_binary'], logreg.pvalues['white_binary'])
      pval_adj = logreg.pvalues['white_binary'] * len(features)
      stars = get_stars(pval_adj)
      lr_outputs[f] = {'coef': logreg.params['white_binary'], 'lr_pval': logreg.pvalues['white_binary'], 'lr_pval_adj': pval_adj, 'stars': stars,'role':role.capitalize(),'name': role.capitalize()+" as a "+re.sub("_"," ",feature)}
      #print(logreg.summary())
  
  
      #logreg = smf.ols(feature + ' ~ ' + ' + '.join(basic_ivars), df).fit()
      
      logreg = smf.ols(feature + ' ~ ' + ' + '.join(basic_ivars), df).fit()
      
      print(feature, logreg.params['white_binary'], logreg.pvalues['white_binary'])
      pval_adj = logreg.pvalues['white_binary'] *  len(features)
      stars = get_stars(pval_adj)
      lo_outputs[f] = {'coef': logreg.params['white_binary'], 'lr_pval': logreg.pvalues['white_binary'], 'lr_pval_adj': pval_adj, 'stars': stars}
      #print(logreg.summary())
      
    
      
  writer = csv.DictWriter(open(outpath + 'log_odds'+model+'.csv','w'), fieldnames = ['feature', 'lr_coef', 'lr_pval', 'lr_pval_adj', 'lr_stars', 'log_odds', 'lo_stars', 'p','role'])     
 
  writer.writeheader()
  for feature in lr_outputs.keys(): #
    if feature in ['police_hero','victim_criminal','shooter_criminal','victim_complex_person','shooter_complex_person']:
      row = {'feature': lr_outputs[feature]['name']} #feature.capitalize()}#renamed[feature]}
      row['lr_coef'] = lr_outputs[feature]['coef']
      row['lr_pval'] = lr_outputs[feature]['lr_pval']
      row['lr_pval_adj'] = lr_outputs[feature]['lr_pval_adj']
      row['role']=lr_outputs[feature]['role']
      #row['name']=lr_outputs[feature]['name']
      row['lr_stars'] = lr_outputs[feature]['stars']
      row['log_odds'] = lo_outputs[feature]['coef']
      row['lo_stars'] = lo_outputs[feature]['stars']
      row['p'] = lo_outputs[feature]['lr_pval']
      writer.writerow(row)
      #print(feature)
  
def get_examples(model=''):
  role_features = {
    #'family':['cousin','aunt', 'uncle', 'mother', 'father', 'mom', 'dad', 'sister','brother', 'son', 'daughter', 'grandmother','grandfather','niece','nephew','parent', 'wife', 'husband', 'boyfriend', 'girlfriend','fiance'],
   # 'social':['friend','neighbor','coach','mentor','volunteer', 'student', 'resident', 'member', 'team', 'leader'],
    'complex_person':['cousin','aunt', 'uncle', 'mother', 'father', 'mom', 'dad', 'sister','brother', 'son', 'daughter', 'grandmother','grandfather','niece','nephew','parent', 'wife', 'husband', 'boyfriend', 'girlfriend','fiance','friend','neighbor','coach','mentor','volunteer', 'student',  'member', 'teammate', 'leader'],
    'shooter': ['criminal','convict','terrorist'], 
    'police': ['hero']
  }
  
  role_features={
    'complex_person':victim_words,
    'criminal':shooter_words,
    'hero':police_words
  }
  role_features={
    #'complex_person':victim_words,
    'criminal':shooter_words,
    'hero':police_words,
    'complex_person':family_words #complex_person_words
  }
  inpath = "/projects/p31502/projects/gun_violence/community_justice/bert/csvs/"
  obj={} 
  for role in ['victim','police','shooter']: #'police',
    infile = inpath+"predictions_with_metadata_"+role+model+".csv"
    #print(infile)
  
    df = pd.read_csv(infile)
    print(df.shape)
    for f in ['criminal','hero','complex_person']:
      if f!='hero' and role=='police':
        continue
      if role!='police' and f=='hero':
        continue
      if role =='police':
        df=df[df['officer']==1]
      role_features[f]=[x for x in role_features[f] if x in list(df.columns)]
      df[f]=df[role_features[f]].sum(axis=1)
      #print(df.shape,int(0.2*df.shape[0]))
      obj[role+"_"+f+"_top"]=list(df.sort_values(f,ascending=False)[:int(0.2*df.shape[0])].sample(n=25)['text'])
      obj[role+"_"+f+"_bottom"]=list(df.sort_values(f,ascending=True)[:int(0.2*df.shape[0])].sample(n=25)['text'])
      obj[role+"_"+f+"_random"]=np.random.choice([0, 1], size=25)
      print(f,list(df.sort_values(f,ascending=False)[f])[int(0.2*df.shape[0])],list(df.sort_values(f,ascending=True)[f])[int(0.2*df.shape[0])])
      first=[]
      second=[]
      for i,c in enumerate(obj[role+"_"+f+"_random"]):
        top = re.sub('(victim_name )+','victim_name ',obj[role+"_"+f+"_top"][i])
        top = re.sub('(shooter_name )+','shooter_name ',top)
        top = re.sub('(police_name )+','police_name ',top)
        bottom = re.sub('(victim_name )+','victim_name ',obj[role+"_"+f+"_bottom"][i])
        bottom = re.sub('(shooter_name )+','shooter_name ',bottom)
        bottom = re.sub('(police_name )+','police_name ',bottom)
        if c==0:
          first.append(top)
          second.append(bottom)
        else:
          second.append(top)
          first.append(bottom)
      obj[role+"_"+f+"_first"]=first
      obj[role+"_"+f+"_second"]=second
  examples=pd.DataFrame.from_dict(obj,orient='columns')
  print(examples.shape)
  #examples.to_csv("/gpfs/projects/p31502/projects/gun_violence/community_justice/bert/csvs/"+model+"_examples.csv",index=False)
    #print(f)
    #print("TOP")
    #print("\n".join(list(top)))
    #print("BOTTOM")
    #print("\n".join(list(bottom)))
#prep_data()
#pipeline_inference()
#inference(True,with_the=True)
#add_metadata('deberta_special')
#add_metadata("")
#add_metadata("deberta_special_added_the")
#log_odds("deberta_special_added_the")
#get_examples("_deberta_special_added_the")
#log_odds('deberta_special')
#log_odds('')

    

def categorize(row):
  if row['race_ice']>0:
    if row['ice']>0:
      return 'white_white'
    else:
      return 'white_poc'
  else:
    if row['ice']>0:
      return 'poc_white'
    else:
      return 'poc_poc'
      
def binary_category(row):
  return (row['nonhispanicwhite']>50 and row['ice']>0) or (row['nonhispanicwhite']<=50 and row['ice']<=0)

def parse_commandline():
    """Parse the arguments given on the command-line.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--role",
                       help="police/shooter/victim",
                       default=None)


    args = parser.parse_args()
    roles=['police','victim','shooter']
    return roles[int(args.role)]

if __name__ == '__main__':
  #prep_data()
  #role=parse_commandline()
  #inference('modernbert',True)
  #inference('bert',True)
  #add_metadata("modernbert")
  #add_metadata("bert")
  #combine('_bert')
#don't need below
  #add_metadata("deberta_special_added_the_only")
  #combine('_bert')
  #inference('bert',False,group)
  #add_metadata("bert")
  #log_odds("bert")
  #log_odds("deberta_special")
  get_examples("_modernbert")
  
  '''
  group = parse_commandline() 
  if group=='None':
    log_odds("bert")
  else:   
    inference('bert',False,group)
  '''
  #log_odds("deberta_special_added_the_only")