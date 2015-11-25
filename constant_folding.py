import copy

import analyzer
from optimizer import UNARY_OPERATORS, BINARY_OPERATORS

def merge(states):
    ret = dict()
    for k in states[0]:
        for s in states:
            if k not in s or s[k] != states[0][k]:
                break
        else:
            ret[k] = states[0][k]
    return ret

def step(old, code, line_num):
    if code[0] in ['jmp','if','ifnot']:
        return old
    
    new = copy.copy(old)
    
    def get_value(v):
        if v[0] == 'constant':
            if type(v[1]) in [type(None), bool, int, float]:
                return (True, v[1])
            else:
                return (False, None)
        elif v[0] == 'symbol':
            if v[1] in old:
                return (True, old[v[1]])
            else:
                return (False, None)
        else:
            raise Exception("Unknown value type %s" % v)
    
    def bin_op(f):
        a_exists, a = get_value(code[2])
        b_exists, b = get_value(code[3])
        if a_exists and b_exists:
            new[code[1][1]] = f(a, b)
        else:
            new.pop(code[1][1], None)
    
    if code[0] == '=':
        exists, v = get_value(code[2])
        if not exists:
            new.pop(code[1][1], None)
        else:
            new[code[1][1]] = v
    elif code[0] == '+':
        bin_op(lambda x,y: x + y)
    elif code[0] == '-':
        bin_op(lambda x,y: x - y)
    elif code[0] == '*':
        bin_op(lambda x,y: x * y)
    elif code[0] == '/':
        bin_op(lambda x,y: x / y)
    elif code[0] == '%':
        bin_op(lambda x,y: x % y)
    elif code[0] == '|':
        bin_op(lambda x,y: x | y)
    elif code[0] == '&':
        bin_op(lambda x,y: x & y)
    elif code[0] == '^':
        bin_op(lambda x,y: x ^ y)
    elif code[0] == '<<':
        bin_op(lambda x,y: x << y)
    elif code[0] == '>>':
        bin_op(lambda x,y: x >> y)
    elif code[0] == '<':
        bin_op(lambda x,y: x < y)
    elif code[0] == '>':
        bin_op(lambda x,y: x > y)
    elif code[0] == '<=':
        bin_op(lambda x,y: x <= y)
    elif code[0] == '>=':
        bin_op(lambda x,y: x >= y)
    elif code[0] == '==':
        bin_op(lambda x,y: x == y)
    elif code[0] == '!=':
        bin_op(lambda x,y: x != y)
    elif code[0] == '~':
        exists, v = get_value(2)
        if not exists:
            new.pop(code[1][1], None)
        else:
            new[code[1][1]] = ~v
    elif code[0] == 'call':
        if code[1] is not None:
            new.pop(code[1][1], None)
        for v in code[3]:
            if v[0] == 'symbol':
                new.pop(v[1], None)
    else:
        raise Exception('Unhandled op: ' + code[0])
    
    return new

def constant_folding(funcs):
    for func_name in funcs:
        funcs[func_name]['code'] = do_folding(funcs[func_name]['code'])
    return funcs

def do_folding(src):
    (state, state_out) = analyzer.analyze_forward(src, merge, step, dict(), dict())
    
    for i in range(len(src)):
        if state[i] is None:
            continue
        
        code = list(src[i])
        if code[0] in BINARY_OPERATORS:
            if code[2][0] == 'symbol' and code[2][1] in state[i]:
                code[2] = ('constant', state[i][code[2][1]])
            if code[3][0] == 'symbol' and code[3][1] in state[i]:
                code[3] = ('constant', state[i][code[3][1]])
        elif code[0] in UNARY_OPERATORS:
            if code[2][0] == 'symbol' and code[2][1] in state[i]:
                code[2] = ('constant', state[i][code[2][1]])
        elif code[0] == 'call':
            for j in range(len(code[3])):
                if code[3][j][0] == 'symbol' and code[3][j][1] in state[i]:
                    code[3][j] = ('constant', state[i][code[3][j][1]])
        elif code[0] in ['if', 'ifnot']:
            if code[1][0] == 'symbol' and code[1][1] in state[i]:
                code[1] = ('constant', state[i][code[1][1]])
        elif code[0] not in ['jmp']:
            raise Exception('Unhandled op: ' + code[0])
        src[i] = tuple(code)
    
    return src