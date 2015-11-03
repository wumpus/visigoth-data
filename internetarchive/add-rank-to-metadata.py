#!/usr/bin/env python3

import shelve
import os

metadata = shelve.open('metadata_shelf', flag='w', writeback=True)
stats = {}
stats['rank_zero'] = 0
stats['rank_nonzero'] = 0

for ia_id in metadata:
    rank = 0
    raw_rank = metadata[ia_id].get('raw_rank')

    if raw_rank is None:
        stats['rank_zero'] += 1
        metadata[ia_id]['rank'] = 0
        continue

    if int(raw_rank.get('wiki_isbn_rank',0)) > 0:
        if raw_rank['wiki_isbn_rank'] > 1:
            rank += 3
        else:
            rank += 2

    if raw_rank.get('academic_press'):
        rank += 4

    raw_pulprank = int(metadata[ia_id]['raw_rank'].get('pulp_rank', 0))
    if raw_pulprank == 0:
        pulprank = 0
    elif raw_pulprank > 500000:
        pulprank = 1
    elif raw_pulprank > 100000:
        pulprank = 2
    else:
        pulprank = 3
        rank += 1

    if rank > 0:
        stats['rank_nonzero'] += 1

    metadata[ia_id]['rank'] = rank

#    print("raw pulprank", raw_pulprank, "results in pulprank of", pulprank)

    stat = 'rank ' + str(rank) + ' + pulp ' + str(pulprank)
    stats[stat] = stats.get(stat,0) + 1

metadata.close()

print("stats are", stats)
