import os, sys
import time
import copy
import random
import numpy as np

iters = 180
begin2end = 5

random.seed(123)
 
cmd0 = 'clang -O0 -emit-llvm -I ../polybench/utilities -I ../polybench/datamining/correlation/correlation -c ../polybench/utilities/polybench.c -o polybench.bc; clang -O0 -emit-llvm -I ../polybench/utilities -I ../polybench/datamining/correlation/correlation -c ../polybench/datamining/correlation/correlation.c -o correlation.bc;'   
cmd1 = ' -S correlation.bc -o correlation.opt.bc; llc -O2 -filetype=obj correlation.opt.bc -o correlation.o'
cmd2 = ' -S polybench.bc -o polybench.opt.bc; llc -O2 -filetype=obj polybench.opt.bc -o polybench.o'
cmd3 = 'clang -O0 -lm *.o'
cmd4 = 'rm -rf *bc *.o *.I *.S a.out'
cmd5 = 'time ./a.out'

#options = ['-fno-peephole2', '-ffast-math', '-fno-schedule-insns2', '-fno-caller-saves', '-funroll-all-loops', '-fno-inline-small-functions', '-finline-functions', '-fno-math-errno', '-fno-tree-pre', '-ftracer', '-fno-reorder-functions', '-fno-dce', '-fipa-cp-clone', '-fno-move-loop-invariants', '-fno-regmove', '-funsafe-math-optimizations', '-fno-tree-loop-optimize', '-fno-merge-constants', '-fno-omit-frame-pointer', '-fno-align-labels', '-fno-tree-ter', '-fno-tree-dse', '-fwrapv', '-fgcse-after-reload', '-fno-align-jumps', '-fno-asynchronous-unwind-tables', '-fno-cse-follow-jumps', '-fno-ivopts', '-fno-guess-branch-probability', '-fprefetch-loop-arrays', '-fno-tree-coalesce-vars', '-fno-common', '-fpredictive-commoning', '-fno-unit-at-a-time', '-fno-cprop-registers', '-fira-coalesce', '-fno-early-inlining', '-fno-delete-null-pointer-checks', '-fselective-scheduling2', '-fno-gcse', '-fno-inline-functions-called-once', '-funswitch-loops', '-fno-tree-vrp', '-fno-tree-dce', '-fno-jump-tables', '-ftree-vectorize', '-fno-argument-alias', '-fno-schedule-insns', '-fno-branch-count-reg', '-fno-tree-switch-conversion', '-fno-auto-inc-dec', '-fno-crossjumping', '-fno-tree-fre', '-fno-tree-reassoc', '-fno-align-functions', '-fno-defer-pop', '-fno-optimize-register-move', '-fno-strict-aliasing', '-fno-rerun-cse-after-loop', '-fno-tree-ccp', '-fno-ipa-cp', '-fno-if-conversion2', '-fno-tree-sra', '-fno-expensive-optimizations', '-fno-tree-copyrename', '-fno-ipa-reference', '-fno-ipa-pure-const', '-fno-thread-jumps', '-fno-if-conversion', '-fno-reorder-blocks', '-falign-loops']

options = ['-targetlibinfo ',
'-no-aa ',
'-tbaa ',
'-basicaa ',
'-globalopt',
'-ipsccp ',
'-deadargelim ',
'-instcombine ',
#'-simplifycfg ',
'-basiccg ',
'-prune-eh ',
'-inline ',
'-functionattrs ',
'-argpromotion',
'-scalarrepl-ssa ',
'-domtree ',
'-early-cse ',
'-simplify-libcalls ',
'-lazy-value-info ',
'-jump-threading ',
'-correlated-propagation ',
'-simplifycfg ',
'-instcombine ',
'-tailcallelim ',
'-simplifycfg ',
'-reassociate ',
'-domtree ',
'-loops ',
'-loop-simplify ',
'-lcssa ',
'-loop-rotate ',
#'-licm ',
'-lcssa ',
'-loop-unswitch ',
'-instcombine ',
'-scalar-evolution ',
'-loop-simplify ',
'-lcssa ',
'-iv-users ',
'-indvars',
'-loop-idiom ',
'-loop-deletion ',
'-loop-unroll ',
'-instcombine ',
'-memdep ',
'-gvn ',
'-memdep ',
'-memcpyopt ',
'-sccp ',
'-instcombine ',
'-lazy-value-info ',
'-jump-threading ',
'-correlated-propagation ',
'-domtree ',
'-memdep ',
'-dse ',
'-adce ',
'-simplifycfg ',
'-strip-dead-prototypes ',
'-print-used-types ',
'-deadtypeelim ',
'-globaldce',
'-constmerge ',
'-preverify ',
'-domtree ',
'-verify']
def generate_opts(independent):
    result = []
    for k, s in enumerate(independent):
        if s == 1:
            result.append(options[k])
    independent = result

    return independent

def get_objective_score(independent):
    independent = generate_opts(independent)
    
    speedups = []
    step = 0
    while (len(speedups) < 6):
        step += 1
        if step > 10:
            print('failed configuration!')
            sys.exit(0)
        os.system(cmd4)
        print(cmd0)
        os.system(cmd0)
        print('opt ' + ' '.join(independent) + cmd1)
        os.system('opt ' + ' '.join(independent) + cmd1)
        print('opt ' + ' '.join(independent) + cmd2)
        os.system('opt ' + ' '.join(independent) + cmd2)
        print(cmd3)
        os.system(cmd3)
        begin = time.time()
        ret = os.system(cmd5)
        if ret > 0:
            continue
        end = time.time()
        de = end - begin
        os.system(cmd4)
        print(cmd0)                                                                                                             
        os.system(cmd0)       
        print('opt ' + ' -O3 ' + cmd1)
        os.system('opt ' + ' -O3 ' + cmd1)
        print('opt ' + ' -O3 ' + cmd2)
        os.system('opt ' + ' -O3 ' + cmd2)
        print(cmd3)
        os.system(cmd3)
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
        x = random.randint(0, 2 ** len(options))
        if x not in training_indep:
            training_indep.append(x)
            comb = bin(x).replace('0b', '')
            comb = '0' * (len(options) - len(comb)) + comb
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
