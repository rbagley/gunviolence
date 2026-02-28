import sys
 
# setting path
path = '/path/to/parent/folder/gunviolence_pnas/'
sys.path.append(path)
 
# importing
from config_base import IS_VIDEOS


OUTPUT_DIR=path+"processed/" 

TIMEFRAME=365 #max number of days between incident and article
#IS_VIDEOS=False
WITH_CENSUS_DATA=True
MIN_YEAR=2014
MAX_YEAR=2023

GVA_CSV='path/to/incidents.csv'
GVA_PARTICIPANT_CSV='path/to/participants.csv'
GVA_WITH_GEOID='your_path_for_updated_file.csv'

GIS_PATH='path_to_gis_data' #download from https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.2018.html#list-tab-790442341
ARTICLE_SOURCE_DIR='/your_path/NOW/sources'
ARTICLE_DIR= '/your_path/NOW/text'

SOURCE_CSV=path+"sources/source_locations_new_complete.csv"
ARTICLE_SUBSET = 'initial_sort' #Options: incidents, issues, opinions, nonviolent,drugs, armed_robberies, initial_sort (all gun-related articles) 
INCREMENT=5

