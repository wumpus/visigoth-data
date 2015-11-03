#!/usr/bin/env python3

import shelve
from sys import argv

backward = shelve.open('redir_backward_shelf', flag='r')
forward = shelve.open('redir_forward_shelf', flag='r')

argv = argv[1:]
for a in argv:
    f = forward.get(a.lower())
    if f is not None:
        print("Forward", a, ",", f)
        print("Backward", f, backward.get(f.lower(), []))

        ff = forward.get(f.lower())
        if ff is not None:
            print("Forward", f, ",", ff)
            print("Backward", ff, backward.get(ff.lower(), []))
            for bb in backward.get(ff.lower(), []):
                print("BackBackward", bb, backward.get(bb.lower(), []))

    b = backward.get(a.lower())
    if b is not None:
        print("Backward", a, ",", b)
