import pandas as pd
import random
import csv
import numpy as np
from collections import defaultdict

import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
model_id="answerdotai/ModernBERT-large"
epochs=3
print("Model: ",model_id)
print("Epochs: ",epochs)

inpath="/projects/p31502/projects/gun_violence/community_justice/processed/"
outpath="/projects/p31502/projects/gun_violence/community_justice/bert/rerun/"
mask_folder="/projects/p31502/projects/gun_violence/community_justice/bert/masks/"
csv_with_race_info= "/gpfs/projects/p31502/projects/gun_violence/community_justice/analysis/regression/revisions/csvs/flipped_regression.csv"

def extract_piece(t):
  words = t.split(" ")
  start_range = max(len(words)-200,100)
  start = random.randint(0,start_range-1)
  return " ".join(words[start:start+200])

def filter_illformed(t):
  words = t.split()
  #if len(set(words[:20]))<0.6*len(words):
   # return False
  return (words[0]==words[1] and words[2]==words[3]) or (words[2]==words[1] and words[4]==words[3])

def get_filtered_matches(ids):
  characteristics=['major','low_death','year','officer','drug','gang','suicide','mass','accident','assaultweapon','domestic_violence','school']
  df = pd.read_csv(inpath+"articles_with_everything.csv")
  df=df[df['article_id'].isin(ids)]
  #df = df[(df['nonhispanicwhite']<=40) | (df['nonhispanicwhite']>=60)]
  id_name='article_id'
  #print([x for x in list(df.columns) if 'id' in x])
  print(df.shape)
  df = df[df['shortterm']>0]
  df=df[(df['nonhispanicwhite']<=40) | (df['nonhispanicwhite']>=60)]
  print(df.shape)
  df['is_poc']=df['nonhispanicwhite']<50
  
  df['major']=df['n_killed'].apply(lambda x : x>4)
  df['precovid']=df['year_incident'].apply(lambda x : x<2020)
  #df['art_count']=df['count'].apply(lambda x : 'one' if x<3 else 'some' if x<=10 else 'many')
  #print(df['year'].value_counts())
  print(df['is_poc'].value_counts())
  df['low_death']=df['n_killed'].apply(lambda x: x<2)
  df = df[['primary_incident_id','year_incident','major','low_death','precovid','is_poc','officer','drug','gang','suicide','mass','accident','assaultweapon','domestic_violence','school',id_name]]
  
  df = df.rename(columns={'article_id_x':'article_id','year_incident':'year'})
  df['vector'] = df[characteristics].apply(lambda x: str([x[a] for a in x.keys()]),axis=1)
  d = df
  df = d[['vector','is_poc','primary_incident_id','article_id']]
  df.to_csv(outpath+'article_vectors_predictions.csv')
  df = d[['vector','is_poc','article_id']]
  
  new_df = df.groupby(['vector']).count()
  
  df1=df[['vector','is_poc']][df['is_poc']==False].groupby('vector').agg('count')
  df2=df[['vector','is_poc']][df['is_poc']==True].groupby('vector').agg('count')
  #print(df1.shape,df2.shape)
  new_df = df1.merge(df2,left_index=True,right_index=True,suffixes=('_white','_poc'))
  #print(new_df.shape)
  new_df['min']=new_df[['is_poc_white','is_poc_poc']].min(axis=1)
  new_df.to_csv(outpath+'article_counts_predictions.csv')
  print(sum(new_df['min'])*2)
  counts={}
  white=defaultdict(list)
  poc=defaultdict(list)
  with open(outpath+'article_counts_predictions.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
      counts[row['vector']]=int(row['min'])
  
  #art_count={}
  missing=0
  with open(outpath+'article_vectors_predictions.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
      d = poc if row['is_poc']=='True' else white
      
      if row['article_id']=='':
        missing+=1
      else:
        d[row['vector']].append(int(float(row['article_id'])))
      #art_count[int(row['id'])]=int(row['count'])
  print(missing)
  
  selected=[]
  pair_frames=[]
  to_select=defaultdict(list)
  for i,key in enumerate(counts.keys()):
    #if counts[key]<5:
    #print(np.random.choice(white[key],counts[key],replace=False))
    selection_size=min(len(white[key]),len(poc[key]))
    if len(white[key])<counts[key]:
      print('white',counts[key],len(white[key]))
    if len(poc[key])<counts[key]:
      print('poc',counts[key],len(poc[key]))
    white_ids = np.random.choice(white[key],selection_size,replace=False).tolist()
    poc_ids =np.random.choice(poc[key],selection_size,replace=False).tolist()
    pair_frames.append(pd.DataFrame({'poc':poc_ids,'white':white_ids}))
    selected+=white_ids
    selected+=poc_ids
  return selected
    

def get_data():
  folder = mask_folder
  dfs = []
  for y in range(2014,2024):
    #if y==2022:
     # continue
    year = str(y)
    d = pd.read_csv(folder+'updated_masks_'+year+".csv")
    dfs.append(d)
  df = pd.concat(dfs)
  
  print(df.shape)
  #df = df[(df['white']<=40) | (df['white']>=60)]
  #df['race']=df['white'].apply(lambda x: 0 if x<50 else 1)
  df['full_text']=df['text'].astype(str)
  print(df['full_text'].head())
  df['sent_len']=df['full_text'].apply(lambda x: len(x.strip().split()))
  print(df['sent_len'].min(),df['sent_len'].max())
  df = df[(df['sent_len']>=200) & (df['sent_len']<2000)]
  print(df.shape)
  df['invalid']=df['full_text'].apply(lambda x: filter_illformed(x))
  df=df[df['invalid']==False]
  print(df.shape)
  print(df['full_text'].head())
  df['text']=df['full_text'].apply(lambda x: extract_piece(x))
  print(df['text'].head())
  print(df.shape)
  ddf= pd.read_csv(csv_with_race_info)
  ddf = ddf.dropna(subset=['nonhispanicwhite'])
  ids_with_data=list(ddf['article_id'])
  
  ids = list(df['article_id'])
  ids = [x for x in ids if x in ids_with_data]
  
  matched_ids=get_filtered_matches(ids)
  df1 = pd.read_csv(inpath+"articles_with_everything.csv")
  df1 = df1[df1['article_id'].isin(matched_ids)]
  df1 = df1[['article_id','source_scope']]
  print(df1.shape)
  df1['scope'] = df1['source_scope'].apply(lambda x: 1 if x=='National' else 0)
  #print(df1.shape)
  df = df.merge(df1,on='article_id')
  print(df.shape)
  print(df['race'].value_counts())
  df.to_csv(mask_folder+"prepared.csv",index=False)

def predict(sents=False):
  
  df = pd.read_csv(mask_folder+"prepared.csv")
  print(df.shape)
  
  print(df['race'].value_counts())
 
  X = list(df['full_text'])
  print("Using full text")  
  y = list(df['race']) 
  svm_crossval(X,y)
  deberta(X,y)
  modernbert(X,y)
  #svm_features(X,y)
  
def svm_crossval(X,y):
  from sklearn.model_selection import train_test_split,cross_val_score
  from sklearn.svm import SVC,LinearSVC
  from sklearn.feature_extraction.text import TfidfTransformer
  from sklearn.feature_extraction.text import CountVectorizer
  
  count_vect = CountVectorizer(ngram_range=(1,2))
  X_counts = count_vect.fit_transform(X)
  tf_transformer = TfidfTransformer().fit(X_counts)
  X_transformed = tf_transformer.transform(X_counts)
  print("ready to start")
  #clf = SVC()#random_state=0,kernel='linear', C=1)
  clf= LinearSVC(random_state=0) 
  scores = cross_val_score(clf, X_transformed, y, cv=5)
  print(scores.mean())
  
def svm_features(X,y):
  from sklearn.model_selection import train_test_split,cross_val_score
  from sklearn.svm import SVC,LinearSVC
  from sklearn.feature_extraction.text import TfidfTransformer
  from sklearn.feature_extraction.text import CountVectorizer
  from sklearn.metrics import accuracy_score
  
  
  X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=0, test_size=0.3)
  
  count_vect = CountVectorizer(ngram_range=(1,2))
  X_train_counts = count_vect.fit_transform(X_train)
  tf_transformer = TfidfTransformer().fit(X_train_counts)
  X_train_transformed = tf_transformer.transform(X_train_counts)
  
  X_test_counts = count_vect.transform(X_test)
  X_test_transformed = tf_transformer.transform(X_test_counts)
  
  print("data prepared")
  
  linear_svc = LinearSVC(random_state=0)
  clf = linear_svc.fit(X_train_transformed,y_train)
  
  # Predict the labels of the testing data
  y_pred = clf.predict(X_test_transformed)
  
  # Calculate the accuracy of the classifier
  acc = accuracy_score(y_test, y_pred)
  print("Accuracy:", acc)
  print_top10(count_vect,clf,clf.classes_)

  
  
def print_top10(vectorizer, clf, class_labels):
  import numpy as np
  """Prints features with the highest coefficient values, per class"""
  feature_names = vectorizer.get_feature_names_out()
  for i, class_label in enumerate(class_labels):
    if i==0:
      top10 = np.argsort(clf.coef_[i])[-10:]
      print("White %s: %s" % (class_label,
            ", ".join(feature_names[j] for j in top10)))
      top10 = np.argsort(clf.coef_[i])[:10]
      print("POC %s: %s" % (class_label,
            ", ".join(feature_names[j] for j in top10)))
  

def deberta(X,y):
  from sklearn.model_selection import StratifiedKFold
  from sklearn.metrics import accuracy_score
  from transformers import AutoTokenizer, DebertaForSequenceClassification
  import re
  from torch.utils.data import DataLoader, Dataset
  import torch
  print('cuda' if torch.cuda.is_available() else 'cpu')
  tokenizer = AutoTokenizer.from_pretrained("microsoft/deberta-base")
  
  #X= [re.sub('<MASK>','[MASK]',text) for text in X]
  X= [re.sub('[A-Za-z]+_mask','[MASK]',text) for text in X]
  
  class TextDataset(Dataset):
    def __init__(self, texts, labels):
        self.texts = texts
        self.labels = labels
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = self.texts[idx]
        label = self.labels[idx]
        encoding = tokenizer(text, padding='max_length', truncation=True, max_length=510, return_tensors='pt')
        input_ids = encoding['input_ids'].squeeze()
        attention_mask = encoding['attention_mask'].squeeze()
        return {'input_ids': input_ids, 'attention_mask': attention_mask, 'labels': torch.tensor(label)}

  
  dataset = TextDataset(X,y)
  # Define k-fold cross-validation
  k_folds = 5
  skf = StratifiedKFold(n_splits=k_folds, shuffle=True, random_state=42)
  
  # Initialize lists to store accuracies for each fold
  fold_accuracies = []
  
  # Perform k-fold cross-validation
  for fold, (train_indices, val_indices) in enumerate(skf.split(X,y)):
      #print(k_folds)
      print(f"Training Fold {fold+1}/{k_folds}")
      
      # Split dataset into train and validation sets for the current fold
      train_dataset = torch.utils.data.Subset(dataset, train_indices)
      val_dataset = torch.utils.data.Subset(dataset, val_indices)
      
      # Create data loaders
      train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
      val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)
      
      # Training loop
      model = DebertaForSequenceClassification.from_pretrained("microsoft/deberta-base")
      optimizer = torch.optim.AdamW(model.parameters(), lr=2e-5)
      criterion = torch.nn.CrossEntropyLoss()
      device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
      
      model.to(device)
      model.train()
      for epoch in range(3):  # Adjust the number of epochs as needed
          for batch in train_loader:
              optimizer.zero_grad()
              input_ids = batch['input_ids'].to(device)
              attention_mask = batch['attention_mask'].to(device)
              labels = batch['labels'].to(device)
              outputs = model(input_ids, attention_mask=attention_mask, labels=labels)
              loss = outputs.loss
              loss.backward()
              optimizer.step()
  
      # Evaluation loop
      model.eval()
      val_predictions = []
      val_labels = []
      with torch.no_grad():
          for batch in val_loader:
              input_ids = batch['input_ids'].to(device)
              attention_mask = batch['attention_mask'].to(device)
              labels = batch['labels'].to(device)
              outputs = model(input_ids, attention_mask=attention_mask)
              _, predicted_labels = torch.max(outputs.logits, dim=1)
              val_predictions.extend(predicted_labels.tolist())
              val_labels.extend(labels.tolist())
  
      fold_accuracy = accuracy_score(val_labels, val_predictions)
      fold_accuracies.append(fold_accuracy)
      print(f"Accuracy for Fold {fold+1}: {fold_accuracy}")
  
  # Calculate average accuracy across all folds
  average_accuracy = sum(fold_accuracies) / len(fold_accuracies)
  print(f"Average Accuracy: {average_accuracy}")

def modernbert(X,y):
  from sklearn.model_selection import StratifiedKFold
  from sklearn.metrics import accuracy_score
  from transformers import AutoTokenizer, ModernBertForSequenceClassification
  import re
  from torch.utils.data import DataLoader, Dataset
  import torch
  print('cuda' if torch.cuda.is_available() else 'cpu')
  tokenizer = AutoTokenizer.from_pretrained(model_id)
  
  #X= [re.sub('<MASK>','[MASK]',text) for text in X]
  X= [re.sub('[A-Za-z]+_mask','[MASK]',text) for text in X]
  
  class TextDataset(Dataset):
    def __init__(self, texts, labels):
        self.texts = texts
        self.labels = labels
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = self.texts[idx]
        label = self.labels[idx]
        encoding = tokenizer(text, padding='max_length', truncation=True, max_length=1000, return_tensors='pt')
        input_ids = encoding['input_ids'].squeeze()
        attention_mask = encoding['attention_mask'].squeeze()
        return {'input_ids': input_ids, 'attention_mask': attention_mask, 'labels': torch.tensor(label)}

  
  dataset = TextDataset(X,y)
  # Define k-fold cross-validation
  k_folds = 5
  skf = StratifiedKFold(n_splits=k_folds, shuffle=True, random_state=42)
  
  # Initialize lists to store accuracies for each fold
  fold_accuracies = []
  
  # Perform k-fold cross-validation
  for fold, (train_indices, val_indices) in enumerate(skf.split(X,y)):
      #print(k_folds)
      print(f"Training Fold {fold+1}/{k_folds}")
      
      # Split dataset into train and validation sets for the current fold
      train_dataset = torch.utils.data.Subset(dataset, train_indices)
      val_dataset = torch.utils.data.Subset(dataset, val_indices)
      
      # Create data loaders
      train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
      val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)
      
      # Training loop
      model = ModernBertForSequenceClassification.from_pretrained(model_id)
      optimizer = torch.optim.AdamW(model.parameters(), lr=2e-5)
      criterion = torch.nn.CrossEntropyLoss()
      device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
      
      model.to(device)
      model.train()
      for epoch in range(epochs):  # Adjust the number of epochs as needed
          for batch in train_loader:
              optimizer.zero_grad()
              input_ids = batch['input_ids'].to(device)
              attention_mask = batch['attention_mask'].to(device)
              labels = batch['labels'].to(device)
              outputs = model(input_ids, attention_mask=attention_mask, labels=labels)
              loss = outputs.loss
              loss.backward()
              optimizer.step()
  
      # Evaluation loop
      model.eval()
      val_predictions = []
      val_labels = []
      with torch.no_grad():
          for batch in val_loader:
              input_ids = batch['input_ids'].to(device)
              attention_mask = batch['attention_mask'].to(device)
              labels = batch['labels'].to(device)
              outputs = model(input_ids, attention_mask=attention_mask)
              _, predicted_labels = torch.max(outputs.logits, dim=1)
              val_predictions.extend(predicted_labels.tolist())
              val_labels.extend(labels.tolist())
  
      fold_accuracy = accuracy_score(val_labels, val_predictions)
      fold_accuracies.append(fold_accuracy)
      print(f"Accuracy for Fold {fold+1}: {fold_accuracy}")
  
  # Calculate average accuracy across all folds
  average_accuracy = sum(fold_accuracies) / len(fold_accuracies)
  print(f"Average Accuracy: {average_accuracy}")


#prep_data()
get_data()
predict()
#predict(split_scope=True,national=False)
#predict(split_scope=True,national=True)