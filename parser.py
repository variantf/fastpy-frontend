#!/usr/bin/env python3
import ast
import random

triple_code_lines = []

class symbol_table:
	sym_tb_stack = [{
		'range': 'range::__init__',
		'__iter__': '__iter__',
		'None': 'none::make',
		'__add__': '__add__',
		'__sub__': '__sub__',
		'len': '__len__'
	}]
	def push_sym_tb(self):
		self.sym_tb_stack.append({})

	def pop_sym_tb(self):
		self.sym_tb_stack.pop()

	def add_symbol(self, key, value = None):
		if None == value:
			value = key
		sym_tb_now = self.sym_tb_stack[len(self.sym_tb_stack) - 1]
		if key in sym_tb_now:
			raise Exception('key has already defined')
		sym_tb_now[key] = value

	def get_symbol(self, key, add = False):
		last_idx = len(self.sym_tb_stack) - 1
		if add:
			if key in self.sym_tb_stack[last_idx]:
				return self.sym_tb_stack[last_idx][key]
			else:
				self.sym_tb_stack[last_idx][key] = key
				return key
		else:
			for i in range(len(self.sym_tb_stack)-1, -1, -1):
				if key in self.sym_tb_stack[i]:
					return self.sym_tb_stack[i][key]
			raise Exception('can not find symbol: ' + key)

sym_tb = symbol_table()


def gen_code_triple(code_type, a, b = None, c = None, target = triple_code_lines):
	if code_type in ['jmp']:
		target.append((code_type, a))
	elif code_type in ['+', '-', '*', '/', '&', '|', '~', 'is', '==', '>', '<', '>=', '<=', '!=', '>>', '<<', '%']:
		target.append((code_type, a, b, c))
	elif code_type in ['call']:
		target.append((code_type, a, b, c))
	elif code_type in ['if', 'ifnot']:
		target.append((code_type, a, b))
	elif code_type in ['=']:
		target.append((code_type, a, b))
	else:
		raise Exception('Unknown instruction: ' + code_type)
	return len(target) - 1

def modify_target_for_currentIdx(idx, target = triple_code_lines):
	if target[idx][0] == 'if':
		target[idx] = ('if', target[idx][1], len(target))
	elif target[idx][0] == 'ifnot':
		target[idx] = ('ifnot', target[idx][1], len(target))
	elif target[idx][0] == 'jmp':
		target[idx] = ('jmp', len(target))
	else:
		print(target[idx])
		raise Exception('Unknown code type')

def modify_target(idx, val, target = triple_code_lines):
	target[idx] = (target[item][i] if 1 != i else val for i in range(len(target[idx])))

def get_currentIdx(target = triple_code_lines):
	return len(target)

name_id = 0

def gen_name(n=5):
	#name = '_' + ''.join([random.choice('abcdefghighkmnopqrstuvwxyz') for _ in range(n)]) + '$'
	global name_id
	name_id = name_id + 1
	name = '_' + str(name_id) + '$'
	sym_tb.add_symbol(name)
	return ('symbol', name)

continue_stack = []
break_stack = []

def gen_dfs(node):
	if type(node) is ast.Module:
		sym_tb.push_sym_tb()
		body = node.body
		for stmt in body:
			gen_dfs(stmt)
		sym_tb.pop_sym_tb()
		return
	elif type(node) is ast.NameConstant:
	    return ('constant', node.value)
	elif type(node) is ast.For:
		target = gen_dfs(node.target)
		it = gen_dfs(node.iter)
		iterator = gen_name()
		gen_code_triple('call', iterator, '__iter__', [it])
		continue_stack.append(gen_code_triple('call', target, '__next__', [iterator]))
		break_stack.append([])
		test = gen_name()
		test_idx = gen_code_triple('==', test, target, ('constant', None))
		ed_loop = gen_code_triple('if', test, 0)

		for stmt in node.body:
			gen_dfs(stmt)

		gen_code_triple('call', target, '__next__', [iterator])
		gen_code_triple('jmp', test_idx)
		modify_target_for_currentIdx(ed_loop)

		for stmt in node.orelse:
			gen_dfs(stmt)

		brk = break_stack.pop()
		for line in brk:
			modify_target_for_currentIdx(line)
	elif type(node) is ast.Num:
		return ('constant', node.n)
	elif type(node) is ast.Str:
		return ('constant', node.s)
	elif type(node) is ast.Expr:
		return gen_dfs(node.value)
	elif type(node) is ast.Call:
		tmp_name = gen_name()
		if type(node.func) is ast.Name:
			gen_code_triple('call', tmp_name, node.func.id, [gen_dfs(arg) for arg in node.args])
		elif type(node.func) is ast.Attribute:
			gen_code_triple('call', tmp_name, node.func.attr, [gen_dfs(node.func.value)] + [gen_dfs(arg) for arg in node.args])
		return tmp_name
	elif type(node) is ast.Name:
		ctx = node.ctx
		if type(ctx) is ast.Load:
			return ('symbol', sym_tb.get_symbol(node.id))
		elif type(ctx) is ast.Store:
			return ('symbol', sym_tb.get_symbol(node.id, True))
		raise Exception('Unknown ctx for Name')
	elif type(node) is ast.Assign:
		source_name = gen_dfs(node.value)
		for target in node.targets:
			if type(target) is ast.Name:
				gen_code_triple('=', gen_dfs(target), source_name)
			elif type(target) is ast.Subscript:
				(name, sub) = gen_dfs(target)
				gen_code_triple('call', None, '__setitem__', [name, sub, gen_dfs(node.value)])
		return
	elif type(node) is ast.BinOp:
		if type(node.op) is ast.Add:
			op = '+'
		elif type(node.op) is ast.Sub:
			op = '-'
		elif type(node.op) is ast.Mult:
			op = '*'
		elif type(node.op) is ast.Div:
			op = '/'
		elif type(node.op) is ast.BitOr:
			op = '|'
		elif type(node.op) is ast.BitAnd:
			op = '&'
		elif type(node.op) is ast.BitXor:
			op = '^'
		elif type(node.op) is ast.RShift:
			op = '>>'
		elif type(node.op) is ast.LShift:
			op = '<<'
		elif type(node.op) is ast.Mod:
			op = '%'
		else:
			raise Exception('Unknown op')
		tmp_name = gen_name()
		gen_code_triple(op, tmp_name, gen_dfs(node.left), gen_dfs(node.right))
		return tmp_name
	elif type(node) is ast.UnaryOp:
		tmp_name = gen_name()
		if type(node.op) is ast.Invert:
			gen_code_triple('~', tmp_name, gen_dfs(node.operand))
		elif type(node.op) is ast.Not:
			gen_code_triple('call', tmp_name, '__not__', [gen_dfs(node.operand)])
		else:
			raise Exception('Unknown unary operator')
	elif type(node) is ast.If:
		test = gen_dfs(node.test)
		test_idx = gen_code_triple('ifnot', test, 0)
		for stmt in node.body:
			gen_dfs(stmt)
		if node.orelse:
			test_else_idx = gen_code_triple('jmp', 0)
			modify_target_for_currentIdx(test_idx)
			for stmt in node.orelse:
				gen_dfs(stmt)
			modify_target_for_currentIdx(test_else_idx)
		else:
			modify_target_for_currentIdx(test_idx)
		return
	elif type(node) is ast.BoolOp:
		ret_name = gen_name()
		goto_ed = []
		if type(node.op) is ast.And:
			for i in range(len(node.values)):
				value = node.values[i]
				tmp_result = gen_dfs(value)
				gen_code_triple('=', ret_name, tmp_result)
				if i != len(node.values) - 1:
					goto_ed.append(gen_code_triple('ifnot', tmp_result, 0))
			for idx in goto_ed:
				modify_target_for_currentIdx(idx)
			return ret_name
		elif type(node.op) is ast.Or:
			goto_ed = []
			for i in range(len(node.values)):
				value = node.values[i]
				tmp_result = gen_dfs(value)
				gen_code_triple('=', ret_name, tmp_result)
				if i != len(node.values) - 1:
					goto_ed.append(gen_code_triple('if', tmp_result, 0))
			for idx in goto_ed:
				modify_target_for_currentIdx(idx)
			return tmp_result
		else:
			raise Exception('Unknown op type for BoolOp')
	elif type(node) is ast.Compare:
		tmp_name = gen_name()
		left = gen_dfs(node.left)
		right_it = iter([gen_dfs(comparators) for comparators in node.comparators])
		goto_ed = []
		for i in range(len(node.ops)):
			op = node.ops[i]
			right = next(right_it)
			if type(op) is ast.Lt:
				gen_code_triple('<', tmp_name, left, right)
			elif type(op) is ast.Gt:
				gen_code_triple('>', tmp_name, left, right)
			elif type(op) is ast.Eq:
				gen_code_triple('==', tmp_name, left, right)
			elif type(op) is ast.LtE:
				gen_code_triple('<=', tmp_name, left, right)
			elif type(op) is ast.GtE:
				gen_code_triple('>=', tmp_name, left, right)
			elif type(op) is ast.NotEq:
				gen_code_triple('!=', tmp_name, left, right)
			elif type(op) is ast.Is:
				gen_code_triple('is', tmp_name, left, right)
			else:
				raise Exception('Unhandled Compare operators')
			left = right
			if i != len(node.ops) - 1:
				goto_ed.append(gen_code_triple('ifnot', tmp_name, 0))
		for idx in goto_ed:
			modify_target_for_currentIdx(idx)
		return tmp_name
	elif type(node) is ast.comprehension:
		target = gen_dfs(node.target)
		it = gen_dfs(node.iter)
		tmp_iter_name = gen_name()
		gen_code_triple('call', tmp_iter_name, '__iter__', [it])
		test_idx = gen_code_triple('call', target, '__next__', [tmp_iter_name])
		test = gen_name()
		gen_code_triple('==', test, target, ('constant', None))
		ed_idx = gen_code_triple('if', test, 0)
		for _if in node.ifs:
			if_name = gen_dfs(_if)
			gen_code_triple('ifnot', if_name, test_idx)
		return (test_idx, ed_idx)
	elif type(node) is ast.ListComp:
		tmp_lst_name = gen_name()
		gen_code_triple('=', tmp_lst_name, ('constant', []))
		idxs = []
		for generator in node.generators:
			idxs.append(gen_dfs(generator))
		elt = gen_dfs(node.elt)
		gen_code_triple('call', None, 'append', [tmp_lst_name, elt])
		while len(idxs) > 0:
			test_idx, ed_idx = idxs.pop()
			gen_code_triple('jmp', test_idx)
			modify_target_for_currentIdx(ed_idx)
		return tmp_lst_name
	elif type(node) is ast.SetComp:
		tmp_set_name = gen_name()
		gen_code_triple('=', tmp_set_name, ('constant', set()))
		idxs = []
		for generator in node.generators:
			idxs.append(gen_dfs(generator))
		elt = gen_dfs(node.elt)
		gen_code_triple('call', None, 'add', [tmp_set_name, elt])
		while len(idxs) > 0:
			test_idx, ed_idx = idxs.pop()
			gen_code_triple('jmp', test_idx)
			modify_target_for_currentIdx(ed_idx)
		return tmp_set_name
	elif type(node) is ast.DictComp:
		tmp_dict_name = gen_name()
		gen_code_triple('=', tmp_dict_name, ('constant', {}))
		idxs = []
		for generator in node.generators:
			idxs.append(gen_dfs(generator))
		key = gen_dfs(node.key)
		val = gen_dfs(node.value)
		gen_code_triple('call', None, '__setitem__', [tmp_dict_name, key, val])
		while len(idxs) > 0:
			test_idx, ed_idx = idxs.pop()
			gen_code_triple('jmp', test_idx)
			modify_target_for_currentIdx(ed_idx)
		return tmp_dict_name
	elif type(node) is ast.Subscript:
		name = gen_dfs(node.value)
		sub = gen_dfs(node.slice.value)
		if type(node.ctx) is ast.Load:
			tmp_name = gen_name()
			gen_code_triple('call', tmp_name, '__getitem__', [name, sub])
			return tmp_name
		elif type(node.ctx) is ast.Store:
			return (name, sub)
		else:
			raise Exception('Unknown ctx type')
	elif type(node) is ast.While:
		start_idx = get_currentIdx()
		continue_stack.append(start_idx)

		test_name = gen_dfs(node.test)
		end_idx = gen_code_triple('ifnot', test_name, 0)
		break_stack.append([])

		for stmt in node.body:
			gen_dfs(stmt)

		gen_code_triple('jmp', start_idx)
		brk = break_stack.pop()

		modify_target_for_currentIdx(end_idx)

		for stmt in node.orelse:
			gen_dfs(stmt)

		for line in brk:
			modify_target_for_currentIdx(line)

	elif type(node) is ast.Break:
		break_stack[len(break_stack) - 1].append(gen_code_triple('jmp', 0))
	elif type(node) is ast.Continue:
		gen_code_triple('jmp', continue_stack[len(continue_stack) - 1])
	elif type(node) is ast.List:
		list_name = gen_name()
		gen_code_triple('=', list_name, ('constant', []))
		for ele in node.elts:
			gen_code_triple('call', None, 'append', [list_name, gen_dfs(ele)])
		return list_name
	elif type(node) is ast.Set:
		set_name = gen_name()
		gen_code_triple('=', set_name, ('constant', set()))
		for ele in node.elts:
			gen_code_triple('call', None, 'add', [set_name, gen_dfs(ele)])
		return set_name
	elif type(node) is ast.Dict:
		dict_name = gen_name()
		gen_code_triple('=', dict_name, ('constant', dict()))
		for i in range(len(node.keys)):
			key = gen_dfs(node.keys[i])
			value = gen_dfs(node.values[i])
			gen_code_triple('call', None, '__setitem__', [dict_name, key, value])
		return dict_name
	else:
		print(node)
		raise Exception('Unknown node type ' + str(type(node)))


f = open('py_code.py', 'r')
code = ''.join(f.readlines())
node = ast.parse(code)
#print(ast.dump(node))
gen_dfs(node)

f = open('triple_code', 'w')
for line in triple_code_lines:
	print(line)
	print(line, file = f)
f.close()



