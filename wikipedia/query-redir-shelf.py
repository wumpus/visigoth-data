#!/usr/bin/env python3

import shelve
from sys import argv
import os

backward = shelve.open(os.environ.get('VISIGOTH_DATA','.')+'/redir_backward_shelf', flag='r')
forward = shelve.open(os.environ.get('VISIGOTH_DATA','.')+'/redir_forward_shelf', flag='r')

argv = argv[1:]
for a in argv:
    f = forward.get(a) or forward.get(a.lower())
    if f is not None:
        print("Forward", a, ",", f)
        print("Backward", f, backward.get(f, []) or backward.get(f.lower(), []))

        ff = forward.get(f) or forward.get(f.lower())
        if ff is not None:
            print("Forward", f, ",", ff)
            print("Backward", ff, backward.get(ff, []) or backward.get(ff.lower(), []))
            for bb in backward.get(ff.lower(), []):
                print("BackBackward", bb, backward.get(bb.lower(), []))
        continue

    b = backward.get(a) or backward.get(a.lower())
    if b is not None:
        print("Backward-only", a, ",", b)
