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
            if '(' in line or '_' in line:
                continue
        print(name)
