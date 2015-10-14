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
	}]
	def push_symbol_table():
		sym_tb_stack.append({})

	def ppo_symbol_table():
		sym_tb_stack.pop()

	def add_symbol(key, value):
		sym_tb_stack[key] = value

	def get_symbol(key, add = False):
		last_idx = len(sym_tb_stack) - 1
		if add:
			if key in sym_tb_stack[last_idx]:
				return sym_tb_stack[last_idx][key]
			else:
				sym_tb_stack[last_idx][key] = key
				return key
		else:
			for i in range(len(sym_tb_stack)-1, 0, -1):
				if key in sym_tb_stack[i]:
					return sym_tb_stack[i][key]
			raise Exception('can not find symbol')

sym_tb = symbol_table()


def gen_code_triple(code_type, a, b, c, target = triple_code_lines):
	a = sym_tb.get_symbol(a)
	b = sym_tb.get_symbol(b)
	if code_type == 'call':
		c = [symbol_table.get_symbol() for s in c]
	else:
		c = sym_tb.get_symbol(c)
	target.append((code_type, a, b, c))
	return len(target) - 1

def modify_target_for_currentIdx(idx, target = triple_code_lines):
	target[idx] = (target[idx][0], target[idx][1], target[idx][2], len(target))


local_sym_tb = set()

file_output = open('output.cpp', 'w')

header_lines = [
	'#include <cstdio>',
	'#include <stdexcept>',
	'#include "assert.h"',
	'#include "type.h"',
	'#include "list.h"',
	'#include "int.h"',
	'#include "float.h"',
	'#include "str.h"',
	'#include "dict.h"',
	'#include "bool.h"',
	'#include "set.h"',
	'#include "func.h"',
	'#include "none.h"',
	'#include "range.h"',
	'#include "range_iterator.h"',
	'int main() {'
]

declare_lines = []

code_lines = []

def gen_name(n=5):
	name = '_' + ''.join([random.choice('abcdefghighkmnopqrstuvwxyz') for _ in range(n)]) + '$'
	sym_tb.add_symbol(name)
	return ('symbol', name)

indent = 0

def code_yield(code, simi = True):
	print('\t' * indent + code + (';' if simi else ''))
	code_lines.append('\t' * indent + code + (';' if simi else ''))

def code_enter_block():
	global indent
	code_yield('{', False)
	indent = indent + 1

def code_leave_block():
	global indent
	indent = indent - 1
	code_yield('}', False)

def gen_dfs(node):
	if type(node) is ast.Module:
		body = node.body
		for stmt in body:
			gen_dfs(stmt)
		return
	elif type(node) is ast.NameConstant:
		if node.value is None:
			return 'none::make()'
		else:
			raise Exception('Unknown NameConstant')
	elif type(node) is ast.For:
		target = gen_dfs(node.target)
		it = gen_dfs(node.iter)
		iterator = gen_name()
		gen_code_triple('call', iterator, '__iter__', [it])
		gen_code_triple('call', target, '__next__', iterator)
		test = gen_name()
		test_idx = gen_code_triple('==', test, target, ('constant', 'none::make()'))
		gen_code_triple('if', test, 0)

		for stmt in node.body:
			gen_dfs(stmt)

		gen_code_triple('call', target, '__next__', [iterator])
		gen_code_triple('jmp', test_idx)
		modify_target_for_currentIdx(test_idx)
	elif type(node) is ast.Num:
		tmp_name = gen_name()
		if type(node.n) is int:
			return ('constant', 'int_::make(%d)' % node.n)
		elif type(node.n) is float:
			return ('constant', 'float::make(%f)' % node.n)
		else:
			raise 'Unknown number type'
	elif type(node) is ast.Str:
		return ('constant', 'str::make("%s")' % node.s)
	elif type(node) is ast.Expr:
		return gen_dfs(node.value)
	elif type(node) is ast.Call:
		tmp_name = gen_name()
		gen_code_triple('call', )
		code_yield(tmp_name + ' = ' + gen_dfs(node.func) + '(' + ', '.join([gen_dfs(arg) for arg in node.args]) + ')')
		return tmp_name
	elif type(node) is ast.Name:
		ctx = node.ctx
		if type(ctx) is ast.Load:
			return ('symbol', symbol_table.get_symbol(node.id))
		elif type(ctx) is ast.Store:
			if not node.id in sym_tb:
				sym_tb[node.id] = node.id
				declare_lines.append("value %s;" % node.id)
		return sym_tb[node.id]
	elif type(node) is ast.Assign:
		for target in node.targets:
			if type(target) is ast.Name:
				code_yield(gen_dfs(target) + ' = ' + gen_dfs(node.value))
			elif type(target) is ast.Subscript:
				(name, sub) = gen_dfs(target)
				code_yield('__setitem__(%s, %s, %s)' % (name, sub, gen_dfs(node.value)))
		return 'void'
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
		tmp_name = gen_name()
		gen_code_triple()
		code_yield('%s = %s(%s, %s)' % (tmp_name, op, gen_dfs(node.left), gen_dfs(node.right)))
		return tmp_name
	elif type(node) is ast.UnaryOp:
		tmp_name = gen_name()
		if type(node.op) is ast.Invert:
			code_yield('%s = __invert__(%s)', tmp_name, gen_dfs(node.operand))
		elif type(node.op) is ast.Not:
			code_yield('%s = bool_::make(!__bool__(%s).boolval)', tmp_name, gen_dfs(node.operand))
		else:
			raise Exception('Unknown unary operator')
	elif type(node) is ast.If:
		res = gen_dfs(node.test)
		code_yield('if(' + res + ')', False)
		code_enter_block()
		for stmt in node.body:
			gen_dfs(stmt)
		code_leave_block()
		code_yield('else', False)
		code_enter_block()
		for stmt in node.orelse:
			gen_dfs(stmt)
		code_leave_block()
		return 'void'
	elif type(node) is ast.BoolOp:
		pass
	elif type(node) is ast.Compare:
		tmp_name = gen_name()
		left = gen_dfs(node.left)
		right_it = iter([gen_dfs(comparators) for comparators in node.comparators])
		for op in node.ops:
			if type(op) is ast.Lt:
				code_yield('%s = __lt__(%s, %s)' % (tmp_name, left, next(right_it)))
			elif type(op) is ast.Gt:
				code_yield('%s = __gt__(%s, %s)' % (tmp_name, left, next(right_it)))
			elif type(op) is ast.Eq:
				code_yield('%s = __eq__(%s, %s)' % (tmp_name, left, next(right_it)))
			elif type(op) is ast.LtE:
				code_yield('%s = __le__(%s, %s)' % (tmp_name, left, next(right_it)))
			elif type(op) is ast.GtE:
				code_yield('%s = __ge__(%s, %s)' % (tmp_name, left, next(right_it)))
			elif type(op) is ast.NotEq:
				code_yield('%s = __ne__(%s, %s)' % (tmp_name, left, next(right_it)))
			else:
				raise Exception('Unhandled Compare operators')
		return tmp_name
	elif type(node) is ast.ListComp:
		tmp_lst_name = gen_name()
		code_yield(tmp_lst_name +' = list::make()')
		for generator in node.generators:
			target = gen_dfs(generator.target)
			it = gen_dfs(generator.iter)
			tmp_iter_name = gen_name()
			code_yield('%s = __iter__(%s)' % (tmp_iter_name, it))
			code_yield('for(%s = __next__(%s); %s != none::make(); %s = __next__(%s))' % (target, tmp_iter_name, target, target, tmp_iter_name), False)
			code_enter_block()
			elt = gen_dfs(node.elt)
			code_yield('append(' + tmp_lst_name + ', %s)' % elt)
			code_leave_block()
		return tmp_lst_name
	elif type(node) is ast.Subscript:
		name = gen_dfs(node.value)
		sub = gen_dfs(node.slice.value)
		if type(node.ctx) is ast.Load:
			tmp_name = gen_name()
			code_yield('%s = __getitem__(%s,%s)' % (tmp_name, name, sub))
			return tmp_name
		elif type(node.ctx) is ast.Store:
			return (name, sub)
		else:
			raise Exception('Unknown ctx type')
	else:
		raise Exception('Unknown node type ' + str(type(node)))

node = ast.parse(code)
print(ast.dump(node))
gen_dfs(node)

file_output.write('\n'.join(header_lines) + '\n')
file_output.write('\n'.join(declare_lines) + '\n')
file_output.write('\n'.join(code_lines) + '\n')
file_output.write('}\n')