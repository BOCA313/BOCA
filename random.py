import os, sys
import time
import copy
import random
import numpy as np

iters = 180
begin2end = 5

random.seed(123)

def generate_opts(independent):
    options = ['-fno-peephole2', '-ffast-math', '-fno-schedule-insns2', '-fno-caller-saves', '-funroll-all-loops', '-fno-inline-small-functions', '-finline-functions', '-fno-math-errno', '-fno-tree-pre', '-ftracer', '-fno-reorder-functions', '-fno-dce', '-fipa-cp-clone', '-fno-move-loop-invariants', '-fno-regmove', '-funsafe-math-optimizations', '-fno-tree-loop-optimize', '-fno-merge-constants', '-fno-omit-frame-pointer', '-fno-align-labels', '-fno-tree-ter', '-fno-tree-dse', '-fwrapv', '-fgcse-after-reload', '-fno-align-jumps', '-fno-asynchronous-unwind-tables', '-fno-cse-follow-jumps', '-fno-ivopts', '-fno-guess-branch-probability', '-fprefetch-loop-arrays', '-fno-tree-coalesce-vars', '-fno-common', '-fpredictive-commoning', '-fno-unit-at-a-time', '-fno-cprop-registers', '-fira-coalesce', '-fno-early-inlining', '-fno-delete-null-pointer-checks', '-fselective-scheduling2', '-fno-gcse', '-fno-inline-functions-called-once', '-funswitch-loops', '-fno-tree-vrp', '-fno-tree-dce', '-fno-jump-tables', '-ftree-vectorize', '-fno-argument-alias', '-fno-schedule-insns', '-fno-branch-count-reg', '-fno-tree-switch-conversion', '-fno-auto-inc-dec', '-fno-crossjumping', '-fno-tree-fre', '-fno-tree-reassoc', '-fno-align-functions', '-fno-defer-pop', '-fno-optimize-register-move', '-fno-strict-aliasing', '-fno-rerun-cse-after-loop', '-fno-tree-ccp', '-fno-ipa-cp', '-fno-if-conversion2', '-fno-tree-sra', '-fno-expensive-optimizations', '-fno-tree-copyrename', '-fno-ipa-reference', '-fno-ipa-pure-const', '-fno-thread-jumps', '-fno-if-conversion', '-fno-reorder-blocks', '-falign-loops']

    result = []
    for k, s in enumerate(independent):
        if s == 1:
            result.append(options[k])
    independent = result

    return independent

def get_objective_score(independent):
    independent = generate_opts(independent)
    cmd2 = ###compile a program with configuration 'independent'###'gcc -O2 ' + ' '.join(independent) + ' -I utilities -I linear-algebra/kernels/2mm utilities/polybench.c linear-algebra/kernels/2mm/2mm.c -lm -DPOLYBENCH_TIME -o 2mm_time'
    cmd5 = ###execute the program###'./2mm_time'
    speedups = []
    while (len(speedups) < 6):
        print(cmd2)
        os.system(cmd2)
        begin = time.time()
        os.system(cmd5)
        end = time.time()
        de = end - begin
        ###compile a program with -O3 optimization level###os.system('gcc -O2 -funswitch-loops -ftree-vectorize -fpredictive-commoning -fipa-cp-clone -finline-functions -fgcse-after-reload -I utilities -I linear-algebra/kernels/2mm utilities/polybench.c linear-algebra/kernels/2mm/2mm.c -lm -DPOLYBENCH_TIME -o 2mm_time')
        begin = time.time()
        os.system(cmd5)
        end = time.time()
        nu = end - begin

        print('nu:' + str(nu) + ' de:' + str(de) + ' val:' + str(nu / de))
        speedups.append(nu / de)

    print(speedups)
    return -np.median(speedups)

def main():
    training_indep = []
    indep = []
    dep = []
    ts = []
    b = time.time()
    while len(training_indep) < iters:
        x = random.randint(0, 2 ** 71)
        if x not in training_indep:
            training_indep.append(x)
            comb = bin(x).replace('0b', '')
            comb = '0' * (71 - len(comb)) + comb
            conf = []
            for k, s in enumerate(comb):
                if s == '1':
                    conf.append(1)
                else:
                    conf.append(0)
            indep.append(conf)
            dep.append(get_objective_score(conf))
            ts.append(time.time() - b)
    print('time:' + str(time.time() - b))
    objectives = [[x, dep[i]] for i, x in enumerate(indep)]

    return [x[1] for x in objectives], ts

if __name__ == '__main__':
    stats = []
    times = []

    for i in range(begin2end): 
        dep, ts = main()
        stats.append(dep)
        times.append(ts)

    vals = [] 
    for j, v_tmp in enumerate(stats):
        max_s = 0
        for i, v in enumerate(v_tmp):
            max_s = min(max_s, v)
            v_tmp[i] = max_s

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
