from constant_folding import constant_folding
from type_inference import type_inference
from dead_code import dead_code
from unused_variable import unused_variable
from successive_jump import successive_jump
from jump_next import jump_next

with open('triple_code', 'r') as f:
    src = [eval(l) for l in f.readlines()]

src = constant_folding(src)
src = dead_code(src)
src = unused_variable(src)
src = successive_jump(src)
src = jump_next(src)
src = type_inference(src)

with open('optimized', 'w') as f:
	for l in src:
		print(l, file=f)