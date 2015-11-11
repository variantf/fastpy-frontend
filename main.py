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

if len(sys.argv) >= 3:
	src = parser_main(sys.argv[1])
	src = constant_folding(src)
	src = dead_code(src)
	src = unused_variable(src)
	src = successive_jump(src)
	src = jump_next(src)
	src = type_inference(src)
	cpp_generator(src, sys.argv[2])
else:
	print("Usage: main.py from.py to.cpp")