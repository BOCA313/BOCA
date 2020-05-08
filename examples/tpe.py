import os, sys
import time
import copy
import random
import numpy as np
from hyperopt import fmin, tpe, hp, space_eval, rand, Trials, partial, STATUS_OK

random.seed(123)
iters = 180
begin2end = 5
cmd2 = ''
cmd3 = ''
cmd4 = ''
cmd5 = ''

options = ['-fno-peephole2', '-ffast-math', '-fno-schedule-insns2', '-fno-caller-saves', '-funroll-all-loops', '-fno-inline-small-functions', '-finline-functions', '-fno-math-errno', '-fno-tree-pre', '-ftracer', '-fno-reorder-functions', '-fno-dce', '-fipa-cp-clone', '-fno-move-loop-invariants', '-fno-regmove', '-funsafe-math-optimizations', '-fno-tree-loop-optimize', '-fno-merge-constants', '-fno-omit-frame-pointer', '-fno-align-labels', '-fno-tree-ter', '-fno-tree-dse', '-fwrapv', '-fgcse-after-reload', '-fno-align-jumps', '-fno-asynchronous-unwind-tables', '-fno-cse-follow-jumps', '-fno-ivopts', '-fno-guess-branch-probability', '-fprefetch-loop-arrays', '-fno-tree-coalesce-vars', '-fno-common', '-fpredictive-commoning', '-fno-unit-at-a-time', '-fno-cprop-registers', '-fira-coalesce', '-fno-early-inlining', '-fno-delete-null-pointer-checks', '-fselective-scheduling2', '-fno-gcse', '-fno-inline-functions-called-once', '-funswitch-loops', '-fno-tree-vrp', '-fno-tree-dce', '-fno-jump-tables', '-ftree-vectorize', '-fno-argument-alias', '-fno-schedule-insns', '-fno-branch-count-reg', '-fno-tree-switch-conversion', '-fno-auto-inc-dec', '-fno-crossjumping', '-fno-tree-fre', '-fno-tree-reassoc', '-fno-align-functions', '-fno-defer-pop', '-fno-optimize-register-move', '-fno-strict-aliasing', '-fno-rerun-cse-after-loop', '-fno-tree-ccp', '-fno-ipa-cp', '-fno-if-conversion2', '-fno-tree-sra', '-fno-expensive-optimizations', '-fno-tree-copyrename', '-fno-ipa-reference', '-fno-ipa-pure-const', '-fno-thread-jumps', '-fno-if-conversion', '-fno-reorder-blocks', '-falign-loops']

def generate_opts(independent):
    result = []
    for k, s in enumerate(independent):
        if s == 1:
            result.append(options[k])
    independent = result

    return independent

process = []
ts = []
b = 0

def get_objective_score(independent):
    opt = ''
    for option in options:
        if independent[option] == 1:
            opt = opt + ' '+ option

    speedups = []
    step = 0
    while (len(speedups) < 6):
        step += 1
        if step > 10:
            print('failed configuration!')
            os.exit(0)
        os.system(cmd4)
        print(cmd2)
        os.system(cmd2)
        begin = time.time()
        ret = os.system(cmd5)
        if ret != 0:
            continue
        end = time.time()
        de = end - begin
        os.system(cmd4)
        os.system(cmd3)
        begin = time.time()
        os.system(cmd5)
        end = time.time()
        nu = end - begin

        print('nu:' + str(nu) + ' de:' + str(de) + ' val:' + str(nu / de))
        speedups.append(nu / de)

    print(speedups)
    process.append(-np.median(speedups))
    ts.append(time.time() - b)
    return -np.median(speedups)

if __name__ == '__main__':
    space = {}
    stats = []
    times = []
    for option in options:
        space[option] = hp.choice(option, [0, 1])

    algo = partial(tpe.suggest, n_startup_jobs=1)
    for i in range(begin2end):
        process = []
        ts = []
        b = time.time()
        best = fmin(get_objective_score, space, algo=algo, max_evals=iters)
        stats.append(process)
        times.append(ts)
        print(best)
        print(get_objective_score(best))
        print(process)

    vals = []
    for j, v_tmp in enumerate(stats):
        max_s = 0
        for i, v in enumerate(v_tmp):
            max_s = min(max_s, v)
            v_tmp[i] = max_s
    print(times)
    print(stats)

    for i in range(iters):
        tmp = []
        for j in range(begin2end):
            tmp.append(times[j][i])
        vals.append(-np.mean(tmp))

    print(vals) 

    vals = []
    for i in range(iters):
        tmp = []
        for j in range(begin2end):
            tmp.append(stats[j][i])
        vals.append(-np.mean(tmp))

    print(vals)

    vals = []
    for i in range(iters):
        tmp = []
        for j in range(begin2end):
            tmp.append(stats[j][i])
        vals.append(-np.std(tmp))

    print(vals)
