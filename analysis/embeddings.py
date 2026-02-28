import os
import json
import re
import csv
import numpy as np

#import spacy
#nlp = spacy.load('en_core_web_lg')
titles=['Dr.','Mr.','Mrs.','Ms.']

resub_title_list=r'Deputy|Officer|Lt|Lt.|Dr|Dr.|Detective|Police Chief|Sgt|Sgt.|Sergeant|Lieutenant|1st Class|2nd Class|First Class|Second Class'

def get_name_variants(name,gender=None):
  names = [name]
  titled_names=[]
  titleless_name=name
  personal_titles=[]
  name = re.sub(r'photo by [A-Z][a-z]+ [A-Z][a-z]+',r'',name,re.IGNORECASE)
  name = re.sub(r'[A-Z][a-z]+ [A-Z][a-z]+\s*[/]\s*getty images',r'',name,re.IGNORECASE)
  names.append(re.sub(resub_title_list,r'',name).strip())
  names.append(re.sub(r' [a-zA-Z][\.]? ',r' ',name).strip())
  #titleless=re.sub(resub_title_list,r'',name).strip().split(" ")
  civilian = not any([x in name.lower().split() for x in ['deputy','officer','lt','detective','special','agent','sgt','sergeant','lieutenant','sgt.','lt.','capt','capt.','captain']])
  
  if civilian and gender!=None:
    if gender!='male':
      personal_titles.append('Mrs.')
      personal_titles.append('Ms.')
    else:
      personal_titles.append('Mr.')
  if re.sub(resub_title_list,r'',name)!=name:
    titled_names.append(name)
    personal_titles.append(name.split(" ")[0])
    titleless_name=re.sub(resub_title_list,r'',name).strip()
  if len(name.split("Agent "))>1:
    names.append(name.split("Agent ")[1])
    personal_titles.append(re.sub(name.split("Agent ")[1],'',name))
    personal_titles.append("Agent")
    titleless_name=name.split("Agent ")[1]
  if len(name.split("Officer "))>1:
    names.append(name.split("Officer ")[1])
    personal_titles.append(re.sub(name.split("Officer ")[1],'',name))
    personal_titles.append("Officer")
    titleless_name=name.split("Officer ")[1]
  names.append(titleless_name)
  n = [x for x in titleless_name.split(" ") if x not in ['Jr', 'Jr.', 'III', 'IV', 'II','Sr.']]
  
  if '"' in titleless_name:
    if " aka " in titleless_name:
      aka = titleless_name.split('"')
      for m in aka:
        if ' aka ' not in m and len(m)>2:
          names.append(m)
    else:
      a=''
      found = False
      for m in n:
        if '"' in m:
          a = a+ re.sub(r'\"',r'',m)
          found = True
        elif found:
          a = a+ " " + m
      names.append(a)
  if re.search('[\'\"][A-Za-z]+[\'\"]',titleless_name):
    nickname=re.search('[\'\"][A-Za-z]+[\'\"]',titleless_name)[0]
    nickname=re.sub('\'|\"','',nickname)
    names.append(nickname+" "+n[-1])

  for t in personal_titles:
    titled_names.append(t+" "+n[-1])
    titled_names.append(t+" "+titleless_name)
    titled_names.append(t+" "+re.sub(r' [a-zA-Z][\.]? ',r' ',titleless_name).strip())
    #if len(t)>4:
     # titled_names.append(t)
  if civilian and len(n)==3:
    #if n[0] not in ['Dr','Dr.','Lt','Lt.','Detective','Officer']:
    names.append(n[0]+" "+n[2])
    names.append(n[2])
  elif len(n)>1:
    names.append(n[-1])
  names.append(n[0])
  names = list(set(names))
  final_list=[]
  for n in names:
    n=n.strip()
    n= re.sub("[ ]+"," ",n)
    if len(n)>3 and n not in ['Agent','Border','Navy','Captain']:
    
      final_list.append(n)
  titled_names=list(set([re.sub("[ ]+"," ",t) for t in titled_names]))
  #if len(list(filter(lambda name_piece: name_piece!='',name.split(" "))))<2:
  #print(name,final_list)
  return final_list,titled_names

