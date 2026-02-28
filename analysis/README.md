# Processing the matched data

To further process the matched data, you should do the following:

1. Add the correct output directory paths to config.py
2. Run `python ent_masking.py` --year YEAR
    This masks all the named entities in each article text and writes a csv for each year containing all the masked sentences for each year, identified by the article id. This can take some time, so it is run year by year to allow simultaneous processing of years.
3. Run `python notable.py` 
    This identifies all the incidents that get the most attention in a given year, and adds a feature to each article in the dataset identifying all 'notable' incidents that they mention (identified through our matching algorithm)
4. Run `python process_gva.py`
    This gathers census tract features for the country so they can be linked to incidents
5. If you want to use linguistic features, proceed to the ling_features folder
6. Generate the csvs with: `python generate_csvs.py --with_features=True` if using linguistic features, otherwise: `python generate_csvs.py --with_features=False`