#!/usr/bin/env python3

import shelve
import sys

print("saw filename of", sys.argv[1])

with shelve.open(sys.argv[1], flag='r') as d:
    for k in sys.argv[2:]:
        print(k, ',', d.get(k))

