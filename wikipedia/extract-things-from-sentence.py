#!/usr/bin/env python3

import gzip
import csv

def load_wikipedia_titles(file):

    things = {}

    if file[-3:] == '.gz':
        input = gzip.open(file, mode='rt', encoding='utf-8', newline='')
    else:
        input = open(file, 'r', encoding='utf-8', newline='')

    with input as f:
        reader = csv.reader(f)
        for row in reader:
            [ spaces, title, redir ] = row
            if int(spaces) > 4: # keep up to 5-word phrases
                continue
            if title.lower() == redir.lower():
                continue
            if title.startswith('List of '):
                continue
            things[title.lower()] = redir.lower()

    return things

def find_things(sentence,things):
    ret = []
    words = sentence.split(sep=' ')
    while 1:
        if len(words) == 0:
            break
        # we use look-forward because we want the longest matches possible
        for count in range(5, 0, -1):
            if len(words) >= count:
                print("checking for count", count)
                match = " ".join(words[0:count])
                if things.get(match.lower(),0) != 0:
                    print("matched", match)
                    ret.append(match.lower())
                    print("popping", count, "things from", words)
                    for blah in range(0, count-1):
                        words.pop(0)
                    break
        words.pop(0)
    return ret

things = load_wikipedia_titles("wikipedia_articles_all.csv.gz")
print("got", len(things), "things")

ret = find_things("Charles Darwin and his daughter Mary Darwin ...", things)
print("got:", ret)

