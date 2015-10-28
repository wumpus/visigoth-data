#!/usr/bin/env python3

# <http://dbpedia.org/resource/Aristotle> <http://xmlns.com/foaf/0.1/name> "Aristotle"@en .

import sys

for line in sys.stdin:
    if '/name' in line:
        first = line.find('"')
        next = line.find('"', first+1)
        name = line[first+1:next]
        if not name:
            continue

        if ' ' not in name:
            # throw out single names if there is ( or _ in the string
            if '(' in line or '_' in line:
                continue
            # throw out names if /resource/foo> does not match name
            first = line.find('/resource/')
            next = line.find('>',first+10)
            article_name = line[first+10:next]

            # unicode always causes mismatches due to an encoding mismatch, so give it a pass if the name has unicode
            # give it a pass if there's a dash in the name
            if '-' not in name and '\\u' not in name and name != article_name:
                continue

        print(name)
