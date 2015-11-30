#!/usr/bin/env python3

import gzip
import csv
import shelve
import os

forward = {}
backward = {}

def load_wikipedia_titles(file):

    if file[-3:] == '.gz':
        input = gzip.open(file, mode='rt', encoding='utf-8', newline='')
    else:
        input = open(file, 'r', encoding='utf-8', newline='')

    with input as f:
        reader = csv.reader(f)
        for row in reader:
            [ spaces, title, redir ] = row
#            if int(spaces) > 4: # keep up to 5-word phrases XXX what if the root article has a lot of words? current we are dropping the shorter phrase, too
#                continue
#            if title.startswith('List of '):
#                continue

# I changed my mind about doing this
#            if title.startswith('Geography of'):
#                continue
#            if title.startswith('Demographics of'):
#                continue
#            if title.startswith('Government of'):
#                continue
#            if title.startswith('History of'):
#                continue
#            if title.startswith('Transportation of'):
#                continue
#            if title.startswith('Transportation in'):
#                continue
#            if title.startswith('Economy of'):
#                continue
#            if title.startswith('Communications in'):
#                continue
#            if title.startswith('Military of'):
#                continue

            forward[title] = redir
            if redir == '':
                continue

            if backward.get(redir) is None:
                backward[redir] = []
            backward[redir].extend([title])

load_wikipedia_titles(os.environ.get('VISIGOTH_DATA', '.') +"/wikipedia_articles_all.csv.gz")

# if there is no lowercase forward, let one of the partly-upper versions be lowercase
# this is needed because humans are going to type all-lower queries into our engine

print("choosing lower-case forwards...")

lower_forwards = {}

for t in forward:
    if t != t.lower():
        if t.lower() not in forward:
            # last one wins XXX not very smart, how about most popular?
            lower_forwards[t.lower()] = forward[t]

for t in lower_forwards:
    # note that we are not setting up a backlink!
    forward[t] = lower_forwards[t]

print("writing shelves...")

with shelve.open('redir_forward_shelf', flag='n', writeback=True) as s:
    for k in forward:
        s[k] = forward[k]

with shelve.open('redir_backward_shelf', flag='n', writeback=True) as s:
    for k in backward:
        s[k] = backward[k]


