# LLM comparisons

To get the correct virtual environment, either create a new venv and run the 'create_env.sh' file, or use the requirements.txt file.

First, you need to generate a set of articles where articles are paired based on incident similarity but differing neighborhood racial composition.

To generate the csv with the matched subset, change path variables at the top of `cem.py` and then run `python cem.py `

You also need to mask the text for the articles, removing named entities and explicit references to race. Change the path variables at the top of `masks.py` and then run   `python masks.py`

Then, to make the predictions, change the path variables at the top of `svm.py` and run `python svm.py`