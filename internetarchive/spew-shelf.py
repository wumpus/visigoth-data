#!/usr/bin/env python3

import shelve
import sys

for f in sys.argv[1:]:
    with shelve.open(f, flag='r') as d:
        for k in d:
            print(k,d[k])


