#!/usr/bin/env python3

import time
import re
import math
import sys



acc = 0

class Game(object):

    def play(self):
        turn = 0
        balance = 0

        disk = []

        while True:

            turn += 1

            balance += math.e

            while True:
                sel = input('Turn {} Balance {}  -- 2/3/a/p? '.format(turn, balance))

                if sel in ('2','3'):

                    isel = int(sel)

                    if balance >= isel:
                        s = int(input('Choose a state 1 to {}: '.format(isel)))
                        if(s >= 1 and s <= isel):
                            balance -= isel
                            disk.append((turn, isel, s))
                            break

                elif(sel == 'p'):
                    for d in disk:
                        print(d)


if __name__ == "__main__":
    g = Game()
    g.play()


# Turn 13 Balance 4.337663769967585  -- 2/3/a/p? p
# (1, 2, 2)
# (2, 2, 2)   long term memory
# (3, 2, 2)
# (4, 3, 2)
# (5, 3, 3)
# (6, 3, 3)
# (7, 3, 3)
# (8, 3, 3)
# (9, 3, 3)
# (10, 3, 3)
# (11, 2, 2)
# (12, 2, 1)  short term memory


# **the memory must form the ability to decide answers**
#
# it should copy itself, generate a cycle which follows maximum effective growth,
# and thereby re-express e


### useful to calculate at what points we dont have enough digits of
### e.. after so many turns it becomes relevant to the decision
### tree.  we can get some generator that spits out digits and then
### use it as-needed or something
