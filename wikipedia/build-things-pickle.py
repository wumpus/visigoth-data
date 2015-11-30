#!/usr/bin/env python3

import os
import csv
import gzip
import shelve
import pickle

lowercase_word_dict = {}
mixedcase_word_dict = {}
titlecase_word_dict = {}

things = {}

backward = shelve.open(os.environ.get('VISIGOTH_DATA','.')+'/redir_backward_shelf', flag='r')
forward = shelve.open(os.environ.get('VISIGOTH_DATA','.')+'/redir_forward_shelf', flag='r')

def load_linux_dictionary():
    with open(os.environ.get('VISIGOTH_DATA','.')+'/linux.words.centos7', 'r') as f:
        for line in f:
            # note: there are no spaces in this dictionary
            word = line.rstrip()
            rest = word[1:]
            if word.lower() == word:
                lowercase_word_dict[word] = word # all lower-case
            elif rest.lower() == rest:
                titlecase_word_dict[word.lower()] = word # first letter upper, rest lower
            else:
                mixedcase_word_dict[word.lower()] = word # more than just first letter upper

def load_wikipedia_titles():
    file = os.environ.get('VISIGOTH_DATA','.') + "/wikipedia_articles_all.csv.gz"

    if file[-3:] == '.gz':
        input = gzip.open(file, mode='rt', encoding='utf-8', newline='')
    else:
        input = open(file, 'r', encoding='utf-8', newline='')

    with input as f:
        reader = csv.reader(f)
        for row in reader:
            [ spaces, title, redir ] = row
            if int(spaces) > 4:
                # keep up to 5-word phrases, discard longer
                continue

            if title.startswith('List of '):
                continue
            if title.isdecimal():
                continue

            first = title[0] # we know this is uppercase, it always is
            rest = title[1:]

            # Multiple words
            if int(spaces) > 0:
                if rest.lower() == rest:
                    # Foo bar -> foo bar -- guess that Foo isn't actually capitalized
                    # XXX this is only somewhat true. how to fix?
                    things[title.lower()] = redir
                else:
                    # something other than first is upper; keep the case
                    things[title] = redir
                continue

            # we have a single word. Wikipedia will always title-case it if it was all-lower...
            # we want to keep proper nouns and drop wikionary entries.

            # funky capitalization. keep.
            if rest.lower() == rest:
                things[title] = redir
                continue

            mixedc = mixedcase_word_dict.get(title.lower())
            titlec = titlecase_word_dict.get(title.lower())
            lowerc = lowercase_word_dict.get(title.lower())
            if mixedc is not None:
                # mixed-case in Linux dict. Keep Linux dict case, forget Wikipedia case, keep word.
                things[mixedc] = redir
            elif titlec is not None and lowerc is None:
                # titlecase-only in linux dict. Keep word as titlecase.
                things[titlec] = redir
            elif titlec is None and lowerc is not None:
                # lowercase-only in linux dict. words like "Abolition" are in this bucket.
                # if it's got more than 2 backlinks
                print("XXX considering", title, ", which is a single word that's only lower in the linux dict")
                f = forward.get(title)
                if f == '':
                    f = title
                if f is None:
                    f = forward.get(title.lower())
                if f == '':
                    f = title.lower()
                back = backward.get(f,[])
                if len(back) > 1:
                    things[lowerc] = redir
                    print("XXX kept", lowerc, "because it has > 1 backlinks: ",len(back))
                    continue
                if 'disambiguation' in redir:
                    things[lowerc] = redir
                    print("YYY kept", lowerc, "because it redirs to disambig")
                    continue
                print("YYY dropping", title, "backlink count is", len(back))
            else:
                # titlecase and lowercase in Linux dict.
                # this happens for proper nouns Darwin/darwin and also for words commonly in titles: An The etc.
                # keep it as titlecase; use blacklist to get rid of words commonly in titles
                things[titlec] = redir

def apply_blacklist():
    with open(os.environ.get('VISIGOTH_DATA','.')+'/things-blacklist', 'r') as f:
        for line in f:
            word = line.rstrip()
            if word.istitle():
                word = word.lower()
            things.pop(word, None)
            title_word = word[0].upper()
            if len(word) > 1:
                title_word += word[1:]
            things.pop(title_word, None)

load_linux_dictionary()
load_wikipedia_titles()
apply_blacklist()

f = open("things_pickle", "wb")
pickle.dump(things, f)

