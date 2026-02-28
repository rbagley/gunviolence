# Preprocessing Pipeline
This pipeline uses data from GVA, articles from NOW, and census data to produce a set of json files corresponding to specific articles matched to incidents of gun violence.

In order to run this code, you need:
    1. census tract shapefiles for all states (we used 2018, from https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.2018.html#list-tab-790442341)
    2. Csvs from GVA
    3. Articles from NOW

Then, change the paths in 'config.py' to the correct directories.

For any given year you want to match, run:
    python master.py --year YEAR --step classify
    python master.py --year YEAR --step match
    python master.py --year YEAR --step write