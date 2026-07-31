import pandas as pd
import os
from config import *

def combine_formality():
  full_df=None
  started=None
  for y in range(2014,2024):
    year = str(y)
    if os.path.exists(OUTPUT_DIR+year+"_formality.csv"):
      df = pd.read_csv(OUTPUT_DIR+year+"_formality.csv")
      new_df = df[['article_id','formality']].groupby('article_id').agg('mean')
      new_df['formal_sent_count']=df.groupby('article_id').size()
      if not started:
        full_df=new_df
        started = True
      else:
        full_df=pd.concat([full_df,new_df])
  full_df.to_csv(OUTPUT_DIR+"formality_scores.csv")


#Subjectivity
subj_df = pd.read_csv(OUTPUT_DIR+"subj_scoresmasked.csv")
print("subj",subj_df.shape)

#Readability
if not os.path.isfile(OUTPUT_DIR+'readability_grouped.csv'):
  temp_df=pd.read_csv(OUTPUT_DIR+'readability_masked.csv')
  temp_df = temp_df.drop(columns=['incident'])
  temp_df = temp_df.groupby('article_id').agg('mean')
  temp_df.to_csv(OUTPUT_DIR+'readability_grouped.csv')

readability_df = pd.read_csv(OUTPUT_DIR+'readability_grouped.csv')


#Concreteness
temp_df = pd.read_csv(OUTPUT_DIR+"concreteness_scoresmasked.csv")
temp_df['conc_rating']=temp_df['rating'] 
conc_df = temp_df[['article_id','conc_rating']]

#Agency
agency_updated=pd.read_csv(OUTPUT_DIR+"agency_police.csv")
agency_allpolice=pd.read_csv(OUTPUT_DIR+"agency_police_updated.csv")
agency_allpolice=agency_allpolice[['article_id','police_agency_updated']]
agency_updated = agency_updated.rename(columns={'police_agency_updated':'policeparticipant_agency_updated'})
  
#Speakers
speaker_df = pd.read_csv(OUTPUT_DIR+"speakers_updated.csv")

#Person mentions
new_df=pd.read_csv(OUTPUT_DIR+"human.csv")

#Participant Framing
participant_df = pd.read_csv(OUTPUT_DIR+"participant_framing_new.csv")

#Formality
if not os.path.isfile(OUTPUT_DIR+"formality_scores.csv"):
  combine_formality()
formal_df = pd.read_csv(OUTPUT_DIR+"formality_scores.csv")

#Combine all features
df = subj_df
df_list = [conc_df,formal_df,readability_df,speaker_df,agency_updated,new_df,participant_df,agency_allpolice]
for d in df_list:
  print(d.shape)
  df = df.merge(d,on="article_id",how='left')
print(df.shape)
df.to_csv(JSON_DIR+"features_updated.csv")