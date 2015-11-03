#!/usr/bin/env python3

import shelve
import os

metadata = shelve.open('metadata_shelf', flag='w', writeback=True)

press_names = {}
unpress_names = {}
wiki_isbn_rank = {}
pulp_rank = {}

def read_press_names():
    f = open(os.environ.get('VISIGOTH_DATA', '.')+'/university-presses', 'r')
    for line in f:
        line = line.rstrip()
        press_names[line] = 1
        if line.endswith(' Press'):
            unpress = line[0:-len(' Press')]
            if ' ' in unpress: # don't do this for Island Press or Beacon Press or Army Press
                unpress_names[unpress] = 1

def read_wiki_isbn_rank():
    f = open(os.environ.get('VISIGOTH_DATA', '.')+'/wiki-isbn-rank', 'r')
    for line in f:
        line = line.rstrip()
        count, isbn13 = line.split(' ')
        wiki_isbn_rank[isbn13] = int(count)

def read_pulp_rank():
    f = open(os.environ.get('VISIGOTH_DATA', '.')+'/bwb isbns seen July 19 to Oct 19 2015.txt', 'r')
    for line in f:
        isbn13, pulprank = line.split() # this file has multiple whitespace
        if isbn13 == 'ISBN': # header line
            continue
        pulp_rank[isbn13] = int(pulprank)

read_press_names()
read_wiki_isbn_rank()
read_pulp_rank()

stats = {}

for ia_id in metadata:
    stats['ia_ids'] = stats.get('ia_ids', 0) + 1

    isbns = metadata[ia_id].get('isbn13s', {}).keys()
    for i in isbns:
        if i in wiki_isbn_rank:
            m = metadata[ia_id].get('raw_rank', {})
            m['wiki_isbn_rank'] = max(m.get('wiki_isbn_rank', 0), wiki_isbn_rank[i]) # taking max instead of sum, because lazy
            metadata[ia_id]['raw_rank'] = m
            stats['wiki_isbn'] = stats.get('wiki_isbn', 0) + 1
        if i in pulp_rank:
            m = metadata[ia_id].get('raw_rank', {})
            m['pulp_rank'] = max(m.get('pulp_isbn_rank', 0), pulp_rank[i]) # taking max instead of sum, because lazy
            metadata[ia_id]['raw_rank'] = m
            stats['pulp_rank'] = stats.get('pulp_rank', 0) + 1

    #publisher = metadata[ia_id].get('publisher', '') # after the metadata shelf is updated XXX
    publisher = metadata[ia_id].get('publisher', '').replace('\n', ' ').replace('  ', ' ')
    hit = 0
    for p in press_names.keys():
        if p in publisher:
            hit = 1
            m = metadata[ia_id].get('raw_rank', {})
            m['academic_press'] = 1
            metadata[ia_id]['raw_rank'] = m
            stats['academic_press'] = stats.get('academic_press', 0) + 1
            continue
    if hit > 0:
        continue
    for p in unpress_names.keys():
        if p in publisher:
            m = metadata[ia_id].get('raw_rank', {})
            m['academic_press'] = 1
            metadata[ia_id]['raw_rank'] = m
            stats['academic_press'] = stats.get('academic_press', 0) + 1
            stats['unacademic_press'] = stats.get('unacademic_press', 0) + 1
            continue

for ia_id in metadata:
    if metadata[ia_id].get('raw_rank') is not None:
        stats['nonzero_rank'] = stats.get('nonzero_rank', 0) + 1

metadata.close()

print("stats are", stats)
