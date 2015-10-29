#!/usr/bin/env python3

import gzip
import csv
import pickle

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
            if int(spaces) > 4: # keep up to 5-word phrases XXX what if the redir has a lot of words?
                continue
            if title.lower() == redir.lower(): # case-changing redir. skip.
                continue
            if title.startswith('List of '):
                continue

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

            if redir == '':
                continue
            forward[title.lower()] = redir
            if backward.get(redir.lower()) is None:
                backward[redir.lower()] = []
            backward[redir.lower()].extend([title]) # keep this upper-case

#            if len(backward[redir]) > 1 and 'of' in title:
#                print("Multiple redirs:", redir, backward[redir])

load_wikipedia_titles("wikipedia_articles_all.csv.gz")

# do something to get rid of the case-changing redirs ... keep the version with the most upper-case
for b in backward:
    uniq = {}
    for a in backward[b]:
        if uniq.get(a.lower()) is not None:
            # this only strips leading/trailing lower-case, really I should use .maketrans / .translate instead XXX
            old_strip = uniq[a.lower()].strip('abcdefghijklmnopqrstuvwxyz')
            new_strip = a.strip('abcdefghijklmnopqrstuvwxyz')
            if len(new_strip) > len(old_strip):
                uniq[a.lower()] = a
        else:
            uniq[a.lower()] = a

    backward[b] = list(uniq[k] for k in uniq.keys())

# debug
print("Pope forward", forward.get('pope'), ", Pope backward", backward.get('pope'))

f = open("redirs_pickle", "wb")
pickle.dump({'forward': forward, 'backward': backward}, f)

#import shelve
#
#with shelve.open('redir_forward_shelf', flag='n', writeback=True) as s:
#    for k in forward:
#        s[k] = forward[k]
#
#with shelve.open('redir_backward_shelf', flag='n', writeback=True) as s:
#    for k in backward:
#        s[k] = backward[k]


