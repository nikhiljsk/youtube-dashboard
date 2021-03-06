import json
import string
from collections import defaultdict
import pandas as pd
import sqlite3 as sql

def get_match_scores(words, titles, ids, descriptions):
    # Get best matching scores based on words matching title or description
    scores = defaultdict(int)
    for word in words:
        for title, id, desc in zip(titles, ids, descriptions):
            if word in title or word in desc:
                scores[id] += 1
    return scores
                

def get_best_match(text, titles, ids, descriptions):
    # Get the top matches (ids) for given word
    scores = get_match_scores(text.split(' '), titles, ids, descriptions)
    scores = {k: v for k,v in sorted(scores.items(), key=lambda item:item[1])}
    ids_matched = [x for x,y in scores.items() if y > 0][:9]
    return ids_matched


def get_word_search_results(text):
  table_name = "videos_check"
  conn = sql.connect(table_name)
  videos = pd.read_sql('select * from {0}'.format(table_name), conn)
  videos.drop_duplicates(keep='first', inplace=True, subset='id')
  conn.close()

  # Pre-processing of data for better match results
  text = text.translate(str.maketrans(string.punctuation, ' ' * len(string.punctuation))).lower()
  titles = [x.translate(str.maketrans(string.punctuation, ' ' * len(string.punctuation))).lower() for x in videos['title'].tolist()]
  descriptions = [x.translate(str.maketrans(string.punctuation, ' ' * len(string.punctuation))).lower() for x in videos['description'].tolist()]
  ids = videos['id'].tolist()

  # Get the best match and send the results
  ids_matched = get_best_match(text, titles, ids, descriptions)
  videos = videos[videos['id'].isin(ids_matched)]
  return json.loads(videos.to_json(orient ='records'))