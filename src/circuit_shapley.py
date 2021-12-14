#!/usr/bin/env python3

import pandas as pd
from ddnnf import dDNNF
from ddnnf import VARGATE, NEGGATE, ORGATE, ANDGATE, TRUECONST, FALSECONST
from collections import deque
from comb_cache import CombCache

OTHERVAR = -1

def factorial(k):
    return CombCache.getInstance().factorial(k)

def comb(N, k):
    return CombCache.getInstance().comb(N, k)


class CircuitShapley:

    def __init__(self, circuit_filepath, forget_filepath=None):
        self._ddnnf = dDNNF(circuit_filepath, forget_filepath)

    # compute alphas and betas
    def __alphas_and_betas__(self):
        varsets = {}  # varsets[i] is the set of variables that have a path to gate i
        alphas = {}  # alphas[x][i] are the #SAT(f_+x,k) values of the gates
        betas = {}  # betas[x][i] are the #SAT(f_-x,k) values
        
        ddnnf = self._ddnnf

        for var in ddnnf._varset:  # initialization
            alphas[var] = {}
            betas[var] = {}
        alphas[OTHERVAR] = {}
        betas[OTHERVAR] = {}

        for gate in ddnnf._topsort:
            if ddnnf._gateTypes[gate] == VARGATE:
                varsets[gate] = {ddnnf._variables[gate]}
                alphas[ddnnf._variables[gate]][gate] = [1]
                betas[ddnnf._variables[gate]][gate] = [0]
                alphas[OTHERVAR][gate] = [0, 1]
                betas[OTHERVAR][gate] = [0, 1]
            elif ddnnf._gateTypes[gate] == TRUECONST:
                varsets[gate] = set()
                alphas[OTHERVAR][gate] = [1]
                betas[OTHERVAR][gate] = [1]
            elif ddnnf._gateTypes[gate] == FALSECONST:
                varsets[gate] = set()
                alphas[OTHERVAR][gate] = [0]
                betas[OTHERVAR][gate] = [0]
            elif ddnnf._gateTypes[gate] == ANDGATE:  # it has exactly two inputs
                in_gate1 = ddnnf._children[gate][0]
                in_gate2 = ddnnf._children[gate][1]
                gate_varsets = varsets[in_gate1].union(varsets[in_gate2])
                varsets[gate] = gate_varsets
                in_gate1_varsets = varsets[in_gate1]
                in_gate2_varsets = varsets[in_gate2]
                for var in gate_varsets:
                    s1 = len(in_gate1_varsets) - (1 if var in in_gate1_varsets else 0)
                    s2 = len(in_gate2_varsets) - (1 if var in in_gate2_varsets else 0)
                    s = s1 + s2  # (because the AND gate is decomposable)
                    cur_alphas = [0] * (s + 1)   # initialization
                    cur_betas = [0] * (s + 1)   # initialization
                    in_gate1_var = var if in_gate1 in alphas[var] else OTHERVAR
                    in_gate1_alphas = alphas[in_gate1_var][in_gate1]
                    in_gate1_betas = betas[in_gate1_var][in_gate1]
                    in_gate2_var = var if in_gate2 in alphas[var] else OTHERVAR
                    in_gate2_alphas = alphas[in_gate2_var][in_gate2]
                    in_gate2_betas = betas[in_gate2_var][in_gate2]
                    for i in range(s1 + 1):
                        for j in range(s2 + 1):
                            cur_alphas[i + j] += in_gate1_alphas[i] * in_gate2_alphas[j]
                            cur_betas[i + j] += in_gate1_betas[i] * in_gate2_betas[j]
                    alphas[var][gate] = cur_alphas
                    betas[var][gate] = cur_betas
                if len(gate_varsets) < len(ddnnf._varset):  # Handle OTHERVAR (and)
                    s1 = len(in_gate1_varsets)
                    s2 = len(in_gate2_varsets)
                    s = s1 + s2  # (because the AND gate is decomposable)
                    cur_alphas = [0] * (s + 1)  # initialization
                    cur_betas = [0] * (s + 1)  # initialization
                    in_gate1_alphas = alphas[OTHERVAR][in_gate1]
                    in_gate1_betas = betas[OTHERVAR][in_gate1]
                    in_gate2_alphas = alphas[OTHERVAR][in_gate2]
                    in_gate2_betas = betas[OTHERVAR][in_gate2]
                    for i in range(s1 + 1):
                        for j in range(s2 + 1):
                            cur_alphas[i + j] += in_gate1_alphas[i] * in_gate2_alphas[j]
                            cur_betas[i + j] += in_gate1_betas[i] * in_gate2_betas[j]
                    alphas[OTHERVAR][gate] = cur_alphas
                    betas[OTHERVAR][gate] = cur_betas
            elif ddnnf._gateTypes[gate] == ORGATE:  # again, it has exactly two inputs
                in_gate1 = ddnnf._children[gate][0]
                in_gate2 = ddnnf._children[gate][1]
                gate_varsets = varsets[in_gate1].union(varsets[in_gate2])
                varsets[gate] = gate_varsets
                in_gate1_varsets = varsets[in_gate1]
                in_gate2_varsets = varsets[in_gate2]
                s1_diff = len(in_gate2_varsets.difference(in_gate1_varsets))
                s2_diff = len(varsets[in_gate1].difference(varsets[in_gate2]))
                for var in gate_varsets:
                    s1 = s1_diff - (1 if var in in_gate2_varsets and var not in in_gate1_varsets else 0)
                    s2 = s2_diff - (1 if var in in_gate1_varsets and var not in in_gate2_varsets else 0)
                    s = len(gate_varsets) - (1 if var in gate_varsets else 0)
                    cur_alphas = [0] * (s + 1)   # initialization
                    cur_betas = [0] * (s + 1)   # initialization
                    in_gate1_var = var if in_gate1 in alphas[var] else OTHERVAR
                    in_gate1_alphas = alphas[in_gate1_var][in_gate1]
                    in_gate1_betas = betas[in_gate1_var][in_gate1]
                    in_gate2_var = var if in_gate2 in alphas[var] else OTHERVAR
                    in_gate2_alphas = alphas[in_gate2_var][in_gate2]
                    in_gate2_betas = betas[in_gate2_var][in_gate2]
                    for i in range(s - s1 + 1):
                        for j in range(s1 + 1):
                            cur_alphas[i + j] += in_gate1_alphas[i] * comb(s1, j)
                            cur_betas[i + j] += in_gate1_betas[i] * comb(s1, j)
                    for i in range(s - s2 + 1):
                        for j in range(s2 + 1):
                            cur_alphas[i + j] += in_gate2_alphas[i] * comb(s2, j)
                            cur_betas[i + j] += in_gate2_betas[i] * comb(s2, j)
                    alphas[var][gate] = cur_alphas
                    betas[var][gate] = cur_betas
                if len(gate_varsets) < len(ddnnf._varset):  # Handle OTHERVAR (or)
                    s1 = s1_diff
                    s2 = s2_diff
                    s = len(gate_varsets)
                    cur_alphas = [0] * (s + 1)  # initialization
                    cur_betas = [0] * (s + 1)  # initialization
                    in_gate1_alphas = alphas[OTHERVAR][in_gate1]
                    in_gate1_betas = betas[OTHERVAR][in_gate1]
                    in_gate2_alphas = alphas[OTHERVAR][in_gate2]
                    in_gate2_betas = betas[OTHERVAR][in_gate2]
                    for i in range(s - s1 + 1):
                        for j in range(s1 + 1):
                            cur_alphas[i + j] += in_gate1_alphas[i] * comb(s1, j)
                            cur_betas[i + j] += in_gate1_betas[i] * comb(s1, j)
                    for i in range(s - s2 + 1):
                        for j in range(s2 + 1):
                            cur_alphas[i + j] += in_gate2_alphas[i] * comb(s2, j)
                            cur_betas[i + j] += in_gate2_betas[i] * comb(s2, j)
                    alphas[OTHERVAR][gate] = cur_alphas
                    betas[OTHERVAR][gate] = cur_betas
            elif ddnnf._gateTypes[gate] == NEGGATE:  # has exactly one input
                in_gate1 = ddnnf._children[gate][0]
                gate_varsets = varsets[in_gate1]
                varsets[gate] = gate_varsets
                s = len(gate_varsets) - 1  # 0?
                for var in gate_varsets:
                    cur_alphas = [0] * (s + 1)  # initialization
                    cur_betas = [0] * (s + 1)  # initialization
                    in_gate1_alphas = alphas[var][in_gate1]
                    in_gate1_betas = betas[var][in_gate1]
                    for i in range(s + 1):
                        cur_alphas[i] = comb(s, i) - in_gate1_alphas[i]
                        cur_betas[i] = comb(s, i) - in_gate1_betas[i]
                    alphas[var][gate] = cur_alphas
                    betas[var][gate] = cur_betas
                if len(gate_varsets) < len(ddnnf._varset):  # Handle OTHERVAR (neg)
                    s += 1
                    # s = len(varsets[gate])  # 1?
                    cur_alphas = [0] * (s + 1)  # initialization
                    cur_betas = [0] * (s + 1)  # initialization
                    in_gate1_alphas = alphas[OTHERVAR][in_gate1]
                    in_gate1_betas = betas[OTHERVAR][in_gate1]
                    for i in range(s + 1):
                        cur_alphas[i] = comb(s, i) - in_gate1_alphas[i]
                        cur_betas[i] = comb(s, i) - in_gate1_betas[i]
                    alphas[OTHERVAR][gate] = cur_alphas
                    betas[OTHERVAR][gate] = cur_betas
        return alphas, betas

    # compute the Shapley values
    def shapley_values(self):
        alphas, betas = self.__alphas_and_betas__()

        shapley_values = {}
        s = len(self._ddnnf._varset)
        for var in self._ddnnf._varset:
            output_alphas = alphas[var][self._ddnnf._outputGate]
            output_betas = betas[var][self._ddnnf._outputGate]
            value = 0
            for k in range(s):
                value += (factorial(k) * factorial(s - k - 1)) * (output_alphas[k] - output_betas[k])
            shapley_values[var] = value / factorial(s)

        return shapley_values