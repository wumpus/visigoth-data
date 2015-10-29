#!/usr/bin/env python

import fileinput
import sys
import re

for line in fileinput.input(sys.argv[1:]):
    print re.sub('^.*?{', '{', line.rstrip())
