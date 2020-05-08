#!/usr/bin/python
#encoding: utf-8
###############################################################################
# This script is the command that is executed every run.
# Check the examples in examples/
#
# This script is run in the execution directory (execDir, --exec-dir).
#
# PARAMETERS:
# argv[1] is the candidate configuration number
# argv[2] is the instance ID
# argv[3] is the seed
# argv[4] is the instance name
# The rest (argv[5:]) are parameters to the run
#
# RETURN VALUE:
# This script should print one numerical value: the cost that must be minimized.
# Exit with 0 if no error, with 1 in case of error
###############################################################################

import datetime
import os.path
import re
import subprocess
import os, sys
import time
import numpy as np
import logging
import random

## This a dummy example that shows how to parse the parameters defined in
## parameters.txt and does not need to call any other software.

cmd2 = ''
cmd3 = ''
cmd4 = ''
cmd5 = ''

logging.basicConfig(level=logging.DEBUG,
                    format='%(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='ilog.log',
                    filemode='a+')

def clean():
    os.system(cmd4)

def compile(level, opt):
    os.system(cmd2)
    logging.info(level+' '+opt)

# Useful function to print errors.
def target_runner_error(msg):
    now = datetime.datetime.now()
    print(str(now) + " error: " + msg)
    sys.exit(1)

def get_objective_score(independent):
    speedups = []
    step = 0
    while (len(speedups) < 6):
        step += 1
        if step > 10:
            print('failed configuration!')
            os.exit(0)
        clean()
        compile('-O2', independent)
        begin = time.time()
        ret = os.system(cmd5)
        if ret != 0:
            continue
        end = time.time()
        de = end - begin
  
        clean()
        compile('-O3', '')
        begin = time.time()
        os.system(cmd5)
        end = time.time()
        nu = end - begin

        logging.info('nu:' + str(nu) + ' de:' + str(de) + ' val:' + str(nu / de))
        speedups.append(nu / de)

    logging.info(speedups)
    return -np.median(speedups)


## This a dummy example that shows how to parse the parameters defined in
## parameters.txt and does not need to call any other software.

if __name__ == '__main__':
    if len(sys.argv) < 5:
        print(
        "\nUsage: ./c-target-runner.py <configuration_id> <instance_id> <seed> <instance_path_name> <list of parameters>\n")
        sys.exit(1)

    # Get the parameters as command line arguments.
    configuration_id = sys.argv[1]
    instance_id = sys.argv[2]
    seed = sys.argv[3]
    instance = sys.argv[4]
    cand_params = sys.argv[5:]

    # Default values (if any)
    mu = 1
    val = None
    indep = ' '
    # Parse parameters

    while cand_params:
        # Get and remove first and second elements.
        passiter = cand_params.pop(0)
        pa = passiter[:-1]
        enable = passiter[-1:]
        if enable == "1":  # enable=1
            val = 2
            indep += pa+' '
        elif enable == "0":
            val = 1
	        # indep = indep
        else:
            target_runner_error("unknown parameter %s" % (passiter))
        mu *= val
#	logging.info('time:' + tm)
#    	logging.info('indep:' + indep)
#    	logging.info('dep:' + str(res))

    tm = str(time.time())
    res = mu
    # res = get_objective_score(indep)
    logging.info('indep '+str(configuration_id)+' '+ indep)
    logging.info('time:' + tm)
    logging.info('dep:' + str(res))

    print(str(res) + '\n')
    sys.exit(0)
