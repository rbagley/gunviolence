import sys
import os
# setting path
path='/path/to/here/gunviolence_pnas/'
sys.path.append(path)
 

OUTPUT_DIR=path+"processed/"
GVA_INCIDENT_CSV="/path/to/file_with_geoids.csv"
GVA_PARTICIPANT_CSV="/path/to/participant_file.csv"
CENSUS_KEY='your_key'

SUBSET_DIR="/path/for/matched/subset/"

path = OUTPUT_DIR+"csvs/"
if not os.path.exists(path):
    try:
      os.makedirs(path)
    except:
      print("tried to make new directory when it exists")
masking_dir = path+"masking/"

