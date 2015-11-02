#!/usr/bin/env python3

import csv
import sys
import isbntools.app
import isbnlib

isbns = {}

rows = csv.reader(sys.stdin, delimiter=',')
for row in rows:
    if len(row) != 2:
        continue
    [ title, isbn ] = row

    if isbn is None:
        continue
    if len(isbn) == 10:
        isbn = isbntools.app.to_isbn13(isbn)
        if isbn is None:
            continue
    if len(isbn) != 13:
        continue
    if not isbnlib.is_isbn13(isbn):
        print("skipping invalid isbn of", isbn, "from article", title, file=sys.stderr)
        continue

    isbns[isbn] = isbns.get(isbn,0) + 1

sorted_list = ((i, isbns[i]) for i in sorted(isbns, key=isbns.get, reverse=True))

for i, count in sorted_list:
    print(count, i)



