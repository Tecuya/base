#!/usr/bin/env python3

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

    def random_staters(self, minstaters, maxstaters):
        numstaters = int(util.rand_int_between(minstaters, maxstaters))
        minprob = 1. / numstaters

        self.set_staters(list(util.rand_float_between(minprob, 1.) for i in range(numstaters)))

    def set_staters(self, staters):
        self.numstaters = len(staters)
        self.staters = staters

    def adjusted_cost(self):
        # for base n, glyph probability x
        # if x=1/n then adjusted cost is 0 (no discrimination between states)
        # if x=n/n then adjusted sum is 1 (perfect discrimination between states)
        def glyphcost(x):
            noisefloor = (1/self.numstaters)

            if x - noisefloor < 0:
                return 0.

            return (x - noisefloor) / (1 - noisefloor)

        return sum(glyphcost(x) for x in self.staters)


class Digit(object):

    def __init__(self, digitconfig):
        self.digitconfig = digitconfig
        self.value = None
        self.truevalue = None

    def write(self, value):
        self.truevalue = value

        if util.rand_float() < self.digitconfig.staters[value]:
            self.value = value
        else:
            # this is where we could encode alternate states based on their p weights
            self.value = -1

    def accurate(self):
        return self.value == self.truevalue


class StoredObjective(object):

    def __init__(self, digitconfig):
        self.digitconfig = digitconfig

    def store(self, objective):
        self.digits = []
        for k in objective.objective_states(self.digitconfig.numstaters):
            d = Digit(self.digitconfig)
            d.write(k)
            self.digits.append(d)

    def __str__(self):
        return str.format(
            'Staters: {}, Digit Value: {}, Digit Truth: {}, Accuracy: {}, Cost: {}, Score: {}',
            self.digitconfig.staters,
            ''.join(list('x' if d.value == -1 else str(d.value) for d in self.digits)),
            ''.join(list(str(d.truevalue) for d in self.digits)),
            self.accuracy(),
            self.cost(),
            self.score())

    def accuracy(self):
        a = sum( 1 if d.accurate() else 0 for d in self.digits )
        accuracy_percentage = float(a) / len(self.digits)
        return accuracy_percentage

    def cost(self):
        return self.digitconfig.adjusted_cost() * len(self.digits)

    def score(self):
        return self.accuracy() / self.cost()


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

    def __init__(self, digitconfig, numtrials, minobjective, maxobjective, print_stored_objectives):
        self.digitconfig = digitconfig
        self.numtrials = numtrials
        self.minobjective = minobjective
        self.maxobjective = maxobjective
        self.print_stored_objectives = print_stored_objectives

    def trial(self):
        cumaccuracy = 0.
        cumscore = 0.
        cumcost = 0.

        for t in range(self.numtrials):

            s = StoredObjective(self.digitconfig)
            s.store(Objective(self.minobjective, self.maxobjective))

            if self.print_stored_objectives:
                print(s)

            cumaccuracy += s.accuracy()
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
    parser.add_argument('--print_stored_objectives', dest='print_stored_objectives', action='store_true', default=False)

    subparsers = parser.add_subparsers(help='available commands', dest='command')

    sample_parser = subparsers.add_parser('samples', help='run the samples')
    randomtrials_parser = subparsers.add_parser('randomtrials', help='run random trials')

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()

    elif args.command == 'samples':
        print('SAMPLES')

        d = DigitConfig()
        d.set_staters([1.0, 1.0])

        t = Trial(d, args.numtrials, args.minobjective, args.maxobjective, args.print_stored_objectives)
        t.trial()
        t.print_results_string()

        d = DigitConfig()
        d.set_staters([1.0, 1.0, 1.0])

        t = Trial(d, args.numtrials, args.minobjective, args.maxobjective, args.print_stored_objectives)
        t.trial()
        t.print_results_string()

    elif args.command == 'randomtrials':

        print('TRIALS')
        high_score = 0
        while True:
            d = DigitConfig()
            d.random_staters(args.minstaters, args.maxstaters)
            t = Trial(d, args.numtrials, args.minobjective, args.maxobjective, args.print_stored_objectives)
            t.trial()

            if t.avgscore > high_score:
                high_score = t.avgscore
                t.print_results_string()
