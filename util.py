import math
import random
import time

time_start = time.time()
def time_since_start():
    return time.time() - time_start

def rand_int_between(nmin, nmax):
    return math.floor(random.random() * (nmax+1 - nmin)) + nmin

def rand_float_between(nmin, nmax):
    return nmin + (random.random() * (nmax-nmin))

def rand_float():
    return random.random()

def float_to_longlong(f):
    return struct.unpack("<q",struct.pack("<d", f))[0]

def longlong_to_float(l):
    return struct.unpack("<d",struct.pack("<q", l))[0]
