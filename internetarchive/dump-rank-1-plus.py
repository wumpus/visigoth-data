#!/usr/bin/env python3

import shelve

metadata = shelve.open('metadata_shelf', flag='r')

for ia_id in metadata:
    if metadata[ia_id].get('rank',0) > 0:
        print(ia_id)

