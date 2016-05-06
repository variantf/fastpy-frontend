#!/usr/bin/env python3
import ast
import random
import optimizer


code_slice = {}

def gen_code_triple(code_type, a, b = None, c = None, target = None):
    if not target:
        target = code_slice[current_func]['code']
    if code_type in ['jmp']:
        target.append((code_type, a))
    elif code_type in optimizer.BINARY_OPERATORS:
        target.append((code_type, a, b, c))
    elif code_type in ['call']:
        target.append((code_type, a, b, c))
    elif code_type in ['if', 'ifnot']:
        target.append((code_type, a, b))
    elif code_type in optimizer.UNARY_OPERATORS:
        target.append((code_type, a, b))
    else:
        raise Exception('Unknown instruction: ' + code_type)
    return len(target) - 1

def modify_target_for_currentIdx(idx, target = None):
    if not target:
        target = code_slice[current_func]['code']
    if target[idx][0] == 'if':
        target[idx] = ('if', target[idx][1], len(target))
    elif target[idx][0] == 'ifnot':
        target[idx] = ('ifnot', target[idx][1], len(target))
    elif target[idx][0] == 'jmp':
        target[idx] = ('jmp', len(target))
    else:
        print(target[idx])
        raise Exception('Unknown code type')

def modify_target(idx, val, target = None):
    if not target:
        target = code_slice[current_func]['code']
    target[idx] = (target[item][i] if 1 != i else val for i in range(len(target[idx])))

def get_currentIdx(target = None):
    if not target:
        target = code_slice[current_func]['code']
    return len(target)

def add_symbol(name, target = None):
    if not target:
        target = code_slice[current_func]['vars']
    local_name = name + '$' + current_func
    if not name in code_slice[current_func]['global'] and not local_name in code_slice[current_func]['paras']:
        target.add(local_name)

name_id = 0

def gen_name(n=5):
    #name = '_' + ''.join([random.choice('abcdefghighkmnopqrstuvwxyz') for _ in range(n)]) + '$'
    global name_id
    name_id = name_id + 1
    name = '_' + str(name_id) + '$'
    add_symbol(name)
    return ('symbol', name + '$' + current_func)

def get_name(name):
    local_name = name + '$' + current_func
    if local_name in code_slice[current_func]['vars'] or local_name in code_slice[current_func]['paras']:
        return local_name
    return name + '$_main$'

continue_stack = []
break_stack = []

def gen_dfs(node):
    global current_func
    if type(node) is ast.FunctionDef:
        code_slice[node.name] = {'code': [], 'vars': set(), 'paras': [], 'global': set(), 'ret': []}
        last_func = current_func
        current_func = node.name
        for arg in node.args.args:
            code_slice[current_func]['paras'].append(arg.arg + '$' + current_func)
        add_symbol('_$$ret')
        gen_code_triple('=', ('symbol', get_name('_$$ret')), ('constant', None))
        for stmt in node.body:
            gen_dfs(stmt)
        for l in code_slice[current_func]['ret']:
            modify_target_for_currentIdx(l)
        current_func = last_func
    elif type(node) is ast.Return:
        if node.value is not None:
            gen_code_triple('=', ('symbol', get_name('_$$ret')), gen_dfs(node.value))
        code_slice[current_func]['ret'].append(gen_code_triple('jmp', 0))
    elif type(node) is ast.Global:
        for name in node.names:
            code_slice['_main$']['vars'].add(name + '$_main$')
            code_slice[current_func]['global'].add(name)
    elif type(node) is ast.Module:
        current_func = '_main$'
        code_slice[current_func] = {'code': [], 'vars': set(), 'global': set(), 'paras': []}
        body = node.body
        for stmt in body:
            gen_dfs(stmt)
        current_func = None
    elif type(node) is ast.NameConstant:
        return ('constant', node.value)
    elif type(node) is ast.For:
        target = gen_dfs(node.target)
        it = gen_dfs(node.iter)
        iterator = gen_name()
        gen_code_triple('call', iterator, 'iter', [it])
        continue_stack.append(gen_code_triple('call', target, 'next', [iterator]))
        break_stack.append([])
        test = gen_name()
        test_idx = gen_code_triple('==', test, target, ('constant', None))
        ed_loop = gen_code_triple('if', test, 0)

        for stmt in node.body:
            gen_dfs(stmt)

        gen_code_triple('call', target, 'next', [iterator])
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
            return ('symbol', get_name(node.id))
        elif type(ctx) is ast.Store:
            add_symbol(node.id)
            return ('symbol', get_name(node.id))
        elif type(ctx) is ast.Del:
            gen_code_triple('call', None, '__delitem__', [('symbol', get_name(node.id))])
        else:
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
        test_bool = gen_name()
        gen_code_triple('call', test_bool, '__bool__', [test])
        test_idx = gen_code_triple('ifnot', test_bool, 0)
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
                    tmp_result_bool = gen_name()
                    gen_code_triple('call', tmp_result_bool, '__bool__', [tmp_result])
                    goto_ed.append(gen_code_triple('ifnot', tmp_result_bool, 0))
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
                    tmp_result_bool = gen_name()
                    gen_code_triple('call', tmp_result_bool, '__bool__', [tmp_result])
                    goto_ed.append(gen_code_triple('if', tmp_result_bool, 0))
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
            elif type(op) is ast.In:
                gen_code_triple('call', tmp_name, '__contains__', [right, left])
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
        gen_code_triple('call', tmp_iter_name, 'iter', [it])
        test_idx = gen_code_triple('call', target, 'next', [tmp_iter_name])
        test = gen_name()
        gen_code_triple('==', test, target, ('constant', None))
        ed_idx = gen_code_triple('if', test, 0)
        for _if in node.ifs:
            if_name = gen_dfs(_if)
            if_bool = gen_name()
            gen_code_triple('call', if_bool, '__bool__', [if_name])
            gen_code_triple('ifnot', if_bool, test_idx)
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
    elif type(node) is ast.Index:
        return gen_dfs(node.value)
    elif type(node) is ast.Slice:
        tmp_name = gen_name()
        paras = [('constant', None), ('constant', None), ('constant', 1)]
        if node.lower:
            paras[0] = gen_dfs(node.lower)
        if node.upper:
            paras[1] = gen_dfs(node.upper)
        if node.step:
            paras[2] = gen_dfs(node.step)
        gen_code_triple('call', tmp_name, 'slice', paras)
        return tmp_name
    elif type(node) is ast.Subscript:
        name = gen_dfs(node.value)
        sub = gen_dfs(node.slice)
        if type(node.ctx) is ast.Load:
            tmp_name = gen_name()
            gen_code_triple('call', tmp_name, '__getitem__', [name, sub])
            return tmp_name
        elif type(node.ctx) is ast.Store:
            return (name, sub)
        elif type(node.ctx) is ast.Del:
            gen_code_triple('call', None, '__delitem__', [name, sub])
        else:
            raise Exception('Unknown ctx type')
    elif type(node) is ast.Delete:
        for item in node.targets:
            gen_dfs(item)
    elif type(node) is ast.While:
        start_idx = get_currentIdx()
        continue_stack.append(start_idx)
        test_name = gen_dfs(node.test)
        test_name_bool = gen_name()
        gen_code_triple('call', test_name_bool, '__bool__', [test_name])
        end_idx = gen_code_triple('ifnot', test_name_bool, 0)
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


def parser_main(filename):
    f = open(filename, 'r')
    code = ''.join(f.readlines())
    node = ast.parse(code)
    gen_dfs(node)
    return code_slice



