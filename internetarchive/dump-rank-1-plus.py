#!/usr/bin/env python3

import shelve
import os

metadata = shelve.open(os.environ.get('VISIGOTH_DATA','.') + '/metadata_shelf', flag='r')

for ia_id in metadata:
    if metadata[ia_id].get('rank',0) == 1:
        print(ia_id)

