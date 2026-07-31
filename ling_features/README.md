# Gather all linguistic features
 Before you begin, change the paths in config.py and run `python masking.py`

 Each of the following sets of features can be run separately if you only want to use a subset of possible features, or you can run all of them.

 Also, several of these features have conflicting package dependencies, so they have their own virtual environments.

 ## Agency
 Note: depending on the size of the dataset you are analyzing, this can use a lot of RAM and take a long time. Using a GPU and/or simultaneously running several jobs on smaller batches of data can substantially speed up the process. 
 If you choose to run each year individually, set IS_YEAR=True (line 16), and uncomment lines 401-404, and comment out line 409-411. If you wished to run data from 2016, you would then run `python srl_agency.py --year 2016` 

 Be sure to create a virtual environment for this file; the requirements are located in srl_requirements.txt

 There are two options for this feature: running agency for victims, shooters, and police participants `run(year, predictor,agency)`, or also analyzing any mention of police `run_plus_police(year, predictor,agency)`.

 After running the code, you should end up with a csv for each year in your dataset. In order to synthesize them into a single file, you should use the `combine_updated()` method if you used `run(...)`, and `combine_police()` if you used `run_plus_police(...)`.

 ## Concreteness and Subjectivity
 These two features use the same prepared data, so you can just run `python consolidate.py` to more efficiently get both features. If you only wish to run one feature, you can borrow the code from concrete.py and subjectivity.py, or you can comment out line 40 or 41 in consolidate.py
 
 ## Speakers and mentions related to people
 Run `python add_new_vars.py`

 ## Readability
 First, create and activate a virtual environment based on readability_requirements.txt
 Then run `python readability.py`

 ## Formality
 Create and activate a virtual environment based on formality_requirements.txt

 Like agency, this one can take a long time if classifying all the data sequentially, so it is designed to run on one year at a time, so you can run each of them simultaneously if you like, e.g. `python formality.py --year 2016`

 ## Participant Framing
 This feature requires the virtual environment used in the bert folder. If you haven't already created that, go to the bert folder and either create a new venv and run the 'create_env.sh' file, or use the requirements.txt file. 
 Make sure you activate the environment and then run `framing_predictions.py` (make sure to change the path names at the top of the file as appropriate)

 # Final step
 After running all the linguistic features, use `python combine.py` to consolidate all the data into a single csv.
 Then return to the `analysis` folder and `run python generate_csvs.py --with_features=True` to generate the final csv that includes all incident features, article features, and linguistic features.








