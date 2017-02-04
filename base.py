#!/usr/bin/env python3

# note:
# cost needs to be calculated differently .. or we need to store differently.. something..


import sys
import random
import math
import time
import argparse
import collections

import util


class DigitConfig(object):

    def __init__(self):
        self.staters = []

    def get_rand_stater_perc(self, minprob):
        # 10% get ones
        p = util.rand_float_between(0, 1.1)
        return p if p < 1 else 1.

    def random_staters(self, minstaters, maxstaters):
        numstaters = int(util.rand_int_between(minstaters, maxstaters))
        minprob = 1. / numstaters

        self.set_staters(list(self.get_rand_stater_perc(minprob) for i in range(numstaters)))

    def set_staters(self, staters):
        self.numstaters = len(staters)
        self.noisefloor = 1/self.numstaters
        self.staters = staters

    def adjusted_cost(self):
        # for base n, glyph probability x
        # if x=1/n then adjusted cost is 0 (no discrimination between states)
        # if x=n/n then adjusted sum is 1 (perfect discrimination between states)
        def glyphcost(x):
            noisefloor = self.noisefloor

            if x - self.noisefloor < 0:
                return 0.

            return (x - self.noisefloor) / (1 - self.noisefloor)

        return sum(glyphcost(x) for x in self.staters)


class Digit(object):

    def __init__(self, digitconfig):
        self.digitconfig = digitconfig
        self.value = None
        self.truevalue = None

    def write(self, value):

        self.truevalue = value

        # copy of the staters we can manipulate
        statercopy = self.digitconfig.staters[:]

        target_prob = self.digitconfig.noisefloor + (statercopy[value] * (1 - self.digitconfig.noisefloor))
        # target_prob = statercopy[value]

        statercopy[value] = 0

        if util.rand_float() < target_prob:
            self.value = value

        else:

            # it missed.  pick amongst the remaining staters in a
            # weighted fashion

            # rand between 0 and the remnants of statercopy
            r = util.rand_float_between(0, sum(statercopy))

            for i in range(len(statercopy)):

                r -= statercopy[i]

                if r <= 0:
                    self.value = i
                    break

    def accurate(self):
        return self.value == self.truevalue


class StoredObjective(object):

    def __init__(self, digitconfig):
        self.digitconfig = digitconfig

    def store(self, objective):
        self.objective = objective
        self.digits = []
        for k in objective.objective_states(self.digitconfig.numstaters):
            d = Digit(self.digitconfig)
            d.write(k)
            self.digits.append(d)

    def read(self):
        n = 0
        for i in range(len(self.digits)):
            n += self.digits[i].value * (self.digitconfig.numstaters ** (len(self.digits)-i-1))
        return n

    def digitaccuracy(self):
        # accuracy of each of the digits
        a = sum( 1 if d.accurate() else 0 for d in self.digits )
        accuracy_percentage = float(a) / len(self.digits)
        return accuracy_percentage

    def adjdigitaccuracy(self):
        # accuracy of each digit, adjusted to remove the noise floor weighting
        return (self.digitaccuracy() - self.digitconfig.noisefloor) / (1 - self.digitconfig.noisefloor)

    def endianaccuracy(self):
        # accuracy of actual stored objective integer vs objective
        return (self.objective.objective - abs(self.objective.objective - self.read())) / self.objective.objective

    def cost(self):
        # return self.digitconfig.adjusted_cost() * len(self.digits)
        return sum(self.digitconfig.staters) * len(self.digits)

    def score(self):
        return self.adjdigitaccuracy() / self.cost()
        # return self.digitaccuracy() / self.cost()

    def __str__(self):
        return str.format(
            'Staters: {}, Digit Value: {}, Digit Truth: {}, Obj: {} => {}, EndAcc: {}, DigAcc: {}, AdjDigAcc: {}, AdjCost: {}, Cost: {}, Score: {}',
            self.digitconfig.staters,
            ''.join(list('x' if d.value == -1 else str(d.value) for d in self.digits)),
            ''.join(list(str(d.truevalue) for d in self.digits)),
            self.objective.objective,
            self.read(),
            self.endianaccuracy(),
            self.digitaccuracy(),
            self.adjdigitaccuracy(),
            self.digitconfig.adjusted_cost(),
            self.cost(),
            self.score())


class Objective(object):

    def __init__(self, minobjective, maxobjective):
        self.objective = util.rand_int_between(minobjective, maxobjective)

    def objective_states(self, base):
        numdigits = int(math.ceil(math.log(self.objective) / math.log(base)))

        states = []
        eatobj = self.objective
        for i in reversed(range(numdigits)):
            piece = math.floor(eatobj / base ** i)
            eatobj -= piece * (base ** i)
            states.append(piece)

        return states


class Trial(object):

    def __init__(self, digitconfig, numtrials, minobjective, maxobjective, printobj):
        self.digitconfig = digitconfig
        self.numtrials = numtrials
        self.minobjective = minobjective
        self.maxobjective = maxobjective
        self.printobj = printobj

    def trial(self):
        cumaccuracy = 0.
        cumscore = 0.
        cumcost = 0.

        for t in range(self.numtrials):

            s = StoredObjective(self.digitconfig)
            s.store(Objective(self.minobjective, self.maxobjective))

            if self.printobj:
                print(s)

            cumaccuracy += s.adjdigitaccuracy()
            cumcost += s.cost()
            cumscore += s.score()

        self.avgaccuracy = cumaccuracy / float(self.numtrials)
        self.avgscore = cumscore / float(self.numtrials)
        self.avgcost = cumcost / float(self.numtrials)

    def print_results_string(self):
        print(util.time_since_start(),
              ' | S:', self.avgscore,
              ' A:', self.avgaccuracy,
              ' C:', self.avgcost,
              ' Staters:', self.digitconfig.staters,
              ' SumStaters:', sum(self.digitconfig.staters),
              ' AdjCost:', self.digitconfig.adjusted_cost(), sep='')


class Generation(object):

    numtrials=1000

    def __init__(self, members):
        self.members = members

    def run(self):

        od = collections.OrderedDict()

        for m in self.members:
            t = Trial(m, numtrials)
            t.trial()
            od[t.avgscore] = m


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--minstaters', dest='minstaters', action='store', type=int, default=2)
    parser.add_argument('--maxstaters', dest='maxstaters', action='store', type=int, default=7)
    parser.add_argument('--minobjective', dest='minobjective', action='store', type=int, default=2**32)
    parser.add_argument('--maxobjective', dest='maxobjective', action='store', type=int, default=2**31)
    parser.add_argument('--numtrials', dest='numtrials', action='store', type=int, default=2000)
    parser.add_argument('--printobj', dest='printobj', action='store_true', default=False)

    subparsers = parser.add_subparsers(help='available commands', dest='command')

    sample_parser = subparsers.add_parser('presets', help='run the presets')
    randomtrials_parser = subparsers.add_parser('randomtrials', help='run random trials')
    spread_parser = subparsers.add_parser('spread', help='run spread')

    randomtrials_parser.add_argument('--hsretrialmult', dest='hsretrialmult', action='store', type=int, default=10, help='high score retrials')
    spread_parser.add_argument('--divisions', dest='divisions', action='store', type=int, default=100)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()

    elif args.command == 'presets':
        print('PRESETS')

        for s in ([1., 1.],
                  [1/2., 1/2.],
                  [1., 1., 1.],
                  [1/3., 1/3., 1/3.],
                  [math.e/3, math.e/3, math.e/3],
                  [math.e/4, math.e/4, math.e/4, math.e/4],
                  [math.e/5, math.e/5, math.e/5, math.e/5, math.e/5],
                  [1., 1., math.e - 2],

                  [0.038473495673535085, 0.0989485964205993],
                  [0.9717208949301608, 0.335328812802043, 1.0]):

            d = DigitConfig()
            d.set_staters(s)
            t = Trial(d, args.numtrials, args.minobjective, args.maxobjective, args.printobj)
            t.trial()
            t.print_results_string()

    elif args.command == 'randomtrials':

        print('TRIALS')
        high_score = 0
        while True:
            d = DigitConfig()
            d.random_staters(args.minstaters, args.maxstaters)
            t = Trial(d, args.numtrials, args.minobjective, args.maxobjective, args.printobj)
            t.trial()

            if t.avgscore > high_score:
                high_score = t.avgscore
                t.print_results_string()

    elif args.command == 'spread':

        print('SPREAD')

        high_score = 0
        divisions = args.divisions

        for x in range(divisions):
            print('>>> x =', x/float(divisions))
            for y in range(divisions):
                for z in range(divisions):
                    d = DigitConfig()
                    d.set_staters([float(x+1) / divisions, float(y+1) / divisions, float(z+1) / divisions])

                    t = Trial(d, args.numtrials, args.minobjective, args.maxobjective, args.printobj)
                    t.trial()
                    if t.avgscore > high_score:

                        t = Trial(d, args.numtrials*args.hsretrialmult, args.minobjective, args.maxobjective, args.printobj)
                        t.trial()
                        if t.avgscore > high_score:

                            high_score = t.avgscore
                            t.print_results_string()
