#!/usr/bin/env python3

import numpy as np
import pandas as pd
from collections import deque

VARGATE = 1
NEGGATE = 2
ORGATE = 3
ANDGATE = 4
TRUECONST = 5
FALSECONST = 6

class dDNNF:

    def __init__(self, circuit_filepath, forget_filepath=None):

        self._forget_vars = set()
        if forget_filepath is not None:
            forget_df = pd.read_csv(forget_filepath, delimiter=' ', header=None)
            self._forget_vars = set(forget_df[0].unique())

        self.__read_nnf__(circuit_filepath)
        self.__topsort__()
        vars = list(set([self._variables[gate] for gate in self._variables if self._gateTypes[gate]==VARGATE]))
        self._var2idx = {v: i for i, v in enumerate(vars)}

    # nnf format described here http://reasoning.cs.ucla.edu/c2d/download.php. We make the circuit binary at the same time
    def __read_nnf__(self, filepath):
        file = open(filepath)
        self._children = {}  # children[i] is a list containing the children of gate i (size 0 or 1 or 2 since I assume my circuits to be binary and I have explicit constant gates)
        self._gateTypes = {}  # gateType[i] is the type of gate i
        self._variables = {}  # when gateType[i] is VARGATE, variables[i] is the variable that this gate holds
        self._outputGate = -1

        currentGate = 0
        for line in file:
            parsed = [x.strip() for x in line.split(' ')]
            if parsed[0] == 'nnf':
                nbgates = int(parsed[1])
                additionalGate = nbgates  # Used to make the nnf binary and also to represent negative literals as negation gates of a variable gate
                self._outputGate = nbgates - 1
            elif parsed[0] == 'L':
                if abs(int(parsed[1])) in self._forget_vars:  # a literal we wish to forget
                    self._gateTypes[currentGate] = TRUECONST
                    self._children[currentGate] = []
                else:
                    if int(parsed[1]) > 0:  # a positive literal
                        self._variables[currentGate] = int(parsed[1])
                        self._gateTypes[currentGate] = VARGATE
                        self._children[currentGate] = []
                    elif int(parsed[1]) < 0:  # a negative literal. We create an additional variable gate and create a neggate for the negative literal
                        self._variables[additionalGate] = - int(parsed[1])
                        self._gateTypes[additionalGate] = VARGATE
                        self._children[additionalGate] = []
                        self._gateTypes[currentGate] = NEGGATE
                        self._children[currentGate] = [additionalGate]
                        additionalGate += 1
                currentGate += 1
            elif parsed[0] == 'A':
                if int(parsed[1]) == 0:  # this is a constant 1-gate
                    self._gateTypes[currentGate] = TRUECONST
                    self._children[currentGate] = []
                elif int(parsed[1]) == 1:  # only one input gate. we create an additional constant true gate to make it binary (this will simplify the code later)
                    self._gateTypes[currentGate] = ANDGATE
                    self._gateTypes[additionalGate] = TRUECONST
                    self._children[currentGate] = [int(parsed[2]), additionalGate]
                    self._children[additionalGate] = []
                    additionalGate += 1
                elif int(parsed[1]) == 2:  # two input gates
                    self._gateTypes[currentGate] = ANDGATE
                    self._children[currentGate] = [int(parsed[2]), int(parsed[3])]
                else:  # strictly more than 2 input gates, we binarize
                    self._gateTypes[currentGate] = ANDGATE
                    self._children[currentGate] = [int(parsed[2])]
                    self._gateTypes[additionalGate] = ANDGATE
                    self._children[currentGate].append(additionalGate)
                    i = 1
                    while i <= int(parsed[1]) - 3:
                        self._children[additionalGate] = [int(parsed[2 + i])]
                        self._gateTypes[additionalGate + 1] = ANDGATE
                        self._children[additionalGate].append(additionalGate + 1)
                        additionalGate += 1
                        i += 1
                    self._children[additionalGate] = [int(parsed[2 + i]), int(parsed[3 + i])]
                    additionalGate += 1
                currentGate += 1
            elif parsed[0] == 'O':
                if int(parsed[2]) == 0:  # this is a constant 0-gate
                    self._gateTypes[currentGate] = FALSECONST
                    self._children[currentGate] = []
                elif int(parsed[2]) == 1:  # only one input gate. we create an additional constant false gate to make it binary (this will simplify the code later)
                    self._gateTypes[currentGate] = ORGATE
                    self._gateTypes[additionalGate] = FALSECONST
                    self._children[currentGate] = [int(parsed[3]), additionalGate]
                    self._children[additionalGate] = []
                    additionalGate += 1
                elif int(parsed[2]) == 2:  # two input gates
                    self._gateTypes[currentGate] = ORGATE
                    self._children[currentGate] = [int(parsed[3]), int(parsed[4])]
                else:  # strictly more than 2 input gates, we binarize
                    self._gateTypes[currentGate] = ORGATE
                    self._children[currentGate] = [int(parsed[3])]
                    self._gateTypes[additionalGate] = ORGATE
                    self._children[currentGate].append(additionalGate)
                    i = 1
                    while i <= int(parsed[2]) - 3:
                        self._children[additionalGate] = [int(parsed[3 + i])]
                        self._gateTypes[additionalGate + 1] = ORGATE
                        self._children[additionalGate].append(additionalGate + 1)
                        additionalGate += 1
                        i += 1
                    self._children[additionalGate] = [int(parsed[3 + i]), int(parsed[4 + i])]
                    additionalGate += 1
                currentGate += 1

    def n_vars(self):
        return len(self._var2idx)

    def to_dot(self):
        ret = "digraph{\n"
        for gate in self._children.keys():
            if self._gateTypes[gate] == VARGATE: lab = str(self._variables[gate])
            if self._gateTypes[gate] == NEGGATE: lab = "NOT"
            if self._gateTypes[gate] == ANDGATE: lab = "AND"
            if self._gateTypes[gate] == ORGATE: lab = "OR"
            if self._gateTypes[gate] == TRUECONST: lab = "TRUE"
            if self._gateTypes[gate] == FALSECONST: lab = "FALSE"
            ret += "id" + str(gate) + " [ label=\"" + str(gate) + ": " + lab + " \"];\n"
        for gate, neighs in self._children.items():
            for child in neighs:
                ret += "id" + str(gate) + " -> id" + str(child) + ";\n"
        ret += "}"
        return ret

    # topological sort of the circuit, and compute the variables that have a path to the output gate
    def __topsort__(self):
        self._topsort = deque([])
        marked = set()
        self._varset = set()  # the input variables that have a path to the output gate (note that there can be less than the number of variables reported by the "nnf" line, which itself can be less than the number of variables in the original CNF formula)

        def visit(gate):
            if gate in marked:
                return
            marked.add(gate)
            if self._gateTypes[gate] == VARGATE:
                self._varset.add(self._variables[gate])
            for child in self._children[gate]:
                visit(child)
            self._topsort.append(gate)

        visit(self._outputGate)

    def evaluate(self, X):
        X = np.array(X)
        if len(X.shape) == 1:
            return self._evaluate_1d(X)
        elif len(X.shape) == 2:
            return np.array([self._evaluate_1d(x) for x in X])
        else:
            raise Exception("X shape is %s. Expect to get 1 or 2 dimensional arrays" % str(X.shape))

    def _evaluate_1d(self, x):
        gate_value = {}

        for gate in self._topsort:
            if self._gateTypes[gate] == VARGATE:
                gate_value[gate] = x[self._var2idx[self._variables[gate]]] > 0
            elif self._gateTypes[gate] == TRUECONST:
                gate_value[gate] = True
            elif self._gateTypes[gate] == FALSECONST:
                gate_value[gate] = False
            elif self._gateTypes[gate] == ANDGATE:  # it has exactly two inputs
                in_gate1 = self._children[gate][0]
                in_gate2 = self._children[gate][1]
                gate_value[gate] = gate_value[in_gate1] and gate_value[in_gate2]
            elif self._gateTypes[gate] == ORGATE:  # again, it has exactly two inputs
                in_gate1 = self._children[gate][0]
                in_gate2 = self._children[gate][1]
                gate_value[gate] = gate_value[in_gate1] or gate_value[in_gate2]
            elif self._gateTypes[gate] == NEGGATE:  # has exactly one input
                in_gate1 = self._children[gate][0]
                gate_value[gate] = not gate_value[in_gate1]
        return int(gate_value[self._outputGate])
