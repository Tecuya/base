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

    # ## stopping this after changing write logic so that [0.5, 0.5] -> [0.0, 0.0]
    # #
    # def adjusted_cost(self):
    #     # for base n, glyph probability x
    #     # if x=1/n then adjusted cost is 0 (no discrimination between states)
    #     # if x=n/n then adjusted sum is 1 (perfect discrimination between states)
    #     def glyphcost(x):
    #         noisefloor = self.noisefloor

    #         if x - self.noisefloor < 0:
    #             return 0.

    #         return (x - self.noisefloor) / (1 - self.noisefloor)

    #     return sum(glyphcost(x) for x in self.staters)

    def adjusted_stater_cost(self):
        # stater [0, 0], sum staters is 0, so should we say there is
        # no cost to this?  then how could it be that [0, 0, 0] is
        # less accurate than [0, 0] if they both put 0 effort in to
        # storing information?

        # another way is to say [0, 0] costs 1, [0, 0, 0] costs 1
        # and [1, 1] costs 2 and [1, 1, 1] costs 3

        return sum(map(lambda x: x + ((1 - x) * self.noisefloor), self.staters))

    def expectedadjdigitaccuracy(self):
        return sum(self.staters)/self.numstaters

    def expecteddigitaccuracy(self):
        a = self.expectedadjdigitaccuracy()
        return (a + ((1 - a)/self.numstaters))

    # def expectedscore(self, objective):
    #     return self.expecteddigitaccuracy() / (sum(self.staters) * len(objective.objective_states(self.numstaters)))

        # compressed version of expected score
        #
        # ss = sum(self.staters)
        # b = self.numstaters
        # return (
        #     (ss/b + ((1 - ss/b) / b))
        #     /
        #     (
        #         ss * math.ceil(math.log(objective.objective)/math.log(b))
        #     )
        # )

    def __str__(self):
        return str.format(
            'Staters: {} sum={} avg={} expdigacc={} expadjdigacc={}',
            self.staters,
            sum(self.staters), sum(self.staters)/float(self.numstaters),
            self.expecteddigitaccuracy(),
            self.expectedadjdigitaccuracy())


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
        # return sum(self.digitconfig.staters) * len(self.digits)
        return self.digitconfig.adjusted_stater_cost() * len(self.digits)

    def score(self):
        return self.adjdigitaccuracy() / self.cost()
        # return self.digitaccuracy() / self.cost()

    def expectedscore(self):
        # return (self.digitconfig.expectedadjdigitaccuracy() /
        #         (sum(self.digitconfig.staters) * len(self.objective.objective_states(self.digitconfig.numstaters))))

        return (self.digitconfig.expectedadjdigitaccuracy() /
                (self.digitconfig.adjusted_stater_cost() * len(self.objective.objective_states(self.digitconfig.numstaters))))
        
    def __str__(self):
        return str.format(
            'StoredObjective: Staters: {}, Digit Value: {}, Digit Truth: {}, Obj: {} => {}, EndAcc: {}, DigAcc: {}, AdjDigAcc: {}, Cost: {}, Score: {}, ExpScore: {}',
            self.digitconfig.staters,
            ''.join(list('x' if d.value == -1 else str(d.value) for d in self.digits)),
            ''.join(list(str(d.truevalue) for d in self.digits)),
            self.objective.objective,
            self.read(),
            self.endianaccuracy(),
            self.digitaccuracy(),
            self.adjdigitaccuracy(),
            self.cost(),
            self.score(),
            self.expectedscore())


class Objective(object):

    def __init__(self, objective):
        self.objective = objective

    @classmethod
    def from_random(cls, minobjective, maxobjective):
        return cls(util.rand_int_between(minobjective, maxobjective))

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

        stats = {'digitaccuracy': [lambda so: so.digitaccuracy(), 0.],
                 'adjdigitaccuracy': [lambda so: so.adjdigitaccuracy(), 0.],
                 'endianaccuracy': [lambda so: so.endianaccuracy(), 0.],
                 'expectedscore': [lambda so: so.expectedscore(), 0.],
                 'score': [lambda so: so.score(), 0.],
                 'cost': [lambda so: so.cost(), 0.],
                 'digits': [lambda so: len(so.digits), 0.]}

        for t in range(self.numtrials):

            s = StoredObjective(self.digitconfig)
            s.store(Objective.from_random(self.minobjective, self.maxobjective))

            if self.printobj:
                print(s)

            for key,stat in stats.items():
                stat[1] += stat[0](s)

        self.results = dict((k, v[1]/self.numtrials) for k, v in stats.items())

    def __str__(self):
        return str(self.results)


class Generation(object):

    numtrials = 1000

    def __init__(self, members):
        self.members = members

    def run(self):

        od = collections.OrderedDict()

        for m in self.members:
            t = Trial(m, numtrials)
            t.trial()
            od[t.avgscore] = m


def output(d, t):
    print(d, "\n", t, "\n")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--minstaters', dest='minstaters', action='store', type=int, default=2)
    parser.add_argument('--maxstaters', dest='maxstaters', action='store', type=int, default=7)
    parser.add_argument('--minobjective', dest='minobjective', action='store', type=int, default=2**32)
    parser.add_argument('--maxobjective', dest='maxobjective', action='store', type=int, default=2**31)
    parser.add_argument('--numtrials', dest='numtrials', action='store', type=int, default=750)
    parser.add_argument('--printobj', dest='printobj', action='store_true', default=False)

    subparsers = parser.add_subparsers(help='available commands', dest='command')

    sample_parser = subparsers.add_parser('presets', help='run the presets')
    randomtrials_parser = subparsers.add_parser('randomtrials', help='run random trials')
    rainbow_parser = subparsers.add_parser('rainbow', help='run rainbow')

    randomtrials_parser.add_argument('--hsretrialmult', dest='hsretrialmult', action='store', type=int, default=2, help='high score retrials')
    rainbow_parser.add_argument('--divisions', dest='divisions', action='store', type=int, default=10)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()

    elif args.command == 'presets':
        print('PRESETS')

        for s in ([.3, .3, .3],
                  [.4, .4, .4],
                  [.45, .45],
                  [.3, .3]):
        # for s in ([1., 1.],
        #           [1/2., 1/2.],
        #           [1., 1., 1.],
        #           [.8, .8, .8],
        #           [1/3., 1/3., 1/3.],
        #           [math.e/3, math.e/3, math.e/3],
        #           [math.e/4, math.e/4, math.e/4, math.e/4],
        #           [math.e/5, math.e/5, math.e/5, math.e/5, math.e/5],
        #           [.01, .01, .01]):

            d = DigitConfig()
            d.set_staters(s)
            t = Trial(d, args.numtrials, args.minobjective, args.maxobjective, args.printobj)
            t.trial()
            output(d, t)

    elif args.command == 'randomtrials':

        print('TRIALS')
        high_score = 0
        while True:
            d = DigitConfig()
            d.random_staters(args.minstaters, args.maxstaters)
            t = Trial(d, args.numtrials, args.minobjective, args.maxobjective, args.printobj)
            t.trial()

            if t.results['score'] > high_score:
                high_score = t.results['score']
                output(d, t)

    elif args.command == 'rainbow':

        print('RAINBOW')

        high_score = 0
        divisions = args.divisions

        for x in range(divisions):
            print('>>> x =', float(x+1)/divisions)
            for y in range(divisions):
                for z in range(divisions):

                    d = DigitConfig()
                    d.set_staters([float(x+1) / divisions, float(y+1) / divisions, float(z+1) / divisions])

                    t = Trial(d, args.numtrials, args.minobjective, args.maxobjective, args.printobj)
                    t.trial()

                    if t.results['score'] > high_score:
                        high_score = t.results['score']
                        output(d, t)
