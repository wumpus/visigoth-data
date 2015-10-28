#!/usr/bin/env python3

import pickle

things = {}
revthings = {}

def load_wikipedia_titles(file):

    if file[-3:] == '.gz':
        input = gzip.open(file, mode='rt', encoding='utf-8', newline='')
    else:
        input = open(file, 'r', encoding='utf-8', newline='')

    with input as f:
        reader = csv.reader(f)
        for row in reader:
            [ spaces, title, redir ] = row
            if int(spaces) > 4: # keep up to 5-word phrases XXX what if the redir has a lot of words?
                continue
            if title.lower() == redir.lower(): # case-changing redir. skip.
                continue
            if title.startswith('List of '):
                continue
            things[title] = redir
            # the reverse direction can be a list
            revthings[redir] = revthings.get(redir,[]).extend(title)

load_wikipedia_titles("wikipedia_articles_all.csv.gz")
