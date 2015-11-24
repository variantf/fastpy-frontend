#!/usr/bin/env python3
import sys
from parser import parser_main
from constant_folding import constant_folding
from type_inference import type_inference
from dead_code import dead_code
from unused_variable import unused_variable
from unused_function import unused_function
from successive_jump import successive_jump
from jump_next import jump_next
from cpp_generator import cpp_generator

def print_funcs(funcs):
    for func_name in funcs:
        print(func_name)
        print(' variables', funcs[func_name]['vars'])
        print(' parameters', funcs[func_name]['paras'])
        for i in range(len(funcs[func_name]['code'])):
            print('  \033[91m', i, '\033[0m', funcs[func_name]['code'][i])

if len(sys.argv) >= 3:
    funcs = parser_main(sys.argv[1])
    print_funcs(funcs)
    funcs = unused_function(funcs)
    funcs = constant_folding(funcs)
    funcs = dead_code(funcs)
    funcs = unused_variable(funcs)
    funcs = successive_jump(funcs)
    funcs = jump_next(funcs)
    funcs = type_inference(funcs)
    print_funcs(funcs)
    cpp_generator(funcs, sys.argv[2])
else:
    print("Usage: main.py from.py to.cpp")
