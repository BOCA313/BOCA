# encoding:utf-8
import sys, os, time, re
import numpy as np

LOG_DIR = 'log' + os.sep
LOG_FILE = LOG_DIR + 'record.log'
ERROR_FILE = LOG_DIR + 'err.log'
options_rec_file = lambda compiler: LOG_DIR + os.path.basename(os.path.normpath(compiler)) + '_options.txt'
execute_time_bounds = [0.1, 30]

def execmd(cmd):
    print(cmd)
    from subprocess import Popen, PIPE
    pipe = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    stdout, stderr = pipe.communicate()
    reval = stdout.decode()
    return reval


def write_log(ss, file):
    log = open(file, 'a')
    log.write(ss + '\n')
    log.flush()
    log.close()


class Executor:
    def __init__(self, bin_path, driver, linker, output='a.out',
                 execute_params=[], src_dir='.', obj_dir='.',
                 libs=[]):
        self.bin_path = bin_path +os.sep
        self.driver = bin_path + os.sep + driver
        self.linker = bin_path + os.sep + linker
        self.src_dir = src_dir
        self.obj_dir = obj_dir

        assert os.path.exists(self.bin_path)
        assert os.path.exists(self.driver)
        assert os.path.exists(self.linker)
        assert os.path.exists(self.src_dir)

        if not os.path.exists(self.obj_dir):
            os.makedirs(self.obj_dir)

        self.libs = libs
        self.LD_OPTS = '-o ' + output
        self.output = output
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
        if 'gcc' in self.driver:
            cmd = self.driver + ' -O3 -Q --help=optimizers | grep enabled | cut -d\'[\' -f1'
            enabled_opts_o3 = execmd(cmd).split('\n')
            enabled_opts_o3 = [opt.strip() for opt in enabled_opts_o3]
            enabled_opts_o3.remove('')

            cmd = self.driver + ' -O0 -Q --help=optimizers | grep enabled | cut -d\'[\' -f1'
            enabled_opts_o0 = execmd(cmd).split('\n')
            enabled_opts_o0 = [opt.strip() for opt in enabled_opts_o0]
            enabled_opts_o0.remove('')

            for op in enabled_opts_o3:
                if op in enabled_opts_o0:
                    enabled_opts_o3.remove(op)
            if '-fno-threadsafe-statics' in enabled_opts_o3: # special for c++ not c
                enabled_opts_o3.remove('-fno-threadsafe-statics')

            self.o3_opts = enabled_opts_o3
        elif 'clang' in self.driver:
            self.llvm_as = self.bin_path + 'llvm-as'
            self.opt = self.bin_path + 'opt'
            self.llc = self.bin_path + 'llc'
            assert os.path.exists(self.llvm_as)
            assert os.path.exists(self.opt)
            assert os.path.exists(self.llc)

            cmd = self.llvm_as + ' < /dev/null | ' + self.opt + ' -O3 -disable-output -debug-pass=Arguments 2>&1'
            pass_arguments = execmd(cmd).split('\n')
            pass_arguments.remove('')
            enabled_opts = []
            for pass_ag in pass_arguments:
                item = re.findall('Pass Arguments:  (.*)', pass_ag)[0].split(' ')
                enabled_opts.extend(item)
            self.o3_opts = enabled_opts
        for opt in self.o3_opts:
            write_log(opt, options_rec_file(self.driver))

    def __genoptseq__(self, independent):
        """
        :param independent: 01 list of options
        :return: corresponding options sequence
        """
        print(len(independent), independent)
        print(len(self.o3_opts), self.o3_opts)
        opt_seq = []
        for k, s in enumerate(independent):
            if s == 1:
                opt_seq.append(self.o3_opts[k])
        return opt_seq

    def __compile__(self, opt_opts):
        """
        Compile with GCC/LLVM
        :return:
        """
        if 'gcc' in self.driver:
            self.__compilegcc__(opt_opts=opt_opts)  # optimization level
            return self.output
        elif 'clang' in self.driver:
            self.__compilellvmorig__(opt_opts=opt_opts,  # opt optimization level
                                     driver_opts='-O0')  # clang optimization level
            return self.output
        write_log('Unknown compiler: ' + self.driver + '.', ERROR_FILE)
        sys.exit()

    def __clean__(self):
        """
        Clean binary code and source code
        """
        execmd('rm -f *.o *.I *.s out a.out *.a *.s *.i')

    def __compilegcc__(self, opt_opts):
        """
        Compile with GCC
        """
        cmd = ' '.join([self.driver, opt_opts, '-c'] + self.libs) + ' ' + self.src_dir + os.sep + '*.c'
        _ = execmd(cmd)
        cmd = ' '.join([self.linker, self.LD_OPTS, opt_opts, ' -lm *.o'])
        _ = execmd(cmd)

    def __compilellvmorig__(self, opt_opts, driver_opts):
        """
        Compile with LLVM, using clang, opt, llc
        """
        for cfile in os.listdir(self.src_dir):
            if cfile.endswith('.c') and (not cfile.startswith('._')):
                basename = cfile.split('.c')[0]
                bcfile = basename+'.bc'
                cmd = ' '.join([self.driver] + self.libs + [driver_opts]) + ' -emit-llvm -c ' \
                      + self.src_dir + os.sep + cfile + ' -o ' + bcfile
                _ = execmd(cmd)

                cmd = self.opt + ' -S ' + opt_opts + ' ' + bcfile + ' -o ' + basename + '.opt.bc'
                _ = execmd(cmd)

                cmd = self.llc + ' -O0 -filetype=obj ' + basename + '.opt.bc'
                _ = execmd(cmd)

        linker_opts = driver_opts
        cmd = ' '.join([self.linker, self.LD_OPTS, linker_opts]) + ' -lm *.o'
        _ = execmd(cmd)

    def __compilellvmsuo__(self, opt_opts, driver_opts='-O3'):
        """
        clang -c -emit-llvm -O3 -mllvm -disable-llvm-optzns
        => opt -flags => llc
        => clang
        => exec
        """
        cmd_suo = ' '.join([self.driver, self.libs,
                            driver_opts]) + ' -emit-llvm -mllvm -disable-llvm-optzns -c ' + self.src_dir + os.sep + '*.c'
        cmd_prefer = ' '.join([self.driver, self.libs,
                               driver_opts]) + ' -emit-llvm -Xclang -disable-llvm-passes -c ' + self.src_dir + os.sep + '*.c'
        _ = execmd(cmd_suo)
        for bicode in os.listdir('.'):
            if bicode.endswith('.bc') and (bicode.endswith('.opt.bc') != True):
                basename = bicode.split('.bc')[0]
                cmd = self.opt + ' -S ' + opt_opts + ' ' + bicode + ' -o ' + basename + '.opt.bc'
                _ = execmd(cmd)
                cmd = self.llc + ' -O0 -filetype=obj ' + basename + '.opt.bc'  # $basename.opt.o
                _ = execmd(cmd)
        linker_opts = driver_opts
        cmd = ' '.join([self.linker, self.LD_OPTS, linker_opts]) + ' -lm *.o'
        _ = execmd(cmd)

    def get_objective_score(self, independent, k_iter, n_eval=5, fail_toleration=10):
        """
        Get current optimization sequence speedup over -O3

        :param independent: 0-1 list, 0 for disable opt_k, 1 for enable opt_k
        :return: median speedup over -O3
        """
        independent = self.__genoptseq__(independent)
        level_fined = ' '.join(independent)
        level_o3 = '-O3'
        gen_execute_cmd = lambda outfile, params: 'time ./' + outfile + ' ' + ' '.join(params)

        speedups = []
        step = 0
        while (len(speedups) < n_eval + 1):
            step += 1
            if step > fail_toleration:
                write_log('Failed configuration!', ERROR_FILE)
                write_log(' '.join([self.driver, level_fined]), ERROR_FILE)
                sys.exit(0)

            self.__clean__()
            output = self.__compile__(opt_opts='-O2 '+level_fined)
            cmd = gen_execute_cmd(output, self.execute_params)
            print(cmd)
            begin = time.time()
            ret = os.system(cmd)
            if ret != 0:
                write_log('Step ' + str(step) + ' return code ' + str(ret), ERROR_FILE)
                assert ret == 0
            end = time.time()
            de = end - begin
            assert de > execute_time_bounds[0]
            assert de < execute_time_bounds[1]

            self.__clean__()
            output = self.__compile__(opt_opts=level_o3)
            cmd = gen_execute_cmd(output, self.execute_params)
            print(cmd)
            begin = time.time()
            _ = os.system(cmd)
            end = time.time()
            nu = end - begin
            assert nu > execute_time_bounds[0]
            assert nu < execute_time_bounds[1]

            # op_str = "nu:{} de:{} spd:{}".format(str(nu), str(de), str(nu / de))
            # write_log(op_str, LOG_FILE)
            # speedups.append(nu / de)

        op_str = "iteration:{} speedup:{}".format(str(k_iter), str(np.median(speedups)))
        write_log(op_str, LOG_FILE)
        return np.median(speedups)

    def get_objective_score_fix(self, independent, k_iter, n_eval=5, fail_toleration=10):
        flag = -1
        if k_iter % 2 == 0:
            flag = 1
        return 1 + flag*(sum(independent)/len(independent))



if __name__ == '__main__':

    automotive_bitcount_HOME = '/boca-test/benchmarks/cbench/automotive_bitcount'
    params_cbench = {
        'ZCC': ['gcc-4.5', 'clang-3.8'][1],
        'LDCC': ['gcc-4.5', 'clang-3.8'][1],
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
        e.__compilellvmorig__(driver_opts='-O0', opt_opts='-O3', )
        b1 = time.time()
        os.system(exe_cmd)
        ed1 = time.time()
        o0o3.append(ed1 - b1)

        e.__clean__()
        e.__compilellvmorig__(driver_opts='-O0', opt_opts='-O1')
        b2 = time.time()
        os.system(exe_cmd)
        ed2 = time.time()
        o0o1.append(ed2 - b2)

        e.__clean__()
        e.__compilellvmorig__(driver_opts='-O3', opt_opts='-O3')
        b3 = time.time()
        os.system(exe_cmd)
        ed3 = time.time()
        o3o3.append(ed3 - b3)

        e.__clean__()
        e.__compilellvmorig__(driver_opts='-O3', opt_opts='-O1')
        b2 = time.time()
        os.system(exe_cmd)
        ed2 = time.time()
        o3o1.append(ed2 - b2)

    write_log('O0-O3 average: ' + str(np.mean(o0o3)), rec_file)
    write_log('O0-O1 average: ' + str(np.mean(o0o1)), rec_file)
    write_log('O3-O3 average: ' + str(np.mean(o3o3)), rec_file)
    write_log('O3-O1 average: ' + str(np.mean(o3o1)), rec_file)
