#!/usr/bin/env python3

import numpy as np
import shap
import math
from scipy.special import comb


def shap_approximate(ddnnf, nsamples=1000, variables=None):
    idxs = [ddnnf._var2idx[var] for var in variables] if variables is not None else list(range(ddnnf.n_vars()))
    bkg = np.ones((1, ddnnf.n_vars()))
    bkg[:, idxs] = 0
    shap_explainer = shap.KernelExplainer(ddnnf.evaluate, bkg, link="identity")
    shap_values = shap_explainer.shap_values(np.ones(ddnnf.n_vars()), nsamples=nsamples)
    return {var: shap_values[i] for var, i in ddnnf._var2idx.items()}


def cnf_prior_shap_approximate(circuit_runtime, ddnnf, nsamples=1000):
    priors = cnf_prior_approximation(circuit_runtime, ddnnf)
    variables = [x[0] for x in sorted(priors.items(), key=lambda x: x[1])][-10:]
    return shap_approximate(ddnnf, nsamples=nsamples, variables=variables)


def monte_carlo_approximate(ddnnf, nsamples=1000, variables=None):
    variables = variables if variables is not None else list(ddnnf._var2idx.keys())
    n = ddnnf.n_vars()
    nsamples = math.ceil(nsamples / (2*len(variables)))
    values = {v: 0 for v in ddnnf._var2idx.keys()}
    for v in variables:
        i = ddnnf._var2idx[v]
        value = 0
        for _ in range(nsamples):
            p = np.random.permutation(np.arange(n))
            x = np.zeros(n)
            for j in range(n):
                if p[j] == i:
                    break
                else:
                    x[p[j]] = 1
            y1 = ddnnf.evaluate(x)
            x[i] = 1
            y2 = ddnnf.evaluate(x)
            value += y2 - y1
        values[v] = value / nsamples
    return values


def cnf_prior_monte_carlo_approximate(circuit_runtime, ddnnf, nsamples=1000):
    priors = cnf_prior_approximation(circuit_runtime, ddnnf)
    variables = [x[0] for x in sorted(priors.items(), key=lambda x: x[1])][-10:]
    return monte_carlo_approximate(ddnnf, nsamples=nsamples, variables=variables)


def cheats_monte_carlo_approximate(circuit_runtime, ddnnf, nsamples=1000):
    shapley_values = circuit_runtime["shapley_values"]
    variables = [int(x[0]) for x in sorted(shapley_values.items(), key=lambda x: x[1])][-10:]
    return monte_carlo_approximate(ddnnf, nsamples=nsamples, variables=variables)


def cnf_prior_approximation(circuit_runtime, ddnnf, nsamples=1000):
    cnf_fname = circuit_runtime['circuit_fname']
    vs = {}
    with open(cnf_fname, 'r') as f:
        c = f.readlines()
    for clause in c:
        if clause[0] != 'p':
            clause = clause.split()
            clause = [int(v) for v in clause if abs(int(v)) in ddnnf._var2idx]
            n_pos = 0
            n_neg = 0
            for v in clause:
                if v > 0:
                    n_pos += 1
                else:
                    n_neg += 1
            for v in clause:
                is_pos = v > 0
                v = abs(v)
                if v not in vs:
                    vs[v] = 0
                vs[v] += (1 if is_pos else -1)/(len(clause) * comb(len(clause)-1, n_neg if is_pos else n_neg-1))
    s = sum(vs.values())
    return {x[0]: x[1]/s for x in vs.items()}