import sys
import os
# setting path
sys.path.append('/yourpathtohere/')
 

lexicon_dir="/yourpath/ling_features/lexicons/"
JSON_DIR="/yourpath/processed/"
csv_path = JSON_DIR+"csvs/"
masking_dir = csv_path+"masking/"
OUTPUT_DIR = '/yourpath/ling_features/csvs/'

for path in [csv_path,masking_dir,OUTPUT_DIR]:
  if not os.path.exists(path):
    try:
      os.makedirs(path)
    except:
      print("Error making", path)