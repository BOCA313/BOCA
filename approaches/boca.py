import os, sys
import time
import random
import numpy as np
import copy
from sklearn.ensemble import AdaBoostRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.ensemble import RandomForestRegressor
from scipy.stats import norm
import math
random.seed(456)
iters = 60
begin2end = 5
md = int(os.environ.get('MODEL', 1))
fnum = int(os.environ.get('FNUM', 8))
decay = float(os.environ.get('DECAY', 0.5))
scale = float(os.environ.get('SCALE', 10))
offset = float(os.environ.get('OFFSET', 20))

cmd2 = ' -I ../polybench/utilities -I ../polybench/linear-algebra/kernels/2mm ../polybench/utilities/polybench.c ../polybench/linear-algebra/kernels/2mm/2mm.c -lm -DPOLYBENCH_TIME -o 2mm_time'
cmd3 = 'gcc -O2 -funswitch-loops -ftree-vectorize -fpredictive-commoning -fipa-cp-clone -finline-functions -fgcse-after-reload -I ../polybench/utilities -I ../polybench/linear-algebra/kernels/2mm ../polybench/utilities/polybench.c ../polybench/linear-algebra/kernels/2mm/2mm.c -lm -DPOLYBENCH_TIME -o 2mm_time'
cmd4 = 'rm -rf *.o *.I *.s a.out'
cmd5 = './2mm_time'
                                                                   
options = ['-fno-peephole2', '-ffast-math', '-fno-schedule-insns2', '-fno-caller-saves', '-funroll-all-loops', '-fno-inline-small-functions', '-finline-functions', '-fno-math-errno', '-fno-tree-pre', '-ftracer', '-fno-reorder-functions', '-fno-dce', '-fipa-cp-clone', '-fno-move-loop-invariants', '-fno-regmove', '-funsafe-math-optimizations', '-fno-tree-loop-optimize', '-fno-merge-constants', '-fno-omit-frame-pointer', '-fno-align-labels', '-fno-tree-ter', '-fno-tree-dse', '-fwrapv', '-fgcse-after-reload', '-fno-align-jumps', '-fno-asynchronous-unwind-tables', '-fno-cse-follow-jumps', '-fno-ivopts', '-fno-guess-branch-probability', '-fprefetch-loop-arrays', '-fno-tree-coalesce-vars', '-fno-common', '-fpredictive-commoning', '-fno-unit-at-a-time', '-fno-cprop-registers', '-fira-coalesce', '-fno-early-inlining', '-fno-delete-null-pointer-checks', '-fselective-scheduling2', '-fno-gcse', '-fno-inline-functions-called-once', '-funswitch-loops', '-fno-tree-vrp', '-fno-tree-dce', '-fno-jump-tables', '-ftree-vectorize', '-fno-argument-alias', '-fno-schedule-insns', '-fno-branch-count-reg', '-fno-tree-switch-conversion', '-fno-auto-inc-dec', '-fno-crossjumping', '-fno-tree-fre', '-fno-tree-reassoc', '-fno-align-functions', '-fno-defer-pop', '-fno-optimize-register-move', '-fno-strict-aliasing', '-fno-rerun-cse-after-loop', '-fno-tree-ccp', '-fno-ipa-cp', '-fno-if-conversion2', '-fno-tree-sra', '-fno-expensive-optimizations', '-fno-tree-copyrename', '-fno-ipa-reference', '-fno-ipa-pure-const', '-fno-thread-jumps', '-fno-if-conversion', '-fno-reorder-blocks', '-falign-loops']

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
        print('gcc -O2 ' + ' '.join(independent) + cmd2)
        os.system('gcc -O2 ' + ' '.join(independent) + cmd2)
        begin = time.time()
        print(cmd5)
        ret = os.system(cmd5)
        if ret != 0:
            continue
        print(ret)
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

class get_exchange(object):
    def __init__(self, incumbent):
        self.incumbent = incumbent

    def to_next(self, feature_id):
        ans = [0] * len(options)
        for f in feature_id:
            ans[f] = 1
        for f in self.incumbent:
            ans[f[0]] = f[1] 
        return ans

def do_search(train_indep, model, eta, rnum):
    features = model.feature_importances_
    print('features')
    print(features)
    
    b = time.time()
    feature_sort = [[i, x] for i, x in enumerate(features)]
    feature_selected = sorted(feature_sort, key=lambda x: x[1], reverse=True)[:fnum]
    feature_ids = [x[0] for x in feature_sort]
    neighborhood_iterators = []    
    for i in range(2 ** fnum):
        comb = bin(i).replace('0b', '')
        comb = '0' * (fnum - len(comb)) + comb
        inc = []
        for k, s in enumerate(comb):
            if s == '1':
                inc.append((feature_selected[k][0], 1))
            else:
                inc.append((feature_selected[k][0], 0))
        neighborhood_iterators.append(get_exchange(inc))
    print('time1:' + str(time.time() - b))

    s = time.time()
    neighbors = []
    r = 0
    print('rnum:' + str(rnum))
    for i, inc in enumerate(neighborhood_iterators):
        for j in range(1 + int(rnum)):
            selected_feature_ids = random.sample(feature_ids, random.randint(0, len(feature_ids)))
            n = neighborhood_iterators[i].to_next(selected_feature_ids)
            neighbors.append(n)
    print('neighbrslen:'+str(len(neighbors)))
    print('time2:' + str(time.time()-s))
    
    pred = []
    estimators = model.estimators_
    s = time.time()
    for e in estimators:
        pred.append(e.predict(np.array(neighbors)))
    acq_val_incumbent = get_ei(pred, eta)
    print('time3:' + str(time.time()-s))
   
    return [[i, a] for a, i in zip(acq_val_incumbent, neighbors)]

def get_ei(pred, eta):
    pred = np.array(pred).transpose(1, 0)
    m = np.mean(pred, axis=1)
    s = np.std(pred, axis=1)

    def calculate_f():
        z = (eta - m) / s
        return (eta - m) * norm.cdf(z) + s * norm.pdf(z)
    
    if np.any(s == 0.0):
        s_copy = np.copy(s)
        s[s_copy == 0.0] = 1.0
        f = calculate_f()
        f[s_copy == 0.0] = 0.0
    else:
        f = calculate_f()

    return f

def get_nd_solutions(train_indep, training_dep, eta, rnum):
    predicted_objectives = []
    model = RandomForestRegressor()
    
    model.fit(np.array(train_indep), np.array(training_dep))
    estimators = model.estimators_

    pred = []
    for e in estimators:
        pred.append(e.predict(train_indep))
    train_ei = get_ei(pred, eta)

    #get_initial_points
    configs_previous_runs = [(x, train_ei[i]) for i, x in enumerate(train_indep)]
    configs_previous_runs_sorted = sorted(configs_previous_runs, key=lambda x: x[1], reverse=True)

    # do search
    begin = time.time()
    merged_predicted_objectives = do_search(train_indep, model, eta, rnum)
    merged_predicted_objectives = sorted(merged_predicted_objectives, key=lambda x: x[1], reverse=True)
    end = time.time()
    print('search time:' + str(begin - end)) 

    begin = time.time()
    for x in merged_predicted_objectives:
        if x[0] not in train_indep:
            print('no repete time:' + str(time.time() - begin))
            return x[0], x[1]

def get_training_sequence(training_indep, training_dep, testing_indep, rnum):
    return_nd_independent, predicted_objectives = get_nd_solutions(training_indep, training_dep, testing_indep, rnum)
    return return_nd_independent, predicted_objectives

def main():
    training_indep = []
    ts = []
    initial_sample_size = 2
    rnum0 = int(os.environ.get('RNUM', 2 ** 8))
    b = time.time()
    sigma = -scale ** 2 / (2 * math.log(decay))
    while len(training_indep) < initial_sample_size:
        x = random.randint(0, 2 ** len(options))
        x = generate_conf(x)
        if x not in training_indep:
            training_indep.append(x)
            ts.append(time.time() - b)

    training_dep = [get_objective_score(r) for r in training_indep]
    steps = 0
    budget = iters
    result = 1e8

    for i, x in enumerate(training_dep):
        if result > x:
            result = x

    while initial_sample_size + steps < budget:
        steps += 1
        rnum = rnum0 * math.exp(-max(0, len(training_indep) - offset) ** 2 / (2 * sigma ** 2))
        best_solution, return_nd_independent = get_training_sequence(training_indep, training_dep, result, rnum)
        print('best_solution')
        print(best_solution)
        training_indep.append(best_solution)
        ts.append(time.time() - b)
        best_result = get_objective_score(best_solution)
        training_dep.append(best_result)

        if best_result < result:
            result = best_result
    
    return training_dep, ts

if __name__ == '__main__':
    stats = []
    times = []

    for i in range(begin2end):
        dep, ts = main()
        print('middle result')
        print(dep)
        stats.append(dep)
        times.append(ts)
        
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
