#!/usr/bin/env python3
import sys
from parser import parser_main
from constant_folding import constant_folding
from type_inference import type_inference
from dead_code import dead_code
from unused_variable import unused_variable
from successive_jump import successive_jump
from jump_next import jump_next
from cpp_generator import cpp_generator

test_funcs = {
    "f": {
        "paras": ['x'],
        "return": 'f_ret',
        "code": [
            ('==', ('symbol', 'cond'), ('symbol', 'x'), ('constant', 0)),
            ('ifnot', ('symbol', 'cond'), 4),
            ('=', ('symbol', 'f_ret'), ('constant', 1)),
            ('jmp', 7),
            ('-', ('symbol', 'x-1'), ('symbol', 'x'), ('constant', 1)),
            ('call', ('symbol', 'fx-1'), 'f', [('symbol', 'x-1')]),
            ('*', ('symbol', 'f_ret'), ('symbol', 'x'), ('symbol', 'fx-1')),
        ]
    },
    "_main$": {
        "paras": [],
        "code": [
            ('call', ('symbol', 'f3'), 'f', [('constant', 3)]),
            ('call', None, 'print', [('symbol', 'f3')]),
            ('call', None, 'f', [('constant', 2)])
        ]
    }
}

if len(sys.argv) >= 3:
    funcs = parser_main(sys.argv[1])
    for func_name in funcs:
        print(func_name)
        print('vars', funcs[func_name]['vars'])
        print('paras', funcs[func_name]['paras'])
        for i in range(len(funcs[func_name]['code'])):
            print('\t', i, funcs[func_name]['code'][i])
    exit(0)
    src = type_inference(test_funcs)
    for i in range(len(src)):
        print(i, src[i])
    exit(0)
    #src = constant_folding(src)
    #src = dead_code(src)
    #src = unused_variable(src)
    #src = successive_jump(src)
    #src = jump_next(src)
    src = type_inference(src)
    cpp_generator({'_main$': {'code': src, 'vars': funcs['_main$']['vars']}}, sys.argv[2])
else:
    print("Usage: main.py from.py to.cpp")
