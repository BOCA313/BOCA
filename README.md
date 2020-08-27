
### BOCA


## Flag list

Under the directory flaglist, there are two files: gccflags.txt and llvmflags.txt, which contain flags used for GCC compiler and for LLVM compiler seperately.

## result

Under this folder, a .pdf file shows the results from 20th iteration to 60th iteration. In this file, a cross means that the approaches timed out in the experiment.

## Benchmarks

CBench, Polybench and Csmith programs are under the cbench, polybench and Csmith directory respectively.

## Source code

Under examples directory, there are source codes written by us. They are examples showing how we carry out the experiment. In boca.py, we compile and execute a program from Polybench by GCC compiler. In ga.py, we show how we test the approach on a program from CBench by GCC compiler. Rio.py compiles and executes a program from Polybench by LLVM compiler. All combinations of programs and compilers can be used in the experiment in a similar way to these examples.
