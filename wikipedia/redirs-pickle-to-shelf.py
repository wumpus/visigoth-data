#!/usr/bin/env python3

import pickle
import shelve

print("reading pickle")
f = open("redirs_pickle", "rb")
redirs = pickle.load(f)
print("done")

forward = redirs['forward']
backward = redirs['backward']

print("writing forward shelf")
with shelve.open('redir_forward_shelf', flag='n', writeback=True) as s:
    for k in forward:
        s[k] = forward[k]
print("done")

print("writing backward shelf")
with shelve.open('redir_backward_shelf', flag='n', writeback=True) as s:
    for k in backward:
        s[k] = backward[k]
print("done")
