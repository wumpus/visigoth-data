#!/usr/bin/env python3

import shelve
from sys import argv

backward = shelve.open('redir_backward_shelf', flag='r')

argv = argv[1:]
for a in argv:
    print("For", a, ", found ", backward.get(a.lower(), []))

