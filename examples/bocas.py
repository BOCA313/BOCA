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
iters = 120
begin2end = 5
md = int(os.environ.get('MODEL', 1))
fnum = int(os.environ.get('FNUM', 8))
decay = float(os.environ.get('DECAY', 0.5))
scale = float(os.environ.get('SCALE', 10))
offset = float(os.environ.get('OFFSET', 20))

cmd2 = ''
cmd3 = ''
cmd4 = ''
cmd5 = ''

cbenchList = [
        # 'automotive_bitcount',
        # 'automotive_qsort1',
        # 'automotive_susan_c',
        # 'automotive_susan_e',
        # 'automotive_susan_s',
        # 'bzip2d',
        # 'bzip2e',
        # 'consumer_jpeg_c',
        # 'consumer_jpeg_d',
        # 'consumer_lame', #
        # 'consumer_mad', #
        # 'consumer_tiff2bw',
        # 'consumer_tiff2rgba',
        # 'consumer_tiffdither',
        # 'consumer_tiffmedian',
        # 'network_dijkstra',
        # 'network_patricia',
        # 'office_ghostscript', #
        # 'office_ispell', #
        # 'office_rsynth', #
        # 'office_stringsearch1',
        # 'security_blowfish_d',
        # 'security_blowfish_e',
        # 'security_pgp_d', #
        # 'security_pgp_e', #
        # 'security_rijndael_d',
        # 'security_rijndael_e',
        # 'security_sha',
        # 'telecom_CRC32',
         'telecom_adpcm_c',
        # 'telecom_adpcm_d',
        # 'telecom_gsm', #
    ]



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

def clean():
    os.system(cmd5)
    print cmd5

def compile(level, opt):
    os.system('ls |wc -l')
    os.system(cmd2)
    print cmd2

def get_objective_score(independent,bench_name,seq):
    independent = generate_opts(independent)
    # path = './cBench_V1.1/' + bench_name + '/src'
    # os.chdir(path)
    # os.system('pwd')
    # cmd1 = 'make clean'
    # cmd2 = 'gcc -O2 ' + ' '.join(independent) + ' -c  *.c'
    # cmd3 = 'gcc -O2 ' + ' '.join(independent) + ' -o a.out  -lm *.o'
    cmd5 = 'time ./a.out'
    speedups = []
    step = 0
    while (len(speedups) < 6):
        step += 1
        if step > 8:
            return 0.0
        # os.system(cmd1)
        clean()
        # print(cmd2)
        # os.system(cmd2)
        # print(cmd3)
        # os.system(cmd3)
        compile(' ', ' '.join(independent))
        begin = time.time()
        print(cmd5)
        ret = os.system(cmd5)
        if ret > 0:
            continue
        print(ret)
        end = time.time()
        de = end - begin

        clean()
        compile('-O3', '')
        begin = time.time()
        os.system(cmd5)
        end = time.time()
        nu = end - begin

        print('nu:' + str(nu) + ' de:' + str(de) + ' val:' + str(nu / de))
        speedups.append(nu / de)

    print(speedups)
    # os.chdir("../../../")
    return -np.median(speedups)

def generate_conf(x):
    comb = bin(x).replace('0b', '')
    comb = '0' * (len(options)  - len(comb)) + comb
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

def do_search(train_indep, model, eta, incumbents):
    b = time.time()
    neighborhood = []
    for inc0 in incumbents:
        num = 0
        inc = inc0
        while num < 100:
            neighbors_for_i = []
            for i in inc[0]:
                tmp = copy.deepcopy(inc[0])
                tmp[i] = 1 - tmp[i]
                neighbors_for_i.append(tmp)
            pred = []
            estimators = model.estimators_
            for e in estimators:
                pred.append(e.predict(np.array(neighbors_for_i)))
            acq_val_incumbent = get_ei(pred, eta)
            max_n = None
            max_a = 0
            for i, x in enumerate(neighbors_for_i):
                if max_a < acq_val_incumbent[i]:
                    max_a = acq_val_incumbent[i]
                    max_n = x
            num += 1
            if max_a <= inc[1]:
                break
            inc = (max_n, max_a)
        neighborhood.append(inc[0])
    for i in range(10000):
        x = random.randint(0, 2 ** len(options))
        x = generate_conf(x)
        neighborhood.append(x)

    pred = []
    estimators = model.estimators_
    s = time.time()
    for e in estimators:
        pred.append(e.predict(np.array(neighborhood)))
    acq_val_incumbent = get_ei(pred, eta)

    return [[i, a] for a, i in zip(acq_val_incumbent, neighborhood)]

def get_ei(pred, eta):
    pred = np.array(pred).transpose(1, 0)
    m = np.mean(pred, axis=1)
    s = np.std(pred, axis=1)
    print('m:' + str(m))
    print('s:' + str(s))

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
    configs_previous_runs_sorted = sorted(configs_previous_runs, key=lambda x: x[1], reverse=True)[:10]

    # do search
    begin = time.time()
    merged_predicted_objectives = do_search(train_indep, model, eta, configs_previous_runs_sorted)
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
def pr(a,b,c):
    print str(a)+str(b)+str(c)
def main(cn,seq):
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
    training_dep = [get_objective_score(r,cn,seq) for r in training_indep]
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
        best_result = get_objective_score(best_solution,cn,seq)
        training_dep.append(best_result)

        if best_result < result:
            result = best_result

    return training_dep, ts

if __name__ == '__main__':
    for cn in cbenchList:
        stats = []
        times = []

        for i in range(begin2end):
            dep, ts = main(cn, 1)
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
