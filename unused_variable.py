import copy

import analyzer
from optimizer import UNARY_OPERATORS, BINARY_OPERATORS, remove_lines

def merge(states):
    merged = set()
    for s in states:
        merged.update(s)
    return merged

def step(state, code, line_num):
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

def unused_variable(src):
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

