# encoding: utf-8
import os
import random
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Args needed for BOCA tuning compiler.")
    # compilation params
    parser.add_argument('--bin-path',
                        help='Specify path to compilation tools.',
                        metavar='<directory>', required=True)
    parser.add_argument('--driver',
                        help='Specify name of compiler-driver.',
                        metavar='<bin>', required=True)
    parser.add_argument('--linker',
                        help='Specify name of linker.',
                        metavar='<bin>',required=True)
    parser.add_argument('--libs',
                        help='Pass comma-separated <options> on to the compiler-driver.',
                        nargs='*', metavar='<options>',default='')
    parser.add_argument('-o', '--output',
                        help='Write output to <file>.',
                        default='a.out', metavar='<file>')
    parser.add_argument('-p', '--execute-params',
                        help='Pass comma-separated <options> on to the executable file.',
                        nargs='+', metavar='<options>')
    parser.add_argument('-src', '--src-dir',
                        help='Specify path to the source file.',
                        required=True, metavar='<directory>')
    # parser.add_argument('-obj', '--obj-dir',
    #                     help='Specify path to save object file.',
    #                     metavar='<directory>')

    # BOCA params
    parser.add_argument('-f', '--fnum',
                        help='Specify number of impactful options of BOCA (8 by default).',
                        type=int, default=8, metavar='<num>')
    # parser.add_argument('-r', '--rnum',
    #                     help='specify base-number of less-impactful option-sequences of BOCA, will decay if the decay process is enabled',
    #                     type=int, default=2**8, metavar='<num>')
    parser.add_argument('--decay',
                        help='Enable the decay process of BOCA, specify the speed of decay (0.5 by default).',
                        default=0.5, type=float, metavar='<float in (0,1)>')
    parser.add_argument('--no-decay',
                        help='Disable the decay process of BOCA (enable by default).',
                        action='store_true')
    parser.add_argument('--scale',
                        help='Specify the scale of the decay process (10 by default).',
                        type=int, default=10, metavar='<num>')
    parser.add_argument('--offset',
                        help='Specify the offset of the decay process (20 by default).',
                        type=int, default=20, metavar='<num>')
    parser.add_argument('-S', '--selection-strategy',
                        help='Specify the selection strategy of BOCA (boca search by default).',
                        default='boca', choices=['boca', 'local'])
    parser.add_argument('-sz', '--initial-sample-size',
                        help='Specify the initial sample size of BOCA (2 by default).',
                        type=int, default=2, metavar='<size>')
    parser.add_argument('-b', '--budget',
                        help='Number of total instances, including initial sampled ones (60 by default).',
                        type=int, default=60, metavar='<budget>')
    parser.add_argument('--seed',
                        help='Fix <seed> for random process and model building.',
                        type=int, default=456, metavar='<seed>')





    args = parser.parse_args()
    if args.seed:
        random.seed(args.seed)
    from algo.executor import Executor, LOG_DIR
    from algo.boca import BOCA

    if not os.path.exists(LOG_DIR):
        os.system('mkdir '+LOG_DIR)


    make_params = {}
    boca_params = {}
    bin_path = args.bin_path
    if not bin_path.endswith(os.sep):
        make_params['bin_path'] = args.bin_path
    else:
        make_params['bin_path'] = args.bin_path[:-1]
    make_params['driver'] = args.driver
    make_params['linker'] = args.linker
    if args.libs:
        make_params['libs'] = args.libs
    make_params['output'] = args.output
    if args.execute_params:
        make_params['execute_params'] = args.execute_params
    make_params['src_dir'] = args.src_dir
    # if args.obj_dir:
    #     make_params['obj_dir'] = args.obj_dir

    e = Executor(**make_params)
    tuning_list = e.o3_opts

    print(len(tuning_list), tuning_list)

    boca_params['s_dim'] = len(tuning_list)
    boca_params['get_objective_score'] = e.get_objective_score
    # boca_params['get_objective_score']=e.get_objective_score_test
    boca_params['fnum'] = args.fnum
    boca_params['decay'] = args.decay
    boca_params['no_decay'] = args.no_decay
    boca_params['scale'] = args.scale
    boca_params['offset'] = args.offset
    boca_params['selection_strategy'] = args.selection_strategy
    boca_params['budget'] = args.budget
    boca_params['initial_sample_size'] = args.initial_sample_size
    if args.seed:
        boca_params['seed'] = args.seed


    boca = BOCA(**boca_params)

    begin2end = 5
    stats = []
    times = []
    for _ in range(begin2end):
        dep, ts = boca.run()
        print('middle result')
        print(dep)
        stats.append(dep)
        times.append(ts)
    for j, v_tmp in enumerate(stats):
        max_s = 0
        for i, v in enumerate(v_tmp):
            max_s = max(max_s, v)
            v_tmp[i] = max_s
    print(times)
    print(stats)

    time_mean = []
    time_std = []
    stat_mean = []
    stat_std = []
    import numpy as np
    for i in range(args.budget):
        time_tmp = []
        stat_tmp = []
        for j in range(begin2end):
            time_tmp.append(times[j][i])
            stat_tmp.append(stats[j][i])
        time_mean.append(np.mean(time_tmp))
        time_std.append(np.std(time_tmp))
        stat_mean.append(np.mean(stat_tmp))
        stat_std.append(np.std(stat_tmp))
    print(time_mean)
    print(time_std)
    print(stat_mean)
    print(stat_std)
