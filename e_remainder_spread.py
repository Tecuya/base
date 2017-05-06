#!/usr/bin/env python3

import time
import re
import math
import sys

x = math.e - 2

s = ''

last = 0
c=0
for i in range(0,200000):

    if math.floor(i*x) == math.floor(last):
        print('|', end='')
        s += '*'
        c = 0
    else:
        print(' ', end='')
        s += ' '
        c += 1

    sys.stdout.flush()
    last = i*x
    time.sleep(0.000005)

