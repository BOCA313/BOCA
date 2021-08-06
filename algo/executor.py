# encoding:utf-8
import sys, os, time, re
import numpy as np
options_rec_file = lambda compiler: os.path.basename(os.path.normpath(compiler)) +'_options.txt'
LOG_FILE = 'record.log'
ERROR_FILE = 'err.log'

def execmd(cmd):
    print(cmd)
    from subprocess import Popen, PIPE
    pipe = Popen(cmd, shell=True,stdout=PIPE,stderr=PIPE)
    stdout, stderr = pipe.communicate()
    reval = stdout.decode()
    return reval

def write_log(ss,file):
    log = open(file,'a')
    log.write(ss+'\n')
    log.flush()
    log.close()

class Executor:
    def __init__(self, ZCC, LDCC, BIN_NAME='a.out',
                 execute_params='', SRC_DIR='.', OBJ_DIR='.',
                 CCC_OPTS=''):
        self.ZCC = ZCC
        self.LDCC = LDCC
        self.SRC_DIR = SRC_DIR
        self.CCC_OPTS = CCC_OPTS  # -I lib
        self.LD_OPTS = '-o '+BIN_NAME
        self.BIN_NAME = BIN_NAME
        self.execute_params = execute_params
        self.__geno3opts__()  # get Member variables, like o3_opts
        # if not os.path.exists(OBJ_DIR):
        #     _ = execmd('mkdir '+OBJ_DIR)
        # self.OBJ_DIR = OBJ_DIR + os.sep

    def __geno3opts__(self):
        """
        Get -O3 enabled options from cmd line.
        If using LLVM, get clang, llvm-as, opt, llc for later compilation process
        :return:
        """
        if 'gcc' in self.ZCC:
            cmd = self.ZCC + ' -O3 -Q --help=optimizers | grep enabled | cut -d\'[\' -f1'
            enabled_opts = execmd(cmd).split('\n')
            enabled_opts = [opt.strip() for opt in enabled_opts]
            enabled_opts.remove('')
            self.o3_opts = enabled_opts
        elif 'clang' in self.ZCC:
            cmd = 'whereis '+self.ZCC+' | cut -d\' \' -f2'
            execute_path = execmd(cmd)
            home = os.path.abspath(os.path.dirname(execute_path)+os.path.sep+".")
            self.llvmas = execmd('ls '+home+' | grep llvm-as').strip()
            self.opt = execmd('ls '+home+' | grep opt-').strip()
            self.llc = execmd('ls '+home+' | grep llc-').strip()
            cmd = self.llvmas+' < /dev/null | ' + self.opt+' -O3 -disable-output -debug-pass=Arguments 2>&1'
            pass_arguments = execmd(cmd).split('\n')
            pass_arguments.remove('')
            enabled_opts = []
            for pass_ag in pass_arguments:
                item = re.findall('Pass Arguments:  (.*)',pass_ag)[0].split(' ')
                enabled_opts.extend(item)
            self.o3_opts = enabled_opts
        for opt in self.o3_opts:
            write_log(opt,options_rec_file(self.ZCC))

    def __genoptseq__(self,independent):
        """
        :param independent: 01 list of options
        :return: corresponding options sequence
        """
        print(len(independent), independent)
        print(len(self.o3_opts),self.o3_opts)
        opt_seq = []
        for k, s in enumerate(independent):
            if s == 1:
                opt_seq.append(self.o3_opts[k])
        return opt_seq

    def __compile__(self,  CCC_OPTS_ADD, OPT_OPTS):
        """
        Compile with GCC/LLVM
        :return:
        """
        if 'gcc' in self.ZCC:
            self.__compilegcc__(CCC_OPTS_ADD=CCC_OPTS_ADD)  # optimization level
            return self.BIN_NAME
        elif 'clang' in self.ZCC:
            self.__compilellvmorig__(CCC_OPTS_ADD=CCC_OPTS_ADD,  # clang optimization level
                                     OPT_OPTS=OPT_OPTS)  # opt optimization level
            return self.BIN_NAME
        write_log('Unknown compiler: '+self.ZCC+'.', ERROR_FILE)
        sys.exit()

    def __clean__(self):
        """
        Clean binary code and source code
        """
        execmd('rm -f *.o *.I *.s out a.out *.a *.s *.i')

    def __compilegcc__(self, CCC_OPTS_ADD):
        """
        Compile with GCC
        """
        cmd = ' '.join([self.ZCC, self.CCC_OPTS, CCC_OPTS_ADD]) + ' -c '+self.SRC_DIR+os.sep+'*.c'
        _ = execmd(cmd)
        cmd = ' '.join([self.LDCC, self.LD_OPTS, CCC_OPTS_ADD]) + ' -lm *.o'
        _ = execmd(cmd)

    def __compilellvmorig__(self, OPT_OPTS, CCC_OPTS_ADD='-O0'):
        """
        Compile with LLVM, using clang, opt, llc
        """
        cmd = ' '.join([self.ZCC, self.CCC_OPTS, CCC_OPTS_ADD]) + ' -emit-llvm -c '+self.SRC_DIR+os.sep+'*.c'
        _ = execmd(cmd)
        for bicode in os.listdir('.'):
            if bicode.endswith('.bc') and (bicode.endswith('.opt.bc') != True):
                basename = bicode.split('.bc')[0]
                cmd = self.opt + ' -S ' + OPT_OPTS + ' ' +bicode + ' -o ' + basename + '.opt.bc'
                _ = execmd(cmd)
                cmd = self.llc + ' -O0 -filetype=obj ' + basename + '.opt.bc'  # $basename.opt.o
                _ = execmd(cmd)

        cmd = ' '.join([self.LDCC, self.LD_OPTS, CCC_OPTS_ADD]) + ' -lm *.o'
        _ = execmd(cmd)

    def __compilellvmsuo__(self, OPT_OPTS, CCC_OPTS_ADD='-O3'):
        """
        clang -c -emit-llvm -O3 -mllvm -disable-llvm-optzns
        => opt -flags => llc
        => clang
        => exec
        """
        cmd0 = ' '.join([self.ZCC, self.CCC_OPTS, CCC_OPTS_ADD]) + ' -emit-llvm -mllvm -disable-llvm-optzns -c ' + self.SRC_DIR + os.sep+'*.c'
        cmd_prefer = ' '.join([self.ZCC, self.CCC_OPTS, CCC_OPTS_ADD]) + ' -emit-llvm -Xclang -disable-llvm-passes -c ' + self.SRC_DIR + os.sep+'*.c'
        _ = execmd(cmd0)
        for bicode in os.listdir('.'):
            if bicode.endswith('.bc') and (bicode.endswith('.opt.bc') != True):
                basename = bicode.split('.bc')[0]
                cmd = self.opt + ' -S ' + OPT_OPTS + ' ' + bicode + ' -o ' + basename + '.opt.bc'
                _ = execmd(cmd)
                cmd = self.llc + ' -O0 -filetype=obj ' + basename + '.opt.bc'  # $basename.opt.o
                _ = execmd(cmd)
        cmd = ' '.join([self.LDCC, self.LD_OPTS, CCC_OPTS_ADD]) + ' -lm *.o'
        _ = execmd(cmd)



    def get_objective_score(self, independent, k_iter, n_eval = 5, fail_toleration = 10):
        """
        Get current optimization sequence speedup over -O3

        :param independent: 0-1 list, 0 for disable opt_k, 1 for enable opt_k
        :return: median speedup over -O3
        """
        independent = self.__genoptseq__(independent)
        level_fined = ' '.join(independent)
        level_o3 = '-O3'
        gen_execute_cmd = lambda outfile, params: 'time '+outfile+' ' + ' '.join(params)

        speedups = []
        step = 0
        while (len(speedups) < n_eval+1):
            step += 1
            if step > fail_toleration:
                write_log('Failed configuration!', ERROR_FILE)
                write_log(' '.join([self.ZCC, level_fined]), ERROR_FILE)
                sys.exit(0)

            self.__clean__()
            BIN_NAME = self.__compile__(OPT_OPTS=level_fined)
            cmd = gen_execute_cmd(BIN_NAME,self.execute_params)
            print(cmd)
            begin = time.time()
            ret = os.system(cmd)
            if ret != 0:
                write_log('Step '+str(step)+' return code '+str(ret), ERROR_FILE)
                continue
            end = time.time()
            de = end - begin

            self.__clean__()
            BIN_NAME = self.__compile__(OPT_OPTS=level_o3)
            cmd = gen_execute_cmd(BIN_NAME, self.execute_params)
            print(cmd)
            begin = time.time()
            _ = os.system(cmd)
            end = time.time()
            nu = end - begin

            op_str = "nu:{} de:{} spd:{}".format(str(nu),str(de),str(round(nu/de)))
            write_log(op_str, LOG_FILE)
            speedups.append(nu / de)

        op_str = "iteration:{} speedup:{}".format(str(k_iter),str(np.median(speedups)))
        write_log(op_str, LOG_FILE)
        return np.median(speedups)

if __name__ == '__main__':

    automotive_bitcount_HOME = '/boca-test/benchmarks/cbench/automotive_bitcount'
    params_cbench = {
        'ZCC': ['gcc-4.5','clang-3.8'][1],
        'LDCC': ['gcc-4.5','clang-3.8'][1],
        'execute_params': '2000',
        'dir': automotive_bitcount_HOME
    }

    poly_HOME = '/boca-test/benchmarks/polybench/medley/nussinov'
    params_poly = {
        'ZCC': ['gcc-4.5', 'clang-3.8'][1],
        'LDCC': ['gcc-4.5', 'clang-3.8'][1],
        'CCC_OPTS': '-I /boca-test/benchmarks/polybench/utilities /boca-test/benchmarks/polybench/utilities/polybench.c',
        'dir': poly_HOME
    }

    e = Executor(**params_cbench)

    exe_cmd = 'time ./a.out 20000'
    # exe_cmd = 'time ./a.out'
    rec_file = 'compilationApproach.txt'
    o0o3 = []
    o0o1 = []
    o3o3 = []
    o3o1 = []
    for _ in range(1):
        e.__clean__()
        e.__compile__(CCC_OPTS_ADD='-O0',OPT_OPTS='-O3', )
        b1 = time.time()
        os.system(exe_cmd)
        ed1 = time.time()
        o0o3.append(ed1 - b1)

        e.__clean__()
        e.__compile__(CCC_OPTS_ADD='-O0',OPT_OPTS='-O1')
        b2 = time.time()
        os.system(exe_cmd)
        ed2 = time.time()
        o0o1.append(ed2 - b2)

        e.__clean__()
        e.__compile__(CCC_OPTS_ADD='-O3', OPT_OPTS='-O3')
        b3 = time.time()
        os.system(exe_cmd)
        ed3 = time.time()
        o3o3.append(ed3 - b3)

        e.__clean__()
        e.__compile__(CCC_OPTS_ADD='-O3', OPT_OPTS='-O1')
        b2 = time.time()
        os.system(exe_cmd)
        ed2 = time.time()
        o3o1.append(ed2 - b2)

    write_log('O0-O3 average: ' + str(np.mean(o0o3)), rec_file)
    write_log('O0-O1 average: ' + str(np.mean(o0o1)), rec_file)
    write_log('O3-O3 average: ' + str(np.mean(o3o3)), rec_file)
    write_log('O3-O1 average: ' + str(np.mean(o3o1)), rec_file)
