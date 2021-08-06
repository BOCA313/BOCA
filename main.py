# encoding: utf-8
import random
random.seed(456)
from algo.executor import Executor
from algo.boca import BOCA
import argparse

"""
todo
1. no decay
2. 
"""

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Args needed for BOCA.")
    # compilation params
    parser.add_argument('--ZCC',
                        help='configure the tool chain ZCC.',
                        metavar='<bin>')
    parser.add_argument('--LDCC',
                        help='configure the tool chain LDCC.',
                        metavar='<bin>')
    parser.add_argument('--CCC-OPTS',
                        help='pass comma-separated <options> on to the ZCC.',
                        nargs='*', metavar='<options>')
    parser.add_argument('-o', '--BIN-NAME',
                        help='specify the output file name.',
                        default='a.out', metavar='<file>')
    parser.add_argument('-p', '--execute-params',
                        help='pass comma-separated <options> on to the executable file.',
                        nargs='+', metavar='<options>')
    parser.add_argument('-src', '--SRC-DIR',
                        help='specify the path to the source file.',
                        default='.', metavar='<directory>')
    # parser.add_argument('-obj','--OBJ-DIR',
    #                     help='a',
    #                     default='.'
    #                     )


    # BOCA params
    parser.add_argument('-f', '--fnum',
                        help='specify number of impactful options of BOCA',
                        type=int, default=8, metavar='<num>')
    # parser.add_argument('-r', '--rnum',
    #                     help='specify base-number of less-impactful option-sequences of BOCA, will decay if the decay process is enabled',
    #                     type=int, default=2**8, metavar='<num>')
    parser.add_argument('--decay',
                        help='enable the decay process of BOCA, specify the speed of decay.',
                        default=0.5, metavar='<float in (0,1)>')
    parser.add_argument('--no-decay',
                        help='disable the decay process of BOCA (enable by default).',
                        action='store_true')
    parser.add_argument('--scale',
                        help='specify the scale of the decay process.',
                        type=int, default=10, metavar='<num>')
    parser.add_argument('--offset',
                        help='specify the offset of the decay process.',
                        type=int, default=20, metavar='<num>')
    parser.add_argument('-S', '--selection-strategy',
                        help='specify the selection strategy of BOCA.',
                        default='boca', choices=['boca', 'local'])
    parser.add_argument('-sz', '--initial-sample-size',
                        help='specify the initial sample size of BOCA',
                        type=int, default=2, metavar='<size>')
    parser.add_argument('-b', '--budget',
                        help='specify the total instances for exploration, including initial sampled ones',
                        type=int, default=60, metavar='<budget>')


    args = parser.parse_args()

    make_params = {}
    boca_params = {}
    print(args.ZCC)
    make_params['ZCC'] = args.ZCC
    make_params['LDCC'] = args.LDCC
    make_params['CCC_OPTS'] = args.CCC_OPTS
    make_params['BIN_NAME'] = args.BIN_NAME
    make_params['execute_params'] = args.execute_params
    make_params['SRC_DIR'] = args.SRC_DIR

    e = Executor(**make_params)
    tuning_list = e.o3_opts
    print(tuning_list)

    boca_params['s_dim'] = len(tuning_list)
    boca_params['get_objective_score'] = e.get_objective_score
    boca_params['fnum'] = args.fnum
    boca_params['decay'] = args.decay
    boca_params['no_decay'] = args.no_decay
    boca_params['scale'] = args.scale
    boca_params['offset'] = args.offset
    boca_params['selection_strategy'] = args.selection_strategy
    boca_params['budget'] = args.budget
    boca_params['initial_sample_size'] = args.initial_sample_size
    print(boca_params)
    print(make_params)

    boca = BOCA(**boca_params)
    boca.run()
