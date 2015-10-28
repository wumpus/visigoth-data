#!/usr/bin/env python3

# zcat sum-pagecounts.out.gz | ./pagecounts-to-autocomplete.py

import fileinput
import pickle

def topn(n, d):
    """
    Trims dict d to keycount n, sorting for the largest values
    """
    sorted_list = ((k, d[k]) for k in sorted(d, key=d.get, reverse=True))
    sorted_list = list(sorted_list)[0:n]

    ret = {}

    for k, v in sorted_list:
        ret[k] = v

    return ret

prefixes = {}

for line in fileinput.input():

    line = line.rstrip()

    parts = line.rsplit(sep=',', maxsplit=1)

    name, count = parts

    name = name.replace('_', ' ')
    if name == 'Main Page':
        continue
    count = int(count)

# 10,000:   8090295 bytes of output
#  5,000:  19309278 bytes
#  2,000:  52682593 bytes
#  1,000: 101589585 bytes
#    500: 182028565 bytes
#    200: 373095156 bytes
#    100: 624874192 bytes - 624 megabytes
#    100: 574321335 bytes - 548 megabytes - int count
#    100: 567319419 bytes - keeping only 5 items. wow, lots of leaves!
#    100: 125786263 bytes - 120 megabytes - max 10 characters of autocomplete
#     50: 193349734 bytes - 185 megabytes
#    100: 261159421 bytes - 250 megabytes - max 15 characters of autocomplete

    if int(count) < 100:
        break

    for l in range(min(len(name), 15)):
        prefix = name[0:l+1].lower()

        if prefixes.get(prefix) is None:
            prefixes[prefix] = {}

        prefixes[prefix][name] = count

        if len(prefixes[prefix]) > 20: # don't want to trim too often, it's expensive. waste memory intead.
            prefixes[prefix] = topn(5, prefixes[prefix])

for prefix in prefixes:
    if len(prefixes[prefix]) > 5:
        prefixes[prefix] = topn(5, prefixes[prefix])

f = open("prefixes_pickle", 'wb') # utf-8?

pickle.dump(prefixes, f)
