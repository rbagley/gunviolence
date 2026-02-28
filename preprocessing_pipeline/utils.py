from config import *
import re
import datetime

def check_article_dates(f,year):
  start=datetime.date(int(year),1,1)
  end=datetime.date(int(year),12,31)
  d = f.split('-')
  year = d[0][5:] if '_' in d[0] else d[0]
  date = datetime.date(int("20"+year),int(d[1]),1)
  return date >= start and date<= end
  
def check_incident_dates(f,year):
  start=datetime.date(int(year),1,1)
  end=datetime.date(int(year),12,31)
  d = f.split('-')
  date = datetime.date(int(d[0]),int(d[1]),int(d[2]))
  return date >= start-datetime.timedelta(days=TIMEFRAME) and date<= end
  
def check_source_dates(f,year):
  start=datetime.date(int(year),1,1)
  end=datetime.date(int(year),12,31)
#  d = re.split(r'-|\.',f)
 # date = datetime.date(int("20"+d[1]),int(d[2]),1)
  f = re.sub(".txt","",f)
  f = re.sub("sources-","",f)
  d = re.split('-',f)
  if len(d)==1:
    year = int(d[0])
  else:
    year= int("20"+d[0])
  return year >= start.year and year<= end.year
 
def get_address_variants(add):
  adds=[add]
  adds.append(re.sub(r' [rd|road|street|st|ave|avenue|drive|dr]$','',add,re.IGNORECASE))
  return list(set(adds))
   
def get_name_variants(name,ignorecase=False,loose=False):
  names = [name]
  var_titles=['Mr','Mrs','Ms','Dr','Sgt','Col','Lt']
  exact_titles=['Miss','Officer','Sheriff','Deputy','Detective','Agent','Sergeant','Lieutenant']
  titles = [t+"." for t in var_titles]+[t+' .' for t in var_titles]+var_titles+exact_titles
  name = re.sub(r'photo by [A-Z][a-z]+ [A-Z][a-z]+',r'',name,re.IGNORECASE)
  name = re.sub(r'[A-Z][a-z]+ [A-Z][a-z]+\s*[/]\s*getty images',r'',name,re.IGNORECASE)
  names.append(re.sub(r'Deputy|Officer|Lt|Lt.|Dr|Dr.|Detective|Special Agent|Sgt|Sgt.|Sergeant|Lieutenant',r'',name).strip())
  names.append(re.sub(r' [a-zA-Z][\.]? ',r' ',name).strip())
  n = name.split(" ")
  if '"' in name:
    if " aka " in name:
      aka = name.split('"')
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
  if len(n)==3 and n[2] not in ['Jr', 'Jr.', 'III', 'IV', 'II'] and n[0] not in ['Dr','Dr.','Lt','Lt.','Detective','Officer', 'Deputy'] and not re.match("Michael \w+ Brown", name):
    names.append(n[0]+" "+n[2])
  if loose:
    if len(n)==3 and n[2] not in ['Jr', 'Jr.', 'III', 'IV', 'II'] and n[0] in ['Dr','Dr.','Lt','Lt.','Detective','Officer','Deputy']:
      names.append(n[0]+" "+n[2])
    last = last_name(name)
    first = first_name(name)
    if last:
      #names+=[t + " " + last for t in titles]
      names.append(last)
    if first:
      names.append(first)
  else:
    if 'Michael Brown' in names:
      names=[name]
  names = list(set(names))
  final_list=[]
  for n in names:
    n=n.strip()
    if len(n)>3 and (len(n.split(" "))>1 or loose) and n.lower() not in ['store employee','security officer','police officer','security guard','corrections officer','not given','delivery driver','fbi agent','atf agent','swat officer','chp officer','unborn child','federal agent','unidentified suspect','dea agent','family dollar store','family dollar','shell gas station','circle k','rite aid','chase bank','special agent']:
      if not ignorecase:
        if n[0].lower()!=n[0]:
          final_list.append(n)
      else:
        final_list.append(n)
  #if len(list(filter(lambda name_piece: name_piece!='',name.split(" "))))<2:
   # print(name,final_list)
  #print("final:",final_list)
  return final_list

def gather_keywords(i):
  keywords=[]
  if i['address']:
    keywords.append(i['address'].lower())
  if i['place_name']:
    keywords.append(i['place_name'].lower())
  for p in i['participants']:
    if p.get('name',None) and p['name'].lower()!='officer' and len(p['name'])>2:
      keywords+=[n.lower() for n in get_name_variants(p['name'],True,True)]
    if p.get('name',None):
      if 'officer' in p['name'].lower():
        keywords.append('officer')
      if 'police' in p['name'].lower():
        keywords.append('police')
  #print(keywords)
  return keywords

def last_name(name):
  n= name.lower()
  n=n.split(" ")
  n=list(filter(skip_suffix,n))
  if len(n)>0:
    return n[len(n)-1]
  else:
    return None

def skip_suffix(piece):
  return piece not in ['jr','jr.','sr','sr.','ii','iii','iv']

def first_name(name):
  n= name.lower()
  n=n.split(" ")
  n=list(filter(skip_title,n))
  if len(n)>0:
    return n[0]
  else:
    return None

def skip_title(piece):
  return piece not in ['mr','mrs','ms','dr','sgt','col','lt', 'miss','officer','sheriff','deputy','detective','agent','sergeant','lieutenant','.']