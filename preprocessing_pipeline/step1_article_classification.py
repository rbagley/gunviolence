import re
import os
import csv
import datetime
from config import *
from utils import check_article_dates,check_source_dates

places = []
with open('./international_places.txt') as infile:
  for row in infile:
    r = row.lower()
    places.append(re.sub(r'\n',r'',r))


tags = []
list1 = set(['gun','guns','firearm','firearms','shot','shooting','murder','murdered','gunfire','gunshot','shootings'])
list1a = set(['death','homicide','dead','killed','kill','killing'])
list2 = set(['blockbuster','movie','actor','actors','actress','director','game','novel','magic','spotify','netflix','concert','concerts','espn','nfl','mlb','album','earnings','hunters','dear','players','nba','music','tv','television','football','basketball','soccer'])
list3 = set(places)


def clean_article(a):
  a = re.sub(r'Posted !|Join the Conversation|Welcome to our new and improved comments , which are for subscribers only .|This is a test to see whether we can improve the experience for you .|You do not need a Facebook profile to participate .|You will need to register before adding a comment .|Typed comments will be lost if you are not logged in .|Please be polite .|It \'s OK to disagree with someone \'s ideas , but personal attacks , insults , threats , hate speech , advocating violence and other violations can result in a ban .|If you see comments in violation of our community guidelines ,|please report them .|Need an online account ?|Not a subscriber ?|Welcome to the discussion .|Keep it Clean .|Please avoid obscene , vulgar , lewd , racist or sexually-oriented language.|PLEASE TURN OFF YOUR CAPS LOCK.|Do n\'t Threaten .|Threats of harming another person will not be tolerated.Be Truthful .|Do n\'t knowingly lie about anyone or anything.|Be Nice .|No racism , sexism or any sort of -ism that is degrading to another person.Be Proactive .|Use the \' Report \' link on each comment to let us know of abusive posts.|Share with Us .|We \'d love to hear eyewitness accounts , the history behind an article .|Watch this discussion.|Stop watching this discussion .',r'',a)
#  pieces = a.split("<h>")
#  all_pieces = re.split(r'<h>|<p|@ @ @ @ @ @ @ @ @ ',a)
 # final = []
#  for p in pieces:
 #   if "@ @ @ @ @ @ @ @ @ " in p:
  #    more_pieces = p.split("@ @ @ @ @ @ @ @ @ ")
   #   for m in more_pieces:
    #    if "<p>" in m:
     #     even_more = m.split("<p")
      #    for e in even_more:
       #     all_pieces.append(e)
        #else:
         # all_pieces.append(m)
#    elif "<p>" in p:
 #     more_pieces = p.split("<p")
  #    for m in more_pieces:
   #     all_pieces.append(m)
    #else:
     # all_pieces.append(p)
  
#  for piece in all_pieces:
 #   p = piece.lower()
  #  if 'email notification' not in p and 'subscribe' not in p and 'thank you' not in p and ") comments" not in p and 'log in' not in p and 'fcc' not in p and 'sign in' not in p and 'signing in' not in p and 'inbox' not in p and 'privacy policy' not in p and 'rights reserved' not in p and 'your notification' not in p and 'subscription' not in p and 'commenter' not in p and 'commenting section' not in p and 'top comments' not in p and 'advertiser' not in p and 'featured comments' not in p and 'terms of service' not in p and 'moderate comments' not in p and 'moderating decision' not in p and 'email update' not in p and 'democracy now !' not in p and 'flag as inappropriate' not in p and 'reserve the right' not in p and 'terms of use' not in p and 'at no additional charge' not in p and 'station policy' not in p and 'regarding NPR' not in p and (len(p.strip().split(" "))>3 or piece==all_pieces[0]):
    #  final.append(piece) 
  #next = "<h>".join(final)
  #next = re.sub(r"<h>@",r'@ @ @ @ @ @ @ @ @ @',next)
  return a#re.sub(r"<h>>",r"<p>",next)
 
def classify_articles(year):
  articles = []
  article_dict={}
  article_content=[]
  print("classifying")
  output = OUTPUT_DIR+year
  path = output+"/article_data"
  ids=[]
  with open("./url_matches.csv",'r') as csvfile: 
    reader = csv.DictReader(csvfile)
    for row in reader:
      ids.append(str(row['article_id']))
  if not os.path.exists(path):
    try:
      os.makedirs(path)
    except:
      print("tried to make new directory when it exists")
  path = output+"/sorted_articles"
  if not os.path.exists(path):
    try:
      os.makedirs(path)
    except:
      print("tried to make new directory when it exists")
  directory = ARTICLE_DIR
  for filename in os.listdir(directory):
    f = os.path.join(directory,filename)
    if ("us" in filename or "US" in filename) and os.path.isfile(f) and check_article_dates(filename,year):
      print(f)
      with open(f,'r') as infile:
        for row in infile:
          r=re.sub(" @@","\n@@",row)
          pieces=r.split("\n")
          for p in pieces:
            if len(p)>2:
              row_set = set(p.lower().split())
              r = p.lower()
              article_id=p[2:].split()[0]
              if article_id in ids or ( (list1.intersection(row_set) or 'assault rifle' in r or 'assault weapon' in r) and len(list3.intersection(row_set))<3):#and not list2.intersection(row_set)  and ('spray gun' not in r and 'flood gun' not in r and 'emission gun' not in r and 'nerf gun' not in r and not 'radar gun' in r and 'anti-aircraft gun' not in r and 'starting gun' not in r and 'water gun' not in r and 'super bowl' not in r and 'music video' not in r and 'video game' not in r and 'machine gun kelly' not in r and 'guns n roses' not in r and 'guns n \' roses' not in r and 'smoking gun' not in r and 'big guns' not in r and 'young gun' not in r and 'jump the gun' not in r and 'jumping the gun' not in r and 'under the gun' not in r and 'james bond' not in r):
                
                p = clean_article(p)
                if p[11:] not in article_content:
                  article_dict[article_id]=p
                  articles.append(p)
                  article_content.append(p[11:])
                  tags.append({'issue':False,'incident':False,'armed_robbery':False,'irrelevant':False,'nonviolent':False,'drugs':False,'opinion':False})
  count=0
  c=0
  final_articles=[]
  directory = ARTICLE_SOURCE_DIR
  for filename in os.listdir(directory):
    f = os.path.join(directory,filename)
    if os.path.isfile(f) and check_source_dates(filename,year):
      #print(f)
      with open(f, errors='ignore') as infile:
        for row in infile:
          r = row.split('\t')
          if article_dict.get(r[0],None) and r[3].lower()=='us':
            c+=1
            headline = set(r[6].lower().split())
            if (list2.intersection(headline) or len(list3.intersection(headline))) and not (list1.intersection(headline) or list1a.intersection(headline)):
              if count<10:
                print(headline)
              count+=1
              continue
            else:
              final_articles.append(article_dict[r[0]])
  print(len(articles),len(final_articles),c,count)
  with open(output+'/sorted_articles/initial_sort.txt','w') as outfile:
    for a in final_articles:
      outfile.write(re.sub(r'\n+',r'\n',a+"\n"))

def write_subcategories():  
  issues=0
  irrelevant = []    
  with open(output+'/sorted_articles/issues.txt','w') as outfile:
    for i,article in enumerate(articles):
      a = article.lower()
      if 'gun violence' in a or 'gun control' in a or 'campaign' in a or 'gun rights' in a or 'amendment' in a or 'gun policy' in a or 'democratic' in a or 'republican' in a or 'partisan' in a or 'liberal' in a or 'conservative' in a or 'background check' in a or 'proposed bill' in a or 'red flag' in a or 'legislation' in a or 'permitless carry' in a or 'concealed carry' in a or 'congress' in a or 'prohibit' in a or 'school district' in a or 'school board' in a:
        #print(re.findall(r'gun|firearm|rifle',a,re.IGNORECASE))
        if len(re.findall(r'[^e]gun|firearm|rifle',a,re.IGNORECASE))>1:
          outfile.write(re.sub(r'\n+',r'\n',article+"\n"))
          tags[i]['issue'] = True
          issues+=1
        else:
          irrelevant.append(a)
          tags[i]['irrelevant']=True
       
  incidents = 0   
  with open(output+'/sorted_articles/incidents.txt','w') as outfile:
    for i,article in enumerate(articles):
      a = article.lower()
      if ('fatal' in a or 'shoot' in a or 'discharg' in a or 'shot ' in a or 'injur' in a or 'murder' in a or 'dead ' in a or 'fired' in a) and 'simulat' not in a and 'shooter drill' not in a and 'no weapons' not in a:
        outfile.write(re.sub(r'\n+',r'\n',article+"\n"))    
        tags[i]['incident'] = True
        incidents +=1

  opinions = 0   
  with open(output+'/sorted_articles/opinions.txt','w') as outfile:
    for i,article in enumerate(articles):
      a = article.lower()
      if 'opinion' in a or 'editorial' in a:
        outfile.write(re.sub(r'\n+',r'\n',article+"\n"))    
        tags[i]['opinion'] = True
        opinions +=1
    
  robberies = 0   
  with open(output+'/sorted_articles/armed_robberies.txt','w') as outfile:
    for i,article in enumerate(articles):
      a = article.lower()
      if 'stole' in a or 'robbery' in a or 'steal' in a or 'robbed' in a or 'carjack' in a:
        outfile.write(re.sub(r'\n+',r'\n',article+"\n"))    
        tags[i]['armed_robbery'] = True
        robberies +=1
  
  nonviolent = 0   
  with open(output+'/sorted_articles/nonviolent.txt','w') as outfile:
    for i,article in enumerate(articles):
      a = article.lower()
      if 'threat' in a or 'gunpoint' in a or 'brandish' in a or 'possession' in a or 'pursuit' in a or 'chase' in a or 'point a gun' in a or 'pointed a gun' in a or 'pointing a gun' in a or 'point at' in a or 'pointed at' in a or 'pointing at' in a or 'endangerment' in a or 'lockdown' in a:
        outfile.write(re.sub(r'\n+',r'\n',article+"\n"))    
        tags[i]['nonviolent'] = True
        nonviolent +=1
  
  drugs = 0   
  with open(output+'/sorted_articles/drugs.txt','w') as outfile:
    for i,article in enumerate(articles):
      a = article.lower()
      if 'drugs' in a or 'marijuana' in a or 'cocaine' in a or 'meth' in a:
        outfile.write(re.sub(r'\n+',r'\n',article+"\n"))    
        tags[i]['drugs'] = True
        drugs +=1
  
  other = 0
  with open(output+'/sorted_articles/other.txt','w') as outfile:
    for i,a in enumerate(articles):
      if not tags[i]['issue'] and not tags[i]['incident'] and not tags[i]['armed_robbery'] and not tags[i]['irrelevant'] and not tags[i]['nonviolent'] and not tags[i]['drugs'] and not tags[i]['opinion']:
        outfile.write(re.sub(r'\n+',r'\n',a+"\n"))  
        other+=1  
  
  print("sorted NOW",len(articles),incidents,issues,robberies,nonviolent,drugs,len(irrelevant),other)


