#!/usr/bin/env python3

import sys
import random
import math
import time


def rand_int_between(nmin, nmax):
    return math.floor(random.random() * (nmax+1 - nmin)) + nmin

def rand_float_between(nmin, nmax):
    return nmin + (random.random() * (nmax-nmin))

time_start = time.time()
def time_since_start():
    return time.time() - time_start


class Radix:

    glyphs_min = 2
    glyphs_max = 7

    glyph_r_max = 1.3

    target_min = 2**62
    target_max = 2**63

    trial_cycles = 5000

    def initialize_random_base(self):
        base = int(rand_int_between(self.glyphs_min, self.glyphs_max))

        self.glyphs = list(reversed(sorted(rand_float_between(1./base, self.glyph_r_max) for i in range(base))))

        self.glyphs = [ 1. if x > 1. else x for x in self.glyphs ]

        self.initialize_glyphs()

    def initialize_glyphs(self):
        self.base = len(self.glyphs)
        self.glyph_sum = sum(self.glyphs)

    def store(self, number):
        self.states = []
        self.stateactual = []
        self.digits = int(math.ceil(math.log(number) / math.log(self.base)))

        eatnumber = number
        self.datas = []
        for i in reversed(range(self.digits)):
            piece = math.floor(eatnumber / self.base ** i)
            eatnumber -= piece * (self.base ** i)
            self.write_glyph(piece)

    def write_glyph(self, state):
        assert(state <= self.base)

        p = self.glyphs[state]

        g1 = random.random()
        if g1 < p:
            f = state

        else:

            f = -1
            # v = random.random()

            # # write fail - so pick a rand number, then walk through the
            # # weights subtracting from the number until we hit 0.  this
            # # should give all weights relatively weighted chance of hitting.
            # done = False
            # while not done:
            #     for i in range(self.base):

            #         w = self.weights[i]
            #         v -= w
            #         if v <= 0:
            #             f = i
            #             done = True
            #             break

        self.states.append(f)
        self.stateactual.append(state)

    def decode(self):
        n = 0
        for i in range(len(self.states)):
            n += self.states[i] * (self.base ** (len(self.states)-i-1))
        return n

    def accuracy_percent(self):
        inaccuracy = 0
        for i in range(len(self.states)):
            if self.states[i] != self.stateactual[i]:
                inaccuracy += 1

        maxinaccuracy = self.digits

        accuracy_p = (maxinaccuracy - inaccuracy) / float(maxinaccuracy)
        return accuracy_p - (1/self.base) # subtract noise floor

    def adjusted_glyph_cost(self):
        # for base n, glyph probability x, if x=1/n then adjusted sum
        # is 0 (no information contained within) if x=n/n then
        # adjusted sum is 1
        def glyphcost(x):
            noisefloor = (1/self.base)

            if x - noisefloor < 0:
                return 0.

            return (x - noisefloor) / (1 - noisefloor)

        return sum(glyphcost(x) for x in self.glyphs)

    def score(self):
#        return self.accuracy_percent() / (sum(self.glyphs) * len(self.states))
        return self.accuracy_percent() / (self.adjusted_glyph_cost() * len(self.states))

    def trial(self):
        cumscore = 0.0
        cumaccuracy = 0.0
        for trial in range(self.trial_cycles):
            target = rand_int_between(self.target_min, self.target_max)
            r.store(target)
            cumscore += r.score()
            cumaccuracy += r.accuracy_percent()

        self.trialscore = cumscore / self.trial_cycles
        self.trialaccuracy = cumaccuracy / self.trial_cycles
        return self.trialscore

    def print_trial_results(self):
        print(time_since_start(),'TS',self.trialscore,'G',self.glyphs,
              'GC',sum(self.glyphs),'AGC',self.adjusted_glyph_cost(),'TA',self.trialaccuracy)


high_score = 0

print('SAMPLES')
r = Radix()

r.glyphs = [1.0, 1.0]
r.initialize_glyphs()
r.trial()
r.print_trial_results()

r.glyphs = [1.0, 1.0, 1.0]
r.initialize_glyphs()
r.trial()
r.print_trial_results()

for i in range(7):
    if i < 3:
        continue
    r.glyphs = [math.e/i for b in range(i)]
    r.initialize_glyphs()
    r.trial()
    r.print_trial_results()

print('TRIALS')
while True:
    r = Radix()
    r.initialize_random_base()
    tscore = r.trial()
    if tscore > high_score:
        high_score = tscore
        r.print_trial_results()
