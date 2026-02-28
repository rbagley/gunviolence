import re

import spacy

nlp = spacy.load('en_core_web_lg', disable=['parser', 'ner'])

def process_text(t):
  r = t[10:] if not IS_VIDEOS else t
  r = re.sub(r'<p>',r'',r)
  r = re.sub(r'<h>',r'',r)
  r = re.sub(r'\n',r'',r)
  #r = r.split("@ @ @ @ @ @ @ @ @ @")
  #for text in r:
  #texts.append(text.strip())
  doc = nlp(t.strip())
  processed = [token.lemma_.lower() for token in doc if not token.is_space] #preprocess_string(r)
  lemmas = " ".join(processed)
  return doc,lemmas
  