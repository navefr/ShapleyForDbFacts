from math import factorial as factoricalm
from scipy.special import comb as combs


class CombCache:
    __instance = None
    _fact_cache = {}
    _comb_cache = {}

    @staticmethod
    def getInstance():
        if CombCache.__instance == None:
            CombCache()
        return CombCache.__instance

    def __init__(self):
        if CombCache.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            CombCache.__instance = self

    def factorial(self, k):
        if k in CombCache._fact_cache:
            return CombCache._fact_cache[k]
        elif k - 1 in CombCache._fact_cache:
            ans = CombCache._fact_cache[k - 1] * k
        else:
            ans = factoricalm(k)
        CombCache._fact_cache[k] = ans
        return ans

    def comb(self, N, k):
        key = (N, k)
        if key in CombCache._comb_cache:
            return CombCache._comb_cache[key]
        ans = combs(N, k)
        CombCache._comb_cache[key] = ans
        return ans