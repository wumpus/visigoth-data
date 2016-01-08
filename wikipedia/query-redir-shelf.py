#!/usr/bin/env python3

import shelve
from sys import argv
import os

backward = shelve.open(os.environ.get('VISIGOTH_DATA','.')+'/redir_backward_shelf', flag='r')
forward = shelve.open(os.environ.get('VISIGOTH_DATA','.')+'/redir_forward_shelf', flag='r')

argv = argv[1:]
for a in argv:
    f = forward.get(a)
    if f == '':
        if not a.islower():
            f = a
        else:
            # XXX to fix a bug in previous build-redir-shelf version
            mixed = a[0].upper() + a[1:]
            f = forward.get(mixed, a)
            if f == '':
                f = mixed
    if f is None:
        f = forward.get(a.lower())
        if f == '':
            f = a.lower()
    if f is not None:
        print("Forward", a, ",", f)
        print("Backward", f, backward.get(f, []))
        if f == a or f == a.lower():
            continue

        ff = forward.get(f)
        if ff == '':
            continue
        if ff is None:
            ff = forward.get(f.lower())
        if ff == '':
            continue
        if ff is not None:
            print("Second hop:")
            print(" Forward", f, ",", ff)
            print(" Backward", ff, backward.get(ff, []))
        continue

    b = backward.get(a)
    if b is None:
        b = backward.get(a.lower())
    if b is not None:
        print("Backward-only", a, ",", b)
