print("beginning")
import argparse
import datetime
from config import *
import os
import time
import re
import json
#IS_YEAR=True

def read_matches(year,segment,articles):
  if segment==0 or segment==None:
    segment=''
  matches={}
  rev_matches = {}
  num_incidents = []
  num_articles=[]
  directory=OUTPUT_DIR+year+"/sorted_articles"
  for filename in os.listdir(OUTPUT_DIR+year+"/sorted_articles"):
    f = os.path.join(directory,filename)
    if os.path.isfile(f) and filename.startswith('id_matches'):
      with open(f,'r') as infile:
        for i,row in enumerate(infile):
          r= re.sub(r'\n',r'',row)
          r=r.split("\t")
          if articles.get(r[0],None):
            s = set(r[1].split(", "))
            m = matches.get(r[0],[])
            m+=list(s)
            matches[r[0]]=m
            num_incidents.append(len(s))
  print(len(num_incidents))
  return matches
  
def not_as_good():
  with open(OUTPUT_DIR+year+"/sorted_articles/id_matches"+str(segment)+".txt",'r') as infile:
    for i,row in enumerate(infile):
      r= re.sub(r'\n',r'',row)
      r=r.split("\t")
      s = set(r[1].split(", "))
      matches[r[0]] = list(s)
      num_incidents.append(len(s))
  with open(OUTPUT_DIR+year+"/sorted_articles/id_matches"+str(INCREMENT)+".txt",'r') as infile:
    for i,row in enumerate(infile):
      r= re.sub(r'\n',r'',row)
      r=r.split("\t")
      if articles.get(r[0],None):
        s = set(r[1].split(", "))
        m = matches.get(r[0],[])
        m+=list(s)
        matches[r[0]]=m
        num_incidents.append(len(s))
  print(len(num_incidents))
  return matches
      
  for filename in os.listdir(OUTPUT_DIR+year+"/sorted_articles"):
    f = os.path.join(directory,filename)
    if os.path.isfile(f) and 'id_matches' in filename:
      with open(f,'r') as infile:
        for row in infile:
          r= re.sub(r'\n',r'',row)
          r=r.split("\t")
          s = set(r[1].split(", "))
          matches[r[0]] = list(s)
          num_incidents.append(len(s))
  
    
def parse_commandline():
    """Parse the arguments given on the command-line.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--step",
                       help="match,write,classify",
                       default='match')
    parser.add_argument("--year",
                       help="year",
                       default=None)
    parser.add_argument("--other",
                       help="year",
                       default=None)

    args = parser.parse_args()
    IS_YEAR = (args.step!='match')
    if 'video' not in OUTPUT_DIR:
      year = int(args.year)  if IS_YEAR else 2014 + int(args.year)//INCREMENT
    
      segment = None if IS_YEAR else int(args.year) % INCREMENT
      other = int(args.other) if args.other!=None else None
    else:
      year = int(args.year)  if IS_YEAR else  2020 + int(args.year)//12
      segment = None if IS_YEAR else 1+ (int(args.year) % 12)
      other = int(args.other) if args.other!=None else None
    return args.step,str(year),segment,other
    

if __name__ == '__main__':
  from step1_article_classification import classify_articles
  from step2_read import add_data
  from step2a_video import add_video_data
  from add_geoids import get_geoids
  
  step,year,segment,extra = parse_commandline()   
  if int(year)<MIN_YEAR or int(year)>MAX_YEAR:
    print("year out of range")
  elif step=='classify':
     classify_articles(year)
     get_geoids()
  else:
    incidents,articles = add_data(year,segment) if not IS_VIDEOS else add_video_data(year,segment)
    print(year,segment,extra)
    
    if step=='match':
  #def temp():
      from step3_matching import matchAll
      matches,rev_matches = matchAll(incidents,articles,year,segment)
    
    elif step=='write':
      from step4_build_dicts import create_data_structures
      from step5_filter_write import write_json
    #  matches=None
    #  files_should_move=False
    #  matches,rev_matches = match_urls({},{},incidents,articles,year)
    #  
    #  if matches: files_should_move=True 
      
      matches = read_matches(year,segment,articles)
      data = create_data_structures(incidents,articles,matches)
      write_json(data,year)
  
  #BE CAREFUL WITH THIS ONE
  #if files_should_move:
   # move_old_files(year)
