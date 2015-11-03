#!/usr/bin/env python3

import fileinput
import shelve
import isbntools.app
import isbnlib
import re

entry = ''
ia_id = ''

metadata = shelve.open('metadata_shelf', flag='n', writeback=True)
isbn13_to_ia_id = shelve.open('isbn13_to_ia_id', flag='n', writeback=True)

def process(ia_id, entry):
    if entry == '': # first entry will be empty
        return

    meta = {}

    # the entry may or may not have carriage returns. don't depend on them.

    matches = re.findall('dc:title\>([^\<]+)\</dc:title', entry)
    if len(matches) > 1:
        print("multiple dc:title seen in", ia_id)
    elif len(matches) == 1:
        meta['title'] = matches[0].rstrip(',.').strip()

    matches = re.findall('dc:publisher\>([^\<]+)\</dc:publisher', entry)
    if len(matches) > 1:
        print("multiple dc:publisher seen in", ia_id)
    elif len(matches) == 1:
        publisher = matches[0].rstrip(',.').strip().replace('\n', ' ').replace('  ', ' ')
        meta['publisher'] = publisher

    matches = re.findall('dc:date\>([^\<]+)\</dc:date', entry)
    if len(matches) > 1:
        print("multiple dc:date seen in", ia_id)
    elif len(matches) == 1:
        meta['date'] = matches[0].rstrip(',.').strip()

    isbn_seen = {}

    matches = re.findall('dc:identifier\>([^\<]+)\</dc:identifier', entry)
    for m in matches:
        if m.startswith('URN:ISBN:'):
            m = m[len('URN:ISBN:'):] # strip off that prefix
            m = m.rstrip('.,')
            # m = m.replace(' ','') -- doesn't fit with the excuse syntax?
            m = m.replace('\n',' ') # sometimes between isbn and excuse
            m = m.replace('-','')
            excuse = ''
            if ' ' in m:
                isbn, excuse = m.split(' ', maxsplit=1)
            else:
                isbn = m
            if len(isbn) == 10:
                isbn = isbntools.app.to_isbn13(isbn)
                if isbn is None: # failed conversion
                    print("failed conversion of isbn10 to isbn13 in", ia_id)
                    continue
            if len(isbn) != 13:
                print("bad length of isbn", isbn, "in", ia_id)
                continue
            if not isbnlib.is_isbn13(isbn):
                print("invalid isbn13 of", isbn, "in", ia_id)
                continue

            if isbn in isbn_seen:
                if excuse != '':
                    meta['isbn13s'][isbn] = excuse
            else:
                meta['isbn13s'] = meta.get('isbn13s', {})
                meta['isbn13s'][isbn] = excuse

                isbn13_to_ia_id[isbn] = isbn13_to_ia_id.get(isbn, [])
                isbn13_to_ia_id[isbn].append(ia_id) # ok because writeback=True

                isbn_seen[isbn] = 1
        else:
            if m.startswith('http'):
                continue
            print("found a non-ISBN identifier in", ia_id, "of", m)

    metadata[ia_id] = meta
    return

for line in fileinput.input():
    if line.startswith('IA_ID '):
        process(ia_id, entry)
        entry = ''
        ia_id = line[len('IA_ID '):].rstrip()
    entry += line

process(ia_id, entry)

metadata.close()
isbn13_to_ia_id.close()

