#!/usr/bin/env python3

import re
import math

x = math.e - 2

s = ''

last = 0
c=0
for i in range(0,200000):

    if math.floor(i*x) == math.floor(last):
        s += '*'
        c = 0
    else:
        s += ' '
        c += 1

    last = i*x


regex = re.compile(r'(.+ .+)( \1)+')
match = regex.search(s)
from IPython import embed; embed(banner1='Reg')
