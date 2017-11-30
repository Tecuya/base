#!/usr/bin/env python

import math
from random import shuffle


class Dot:
    bank = 0
    parent = None
    choice = None

    def __init__(self, parent, choice, bank):
        self.choice = choice
        self.parent = parent
        self.bank = bank

    def choices(self):
        return filter(lambda x: x >= 2, range(int(math.floor(math.e + self.bank))))

    def produce_children(self):
        return [Dot(self, b, self.bank + math.e - b) for b in self.choices()]

    def __repr__(self):
        return str(self.choice)

    def history(self):
        h = [self.choice]

        p = self.parent
        while p is not None:
            h.append(p.choice)
            p = p.parent

        h.reverse()
        return h


def pl(pline):
    total_choices = sum((len(x.choices()) for x in pline))
    number_unique = len(set(x.bank for x in pline))
    print(len(pline), total_choices, total_choices / len(pline), number_unique)


lastline = [Dot(None, 2, math.e - 2)]

pl(lastline)

for i in range(12):
    newline = []
    for d in lastline:
        newline.extend( d.produce_children() )

    pl(newline)

    lastline = newline

def score_dot(dot):
    return dot.choice / math.log(dot.choice)
    return abs(dot.choice - math.e)

shuffle(lastline)

lowest_bank = 999
lowest_dot = None
for d in lastline:
    print 'test', d.bank, d.history()
    if d.bank <= lowest_bank:
        lowest_dot = d
        lowest_bank = d.bank
        print 'new/tie lowest bank', d.bank, d.history()

# lowest = 999
# highest = 0
# for d in lastline:

#     overall_diverge = score_dot(d)

#     p = d.parent
#     while p is not None:
#         overall_diverge += score_dot(p)
#         p = p.parent

#     if overall_diverge > highest:
#         highest = overall_diverge
#         highest_dot = d
#         print('new highest diverge', overall_diverge, highest, d.history(), d.bank)

#     if overall_diverge < lowest:
#         lowest = overall_diverge
#         print('new lowest diverge: ',overall_diverge,lowest,d.history(), d.bank)
#         lowest_dot = d

#     if overall_diverge == lowest:
#         print('tied lowest diverge: ',overall_diverge,lowest,d.history(), d.bank)

# print lowest_dot.history()
