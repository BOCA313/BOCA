import os, sys
import random
import math
import numpy as np
import numpy as np
import time
random.seed(123)
initial_set = 4
begin2end = 5
iters = 30

cmd1 = ' -o a.out -lm *.o'
cmd2 = ' -c *.c'
cmd3 = 'gcc -O2 -funswitch-loops -ftree-vectorize -fpredictive-commoning -fipa-cp-clone -finline-functions -fgcse-after-reload -c *.c; gcc -O2 -funswitch-loops -ftree-vectorize -fpredictive-commoning -fipa-cp-clone -finline-functions -fgcse-after-reload -o a.out -lm *.o'
cmd4 = 'rm -rf *.o *.S *.I a.out'
cmd5 = './__run 1'
path = '/BOCA/cbench/automotive_bitcount'


options = ['-fno-peephole2', '-ffast-math', '-fno-schedule-insns2', '-fno-caller-saves', '-funroll-all-loops', '-fno-inline-small-functions', '-finline-functions', '-fno-math-errno', '-fno-tree-pre', '-ftracer', '-fno-reorder-functions', '-fno-dce', '-fipa-cp-clone', '-fno-move-loop-invariants', '-fno-regmove', '-funsafe-math-optimizations', '-fno-tree-loop-optimize', '-fno-merge-constants', '-fno-omit-frame-pointer', '-fno-align-labels', '-fno-tree-ter', '-fno-tree-dse', '-fwrapv', '-fgcse-after-reload', '-fno-align-jumps', '-fno-asynchronous-unwind-tables', '-fno-cse-follow-jumps', '-fno-ivopts', '-fno-guess-branch-probability', '-fprefetch-loop-arrays', '-fno-tree-coalesce-vars', '-fno-common', '-fpredictive-commoning', '-fno-unit-at-a-time', '-fno-cprop-registers', '-fira-coalesce', '-fno-early-inlining', '-fno-delete-null-pointer-checks', '-fselective-scheduling2', '-fno-gcse', '-fno-inline-functions-called-once', '-funswitch-loops', '-fno-tree-vrp', '-fno-tree-dce', '-fno-jump-tables', '-ftree-vectorize', '-fno-argument-alias', '-fno-schedule-insns', '-fno-branch-count-reg', '-fno-tree-switch-conversion', '-fno-auto-inc-dec', '-fno-crossjumping', '-fno-tree-fre', '-fno-tree-reassoc', '-fno-align-functions', '-fno-defer-pop', '-fno-optimize-register-move', '-fno-strict-aliasing', '-fno-rerun-cse-after-loop', '-fno-tree-ccp', '-fno-ipa-cp', '-fno-if-conversion2', '-fno-tree-sra', '-fno-expensive-optimizations', '-fno-tree-copyrename', '-fno-ipa-reference', '-fno-ipa-pure-const', '-fno-thread-jumps', '-fno-if-conversion', '-fno-reorder-blocks', '-falign-loops']

def generate_opts(independent):
    result = []
    for k, s in enumerate(independent):
        if s == 1:
            result.append(options[k])
    independent = result

    return independent

def generate_conf(x):
    comb = bin(x).replace('0b', '')
    comb = '0' * (len(options) - len(comb)) + comb
    conf = []
    for k, s in enumerate(comb):
        if s == '1':
            conf.append(1)
        else:
            conf.append(0)
    return conf

def get_objective_score(independent):
    independent = generate_opts(independent)
   
    speedups = []
    step = 0
    while (len(speedups) < 6):
        step += 1
        if step > 10:
            print('failed configuration!')
            sys.exit(0)
        os.chdir(path)
        os.system(cmd4)
        print('gcc -O2 ' + ' '.join(independent) + cmd2)
        os.system('gcc -O2 ' + ' '.join(independent) + cmd2)
        print('gcc -O2 ' + ' '.join(independent) + cmd1)
        os.system('gcc -O2 ' + ' '.join(independent) + cmd1)
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
    return -np.median(speedups)

class GA:
    def __init__(self):
        geneinfo = []
        for i in range(initial_set):
            x = random.randint(0, 2 ** len(options))
            geneinfo.append(generate_conf(x))
        fitness = []
        self.begin = time.time()
        self.dep = []
        self.times = []
        for x in geneinfo:
            tmp = get_objective_score(x)
            fitness.append(-1.0 / tmp)
            
        self.pop = [(x, fitness[i]) for i, x in enumerate(geneinfo)]
        self.pop = sorted(self.pop, key=lambda x:x[1])
        self.best = self.selectBest(self.pop)
        self.dep.append(1.0/self.best[1])
        self.times.append(time.time() - self.begin)
        
    def selectBest(self, pop):
        return pop[0]
        
    def selection(self, inds, k):
        s_inds = sorted(inds, key=lambda x:x[1])
        return s_inds[:int(k)]

    def crossoperate(self, offspring):
        dim = len(options)
        geninfo1 = offspring[0][0]
        geninfo2 = offspring[1][0]
        pos = random.randrange(1, dim)

        newoff = []
        for i in range(dim):
            if i>=pos:
                newoff.append(geninfo2[i])
            else:
                newoff.append(geninfo1[i])
        return newoff

    def mutation(self, crossoff):
        dim = len(options)
        pos = random.randrange(1, dim)
        crossoff[pos] = 1 - crossoff[pos]
        return crossoff

    def GA_main(self):
        for g in range(iters):
            selectpop = self.selection(self.pop, 0.5 * initial_set)
             
            nextoff = []
            while len(nextoff) != initial_set:
                offspring = [random.choice(selectpop) for i in range(2)]
                crossoff = self.crossoperate(offspring)
                muteoff = self.mutation(crossoff)
                fit_muteoff = get_objective_score(muteoff)
                nextoff.append((muteoff, -1.0 / fit_muteoff))
            self.pop = nextoff       
            self.pop = sorted(self.pop, key=lambda x:x[1])
            self.best = self.selectBest(self.pop)
            self.times.append(time.time() - self.begin)
            self.dep.append(1.0/self.best[1])

        return self.dep, self.times

if __name__ == '__main__':
    stats = []
    times = []

    for i in range(begin2end):
        run = GA()
        dep, ts = run.GA_main()
        print('middle result')
        print(dep)
        stats.append(dep)
        times.append(ts)

    vals = []
    for j, v_tmp in enumerate(stats):
        max_s = 0
        for i, v in enumerate(v_tmp):
            max_s = max(max_s, v)
            v_tmp[i] = max_s

    print(times)
    print(stats)

    for i in range(iters):
        tmp = []
        for j in range(begin2end):
            tmp.append(times[j][i])
        vals.append(np.mean(tmp))

    print(vals)

    vals = []
    for i in range(iters):
        tmp = []
        for j in range(begin2end):
            tmp.append(stats[j][i])
        vals.append(np.mean(tmp))

    print(vals)

    vals = []
    for i in range(iters):
        tmp = []
        for j in range(begin2end):
            tmp.append(stats[j][i])
        vals.append(np.std(tmp))

    print(vals)
