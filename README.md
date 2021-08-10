# Efficient Compiler Autotuning via Bayesian Optimization(BOCA)

This is the implementation version2.0 of our approach: **Efficient Compiler Autotuning via Bayesian Optimization**.

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
Also, the optimal sequences of different programs are shown in important_flags.txt, where flags among the impactful ones are listed before those that are not impactful. The two kinds of flags are delimited by a "||".
Raw_data_for_results.txt shows the speedups and time of different methods. The .pdf file is generated from this. In the header of this file, there are instructions explaining how to read the file.

## Usage 

### Dependencies
* numpy == 1.19.2
* scikit_learn == 0.22.1
* scipy == 1.6.2

### Installation
```bash
pip3 install -r requirements.txt
```

### How to run
```bash
usage: main.py [-h] --bin-path <directory> --driver <bin> --linker <bin>
               [--libs [<options> [<options> ...]]] [-o <file>]
               [-p <options> [<options> ...]] -src <directory> [-f <num>]
               [--decay <float in 0,1>] [--no-decay] [--scale <num>]
               [--offset <num>] [-S {boca,local}] [-sz <size>] [-b <budget>]

Args needed for BOCA tuning compiler.

optional arguments:
  -h, --help            show this help message and exit
  --bin-path <directory>
                        Specify path to compilation tools.
  --driver <bin>        Specify name of compiler-driver.
  --linker <bin>        Specify name of linker.
  --libs [<options> [<options> ...]]
                        Pass comma-separated <options> on to the compiler-
                        driver.
  -o <file>, --output <file>
                        Write output to <file>.
  -p <options> [<options> ...], --execute-params <options> [<options> ...]
                        Pass comma-separated <options> on to the executable
                        file.
  -src <directory>, --src-dir <directory>
                        Specify path to the source file.
  -f <num>, --fnum <num>
                        Specify number of impactful options of BOCA (8 by
                        default).
  --decay <float in (0,1)>
                        Enable the decay process of BOCA, specify the speed of
                        decay (0.5 by default).
  --no-decay            Disable the decay process of BOCA (enable by default).
  --scale <num>         Specify the scale of the decay process (10 by
                        default).
  --offset <num>        Specify the offset of the decay process (20 by
                        default).
  -S {boca,local}, --selection-strategy {boca,local}
                        Specify the selection strategy of BOCA (boca search by
                        default).
  -sz <size>, --initial-sample-size <size>
                        Specify the initial sample size of BOCA (2 by
                        default).
  -b <budget>, --budget <budget>
                        Number of total instances, including initial sampled
                        ones (60 by default).
```
* In order to tune `gcc-4.4`'s optimization for program `benchmarks/cbench/automotive_bitcount`, execute the following command:
```bash
python3 main.py --bin-path /gcc-lib/bin --driver gcc-4.4 --linker gcc-4.4 --src-dir 'benchmarks/cbench/automotive_bitcount' --execute-params 20
```
* if you want to get a good `clang-3.8` optimization sequence for program `3mm` in `polybench` without decay, execute the followoing:
```bash
python3 main.py --bin-path /usr/bin/ --driver clang-3.8 --linker clang-3.8 --src-dir 'benchmarks/polybench/linear-algebra/kernels/3mm' --libs '-I benchmarks/polybench/utilities benchmarks/polybench/utilities/polybench.c'
```

All combinations of programs and compilers can be used in the experiment in a similar way to these examples.

## Structure
```
|-- algo
|   |-- boca.py
|   |-- executor.py
|
|-- benchmarks
|   |-- cbench
|   |-- CSmith
|   |-- polybench
|
|-- examples
|   |-- boca.py
|   |-- bocas.py
|   |-- ga.py
|   |-- irace.py
|   |-- rio.py
|   |-- tpe.py
|
|-- results
|   |-- flaglist
|   |
|   |-- raw_data_for_results.txt
|   |-- important_flags.txt
|   |-- results.pdf
|
|-- README.md
|-- main.py
```
1. `algo` directory contains BOCA_v2.0 source code.
2. `benchmarks` directory contains two widely-used C benchmarks (i.e., CBench and PolyBench), which have been widely used in many existing studies. Also 5 Csmith generated programs.
3. Under `examples` directory, there are source codes written by us.
4. `results` directory contains detailed results of our experiment.