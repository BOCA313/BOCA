# Efficient Compiler Autotuning via Bayesian Optimization(BOCA)

This is the implementation repository of our approach: **Efficient Compiler Autotuning via Bayesian Optimization**.

## Description

`BOCA` is  the first Bayesian optimization based approach for compiler autotuning. The goal is to tune compiler's optimization flags as efficient as possible in order to achieve the required runtime performance of the compiled programs. We further propose a searching strategy in `BOCA` to improve the efficiency of Bayesian optimization that can strike a balance between exploitation and exploration. We conduct extensive experiments to investigate the effectiveness of `BOCA` based on `GCC 4.7.7` , `LLVM 2.9 `and `GCC 8.3.1`. `BOCA` significantly outperforms the state-of-the-art compiler autotuning approaches and Bayesion optimization methods in terms of the time spent on achieving specified speedups, demonstrating the effectiveness of `BOCA`.

## Compilers/Benchmarks/Result

### Compilers/Benchmarks

We used two most popular C compilers (i.e., `GCC` and `LLVM`) and two widely-used C benchmarks (i.e., `CBench` and `PolyBench`), which have been widely used in many existing studies. Also 5 Csmith generated programs. 



| Compiler | Version | Optimization flags number |
| -------- | ------- | ------------------------- |
| GCC      | 4.7.7   | 71                        |
| LLVM     | 2.9     | 64                        |
| GCC      | 8.3.1   | 86                        |

Under the directory `flaglist`, there are two files: `gcc4flags.txt`,` llvmflags.txt` and  `gcc8flags.txt`, which contain flags used for `GCC` compiler and for `LLVM` compiler seperately.



| ID      | Program             | Number of Source Lines of Code |
| ------- | ------------------- | ------------------------------ |
| C1      | consumer_jpeg_c     | 26,950                         |
| C2      | security_sha        | 297                            |
| C3      | automotive_bitcount | 954                            |
| C4      | automotive_susan_e  | 2,129                          |
| C5      | automotive_susan_c  | 2,129                          |
| C6      | automotive_susan_s  | 2,129                          |
| C7      | bzip2e              | 7,200                          |
| C8      | consumer_tiff2rgba  | 22,321                         |
| C9      | telecom_adpcm_c     | 389                            |
| C10     | office_rsynth       | 5,412                          |
| P1      | 2mm                 | 252                            |
| P2      | 3mm                 | 267                            |
| P3      | cholesky            | 212                            |
| P4      | jacobi-2d           | 200                            |
| P5      | lu                  | 210                            |
| P6      | correlation         | 248                            |
| P7      | nussinov            | 569                            |
| P8      | symm                | 231                            |
| P9      | heat-3d             | 211                            |
| P10     | covariance          | 218                            |
| CSmith1 | trainprogram1.c     | 4160                           |
| CSmith2 | trainprogram2.c     | 11793                          |
| CSmith3 | trainprogram3.c     | 10049                          |
| CSmith4 | trainprogram4.c     | 8703                           |
| CSmith5 | trainprogram5.c     | 12246                          |

`CBench`, `Polybench` and `5 Csmith programs` are under the `cbench`, `polybench` and `Csmith` directory respectively.



### Result

Under this folder, a .pdf file shows the results from 20th iteration to 60th iteration. In this file, a cross means that the approaches timed out in the experiment.



## Reproducibility

### Environment

Our study is conducted on a workstation with 16- core Intel(R) Xeon(R) CPU E5-2640 v3, 126G memory, and CentOS 6.10 operating system. (**Note: in docker environment**)

### Source code

Under `examples` directory, there are source codes written by us. 

| script     | Description                                                  |
| ---------- | ------------------------------------------------------------ |
| `boca.py`  | Compiler Autotuning via Bayesian Optimization.               |
| `bocas.py` | BOCA with the local search strategy used in SMAC.            |
| `ga.py`    | Genetic Algorithm based Iterative Optimization (initial size of 4). |
| `irace.py` | Irace-based Iterative Optimization.                          |
| `rio.py`   | Random Iterative Optimization.                               |
| `tpe.py`   | an advanced general Bayesian optimization.                   |



### Compile with GCC/LLVM

They are examples showing commands we used to compile benchmark programs with C compilers (i.e., `GCC` and `LLVM`) .

#### GCC

Compile `CBench` programs under current directory using `GCC` with optimization flag `-targetlibinfo` and `-tti` using command line.

```bash
gcc -fbranch-count-reg -fcaller-saves -c *.c 
gcc -fbranch-count-reg -fcaller-saves -lm *.o
time ./a.out # execute
```

Compile `Polybench` programs `3mm` using `GCC` with optimization flag `-fbranch-count-reg` and`-fcaller-saves `using command line.

```bash
gcc -O2 -fbranch-count-reg -fcaller-saves -I utilities -I linear-algebra/kernels/3mm utilities/polybench.c linear-algebra/kernels/3mm/3mm.c -lm -DPOLYBENCH_TIME -o 3mm_time
time ./3mm_time # execute
```

Compile `Csmith` program `trainprogram1.c` using `GCC` with optimization flag `-fbranch-count-reg` and`-fcaller-saves` using command line.

```bash
gcc -g -Wall -std=c99 -O2 -fbranch-count-reg -fcaller-saves trainprogram1.c -o a.out
time ./a.out # execute
```



#### LLVM

There are more steps to compile program(s) with `LLVM` than with `GCC` since the front, middle and back ends of `LLVM` are controlled by three commands instead of one.

Compile `CBench` programs under current directory using LLVM with optimization flag `-targetlibinfo` and `-tti` using Python.

```python
for file in cur_dir:
	if file.endswith('.c') and file.startswith('._') != True:

		clangcmd = 'clang -O0 -scalarrepl  -emit-llvm -c -I./ ' + file + ' -o ' + file[:-1] + 'bc'	
		optcmd = 'opt -targetlibinfo -tti -S ' + file[:-1] + 'bc -o ' + file[:-1] + 'opt.bc'
		llccmd = 'llc  -O2 -filetype=obj ' + file[:-1] + 'opt.bc -o ' + file[:-1] + 'o'
    
		os.system(optcmd)
		os.system(clangcmd)
		os.system(llccmd)

cmd = 'clang   -O0 -scalarrepl -lm *.o'
os.system(cmd)

os.system('time ./a.out') # execute
```

Compile `Polybench` program `3mm` using `LLVM` with optimization flag `-targetlibinfo` and `-tti` using Python.

```python
files = os.listdir('./')
files.append('../utilities/polybench.c')

for file in 3mm_dir:
	if file.endswith('.c') and file.startswith('._') != True:
		file_name = file.split('/')[-1][:-1]
		clangcmd = 'clang -O0 -scalarrepl  -emit-llvm -I ../utilities -I ./ -c ' + file + ' -o ' + file_name + 'bc '
		optcmd = 'opt -targetlibinfo -tti -S ' + file_name + 'bc -o ' + file_name + 'opt.bc '
		llccmd = 'llc  -O2 -filetype=obj ' + file_name + 'opt.bc -o ' + file_name + 'o '
		
		os.system(optcmd)
		os.system(clangcmd)
		os.system(llccmd)
cmd = 'clang -O0 -scalarrepl -lm *.o '
os.system(cmd) 

os.system('time ./a.out') # execute
```

Compile `Csmith` program `test.c` using `LLVM` with optimization flag `-targetlibinfo` and `-tti` using command line.

```bash
clang -O0 -emit-llvm -c -I./ trainprogram1.c -o trainprogram1.c.bc
opt -targetlibinfo -tti -S trainprogram1.c.bc -o trainprogram1.c.opt.bc
llc -O3 -filetype=obj trainprogram1.c.opt.bc -o trainprogram1.c.o
clang -O0 -lm *.o 

time ./a.out # execute
```



In `boca.py`, we compile and execute a program from Polybench by GCC compiler. In `ga.py`, we show how we test the approach on a program from CBench by GCC compiler. In  `rio.py` compiles and executes a program from Polybench by LLVM compiler. 

All combinations of programs and compilers can be used in the experiment in a similar way to these examples.

