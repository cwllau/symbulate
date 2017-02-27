from .distributions import Exponential
from .math import inf
from .random_processes import RandomProcess, TimeIndex

class PoissonProcess(RandomProcess):

    def __init__(self, rate):
        self.rate = rate
        self.probSpace = Exponential(rate=rate) ** inf
        self.timeIndex = TimeIndex(fs=inf)
        def fun(x, t):
            n = 0
            total_time = 0
            while True:
                total_time += x[n]
                if total_time > t:
                    break
                else:
                    n += 1
            return n
        self.fun = fun
