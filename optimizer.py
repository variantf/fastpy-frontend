import copy

import analyzer

BINARY_OPERATORS = ['+','-','*','/','%','>','<','>=','<=','&','|','^','<<','>>','==']
UNARY_OPERATORS = ['=', '~']

def remove_lines(src, to_remove):
    assert to_remove == sorted(to_remove)
    next_remove = 0
    next_index = 0
    new_index = []
    for i in range(len(src)):
        if next_remove < len(to_remove) and to_remove[next_remove] == i:
            next_remove += 1
            new_index.append(next_index)
        else:
            new_index.append(next_index)
            next_index += 1
    new_index.append(next_index)
        
    new_src = []
    next_remove = 0
    for i in range(len(src)):
        if next_remove < len(to_remove) and to_remove[next_remove] == i:
            next_remove += 1
        else:
            code = src[i]
            if code[0] == 'jmp':
                new_src.append(('jmp', new_index[code[1]]))
            elif code[0] in ['if', 'ifnot']:
                new_src.append((code[0], code[1], new_index[code[2]]))
            else:
                new_src.append(code)
    return new_src

def constant_folding(src):
    def merge(states):
        ret = dict()
        for k in states[0]:
            for s in states:
                if k not in s or s[k] != states[0][k]:
                    break
            else:
                ret[k] = states[0][k]
        return ret
    
    def step(old, code):
        if code[0] in ['jmp','if','ifnot']:
            return old
        
        new = copy.copy(old)
        
        def get_value(v):
            if v[0] == 'constant':
                return (True, v[1])
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
                    c = state[i][code[3][j][1]]
                    # Must not be used as left value
                    if type(c) in [type(None), bool, int, float, str]:
                        code[3][j] = ('constant', c)
        elif code[0] in ['if', 'ifnot']:
            if code[1][0] == 'symbol' and code[1][1] in state[i]:
                code[1] = ('constant', state[i][code[1][1]])
        elif code[0] not in ['jmp']:
            raise Exception('Unhandled op: ' + code[0])
        src[i] = tuple(code)
    
    return src

def dead_code(src):
    def merge(states):
        return any(states)
    def step(old_state,code):
        return old_state
    
    (state, state_out) = analyzer.analyze_forward(src, merge, step, True, False)
    
    to_remove = []
    for i in range(len(src)):
        if not state[i]:
            to_remove.append(i)
            continue
        code = src[i]
        if analyzer.must_take(code):
            src[i] = code = ('jmp', code[2])
        if analyzer.must_not_take(code):
            to_remove.append(i)
            continue
    
    return remove_lines(src, to_remove)

def unused_variable(src):
    def merge(states):
        merged = set()
        for s in states:
            merged.update(s)
        return merged
    
    def step(state, code):
        new = copy.copy(state)
        if code[0] in BINARY_OPERATORS:
            if code[1][1] in new:
                new.remove(code[1][1])
                if code[2][0] == 'symbol':
                    new.add(code[2][1])
                if code[3][0] == 'symbol':
                    new.add(code[3][1])
        elif code[0] in UNARY_OPERATORS:
            if code[1][1] in new:
                new.remove(code[1][1])
                if code[2][0] == 'symbol':
                    new.add(code[2][1])
        elif code[0] == 'call':
            if code[1] is not None:
                new.discard(code[1][1])
            for arg in code[3]:
                if arg[0] == 'symbol':
                    new.add(arg[1])
        elif code[0] in ['if', 'ifnot']:
            if code[1][0] == 'symbol':
                new.add(code[1][1])
        elif code[0] != 'jmp':
            raise Exception("Unhandled op: " + code[0])
        return new
    
    states, states_out = analyzer.analyze_backward(src, merge, step, set())
    
    to_remove = []
    for i in range(len(src)):
        code = src[i]
        if code[0] in BINARY_OPERATORS:
            if code[1][1] not in states[i]:
                to_remove.append(i)
        elif code[0] in UNARY_OPERATORS:
            if code[1][1] not in states[i]:
                to_remove.append(i)
        elif code[0] == 'call':
            if code[1] is not None and code[1][1] not in states[i]:
                code = list(code)
                code[1] = None
                src[i] = tuple(code)
        elif code[0] not in ['jmp','if','ifnot']:
            raise Exception("Unhandled op: " + code[0])
    
    return remove_lines(src, to_remove)

def successive_jump(src):
    def trace_jump(start, now):
        jumped = {start}
        while now not in jumped:
            if now == len(src):
                return now
            if src[now][0] == 'jmp':
                jumped.add(now)
                now = src[now][1]
            else:
                return now
        
        # encountered dead loop
        if (start + 1) in jumped:
            return start + 1 # to better optimize out
        else:
            return start
    
    for i in range(len(src)):
        code = src[i]
        if code[0] in ['if', 'ifnot']:
            src[i] = (code[0], code[1], trace_jump(i, code[2]))
        elif code[0] == 'jmp':
            src[i] = ('jmp', trace_jump(i, code[1]))
    return src

def jump_next(src):
    to_remove = True
    while to_remove:
        to_remove = []
        for i in range(len(src)):
            code = src[i]
            if code[0] in ['if', 'ifnot']:
                if code[2] == i+1:
                    to_remove.append(i)
            elif code[0] == 'jmp':
                if code[1] == i+1:
                    to_remove.append(i)
        src = remove_lines(src, to_remove)
    return src


with open('triple_code', 'r') as f:
    src = [eval(l) for l in f.readlines()]

src = constant_folding(src)
src = dead_code(src)
src = unused_variable(src)
src = successive_jump(src)
src = jump_next(src)

for l in src:
    print(l)