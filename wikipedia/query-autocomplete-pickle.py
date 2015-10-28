#!/usr/bin/env python3

import pickle

f = open('prefixes_pickle', 'rb') # utf8?

prefixes = pickle.load(f) # utf8?

import sys
import json

for q in sys.argv[1:]:
    answer = prefixes[q.lower()]
    sorted_list = ((k) for k in sorted(answer, key=answer.get, reverse=True))
    sorted_list = list(sorted_list)[0:5]

# non-smelly way
#    print(json.dumps({ 'query': q , 'answer': sorted_list }))

# jquery autocomplete 
    print(json.dumps(sorted_list))

