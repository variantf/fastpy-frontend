import copy

import analyzer

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
        if code[0] in ['+','-','*','/','>','<','>=','<=','&','|','^','<<','>>','==']:
            if code[2][0] == 'symbol' and code[2][1] in state[i]:
                code[2] = ('constant', state[i][code[2][1]])
            if code[3][0] == 'symbol' and code[3][1] in state[i]:
                code[3] = ('constant', state[i][code[3][1]])
        elif code[0] in ['=', '~']:
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
    
    should_remove = []
    for i in range(len(src)):
        if not state[i]:
            should_remove.append(True)
            continue
        code = src[i]
        if analyzer.must_take(code):
            src[i] = code = ('jmp', code[2])
        if analyzer.must_not_take(code):
            should_remove.append(True)
            continue
        if code[0] == 'jmp' and code[1] == i + 1:
            should_remove.append(True)
            continue
        should_remove.append(False)
    
    while any(should_remove):
        next_index = 0
        new_index = []
        for i in range(len(src)):
            if should_remove[i]:
                new_index.append(next_index)
            else:
                new_index.append(next_index)
                next_index += 1
    
        new_src = []
        for i in range(len(src)):
            if not should_remove[i]:
                code = src[i]
                if code[0] == 'jmp':
                    new_src.append(('jmp', new_index[code[1]]))
                elif code[0] in ['if', 'ifnot']:
                    new_src.append((code[0], code[1], new_index[code[2]]))
                else:
                    new_src.append(code)
        
        src = new_src
        should_remove = []
        for i in range(len(src)):
            code = src[i]
            if code[0] == 'jmp' and code[1] == i + 1:
                should_remove.append(True)
                continue
            should_remove.append(False)
    return src

with open('triple_code', 'r') as f:
    src = [eval(l) for l in f.readlines()]

src = constant_folding(src)
src = dead_code(src)

for l in src:
    print(l)