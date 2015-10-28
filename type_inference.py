import copy

import analyzer
from optimizer import UNARY_OPERATORS, BINARY_OPERATORS

REL_OP_RULES = [
    ([(('bool',),), (('bool',),)], ('bool',)),
    ([(('bool',),), (('int',),)], ('bool',)),
    ([(('bool',),), (('float',),)], ('bool',)),
    ([(('int',),), (('bool',),)], ('bool',)),
    ([(('int',),), (('int',),)], ('bool',)),
    ([(('int',),), (('float',),)], ('bool',)),
    ([(('float',),), (('bool',),)], ('bool',)),
    ([(('float',),), (('int',),)], ('bool',)),
    ([(('float',),), (('float',),)], ('bool',)),
    ([(('list', 'T'),), (('list', 'E'),)], ('bool',)),
    ([(('set', 'T'),), (('set', 'E'),)], ('bool',)),
    ([(('dict', 'T', 'E'),), (('dict', 'U', 'V'),)], ('bool',)),
]

TYPE_RULES = {
    '=': [
        ([('E',)], 'E')
    ],
    '~': [
        ([(('bool',),)], ('int',)),
        ([(('int',),)], ('int',))
    ],
    '+': [
        ([(('bool',),), (('bool',),)], ('int',)),
        ([(('bool',),), (('int',),)], ('int',)),
        ([(('bool',),), (('float',),)], ('float',)),
        ([(('int',),), (('bool',),)], ('int',)),
        ([(('int',),), (('int',),)], ('int',)),
        ([(('int',),), (('float',),)], ('float',)),
        ([(('float',),), (('bool',),)], ('float',)),
        ([(('float',),), (('int',),)], ('float',)),
        ([(('float',),), (('float',),)], ('float',)),
        ([(('str',),), (('str',),)], ('str',)),
        ([(('list', 'T'),), (('list', 'E'),)], ('list', ('$merge', 'T', 'E')))
    ],
    '-': [
        ([(('bool',),), (('bool',),)], ('int',)),
        ([(('bool',),), (('int',),)], ('int',)),
        ([(('bool',),), (('float',),)], ('float',)),
        ([(('int',),), (('bool',),)], ('int',)),
        ([(('int',),), (('int',),)], ('int',)),
        ([(('int',),), (('float',),)], ('float',)),
        ([(('float',),), (('bool',),)], ('float',)),
        ([(('float',),), (('int',),)], ('float',)),
        ([(('float',),), (('float',),)], ('float',))
    ],
    '*': [
        ([(('bool',),), (('bool',),)], ('int',)),
        ([(('bool',),), (('int',),)], ('int',)),
        ([(('bool',),), (('float',),)], ('float',)),
        ([(('bool',),), (('str',),)], ('str',)),
        ([(('bool',),), (('list', 'E'),)], ('list', 'E')),
        ([(('int',),), (('bool',),)], ('int',)),
        ([(('int',),), (('int',),)], ('int',)),
        ([(('int',),), (('float',),)], ('float',)),
        ([(('int',),), (('str',),)], ('str',)),
        ([(('int',),), (('list', 'E'),)], ('list', 'E')),
        ([(('float',),), (('bool',),)], ('float',)),
        ([(('float',),), (('int',),)], ('float',)),
        ([(('float',),), (('float',),)], ('float',)),
        ([(('str',),), (('bool',),)], ('str',)),
        ([(('list', 'E'),), (('bool',),)], ('list', 'E')),
        ([(('str',),), (('int',),)], ('str',)),
        ([(('list', 'E'),), (('int',),)], ('list', 'E'))
    ],
    '/': [
        ([(('bool',),), (('bool',),)], ('float',)),
        ([(('bool',),), (('int',),)], ('float',)),
        ([(('bool',),), (('float',),)], ('float',)),
        ([(('int',),), (('bool',),)], ('float',)),
        ([(('int',),), (('int',),)], ('float',)),
        ([(('int',),), (('float',),)], ('float',)),
        ([(('float',),), (('bool',),)], ('float',)),
        ([(('float',),), (('int',),)], ('float',)),
        ([(('float',),), (('float',),)], ('float',))
    ],
    '%': [
        ([(('bool',),), (('bool',),)], ('int',)),
        ([(('bool',),), (('int',),)], ('int',)),
        ([(('bool',),), (('float',),)], ('float',)),
        ([(('int',),), (('bool',),)], ('int',)),
        ([(('int',),), (('int',),)], ('int',)),
        ([(('int',),), (('float',),)], ('float',)),
        ([(('float',),), (('bool',),)], ('float',)),
        ([(('float',),), (('int',),)], ('float',)),
        ([(('float',),), (('float',),)], ('float',))
    ],
    '==': [
        ([('T',), ('E',)], ('bool',)),
    ],
    '>': REL_OP_RULES,
    '<': REL_OP_RULES,
    '<=': REL_OP_RULES,
    '>=': REL_OP_RULES,
    'append': [
        ([(('list', 'T'), ('list', ('$merge', 'T', 'E'))), 'E'], ('none',))
    ],
    'add': [
        ([(('set', 'T'), ('set', ('$merge', 'T', 'E'))), 'E'], ('none',))
    ],
    'range': [
        ([(('int',),)], ('range',)),
        ([(('int',),),(('int',),)], ('range',)),
        ([(('int',),),(('int',),),(('int',),)], ('range',)),
    ],
    '__iter__': [
        ([(('range',),)], ('range_iterator',)),
    ],
    '__next__': [
        ([(('range_iterator',),)], ('int',)),
    ],
    '__setitem__': [
        ([(('list', 'T'), ('list', ('$merge', 'T', 'E'))), (('int',),), ('E',)], ('none',)),
        ([(('list', 'T'), ('list', ('$merge', 'T', 'E'))), (('slice',),), (('list', 'E'),)], ('none',)),
        ([(('dict', 'K', 'V'), ('dict', ('$merge', 'K', 'T'), ('$merge', 'V', 'E'))), ('T',), ('E',)], ('none',)),
    ],
    '__getitem__': [
        ([(('str',),), (('int',),)], ('str',)),
        ([(('list', 'T'),), (('int',),)], 'T'),
        ([(('list', 'T'),), (('slice',),)], ('list', 'T')),
        ([(('dict', 'K', 'V'),), ('T',)], 'V'),
    ],
    '__len__': [
        ([(('str',),)], ('int',)),
        ([(('list', 'T'),)], ('int',)),
        ([(('set', 'T'),)], ('int',)),
        ([(('dict', 'T', 'E'),)], ('int',)),
    ],
}

def type_inference(src):
    states, states_out = analyzer.analyze_forward(src, merge, step, {}, {})
    
    def add_type(v, state):
        if v[0] == 'symbol':
            return ('symbol', v[1], state[v[1]])
        if v[0] == 'constant':
            return ('constant', v[1], constant_type(v[1]))
        raise Exception("Unknown value: " + str(v))
    
    for i in range(len(src)):
        code = list(src[i])
        if code[0] in UNARY_OPERATORS:
            code[1] = add_type(code[1], states_out[i])
            code[2] = add_type(code[2], states[i])
        elif code[0] in BINARY_OPERATORS:
            code[1] = add_type(code[1], states_out[i])
            code[2] = add_type(code[2], states[i])
            code[3] = add_type(code[3], states[i])
        elif code[0] == 'call':
            if code[1] is not None:
                code[1] = add_type(code[1], states_out[i])
            code[3] = [add_type(x, states[i]) for x in code[3]]
        elif code[0] in ['if', 'ifnot']:
            code[1] = add_type(code[1], states[i])
        elif code[0] != 'jmp':
            raise Exception('Unhandled op: ' + code[0])
        src[i] = tuple(code)
    
    return src

def merge(states):
    variables = set()
    for s in states:
        variables.update(s.keys())
    
    ret = dict()
    for var in variables:
        the_type = ('any',)
        for s in states:
            the_type = merge_type(the_type, s.get(var, ('dynamic',)))
        ret[var] = the_type
    return ret

def step(old, code):
    if code[0] in ['if','ifnot','jmp']:
        return old
    
    def get_type(v):
        if v[0] == 'symbol':
            return old.get(v[1], ('any',))
        if v[0] == 'constant':
            return constant_type(v[1])
        raise Exception('Unknown value: ' + str(v))
    
    def set_type(v, t):
        if v[0] == 'symbol':
            new[v[1]] = t
    
    new = copy.copy(old)
    if code[0] in UNARY_OPERATORS:
        infered = infer_type(code[0], [get_type(code[2])])
        set_type(code[2], infered[0])
        set_type(code[1], infered[1])
    elif code[0] in BINARY_OPERATORS:
        infered = infer_type(code[0], [get_type(code[2]), get_type(code[3])])
        set_type(code[2], infered[0])
        set_type(code[3], infered[1])
        set_type(code[1], infered[2])
    elif code[0] == 'call':
        infered = infer_type(code[2], [get_type(arg) for arg in code[3]])
        for i in range(len(code[3])):
            set_type(code[3][i], infered[i])
        if code[1] is not None:
            set_type(code[1], infered[len(code[3])])
    else:
        raise Exception('Unknown op: ' + code[0])
    return new

def infer_type(fn, args):
    for arg in args:
        if arg[0] == 'any':
            raise Exception('Use before assignment')
    
    rules = TYPE_RULES[fn]
    infered = [('any',) for i in range(len(args) + 1)]
    matched = False
    for rule in rules:
        arg_tpl = rule[0]
        ret_tpl = rule[1]
        if len(arg_tpl) != len(args):
            continue
        
        params = {}
        all_matched = True
        for i in range(len(args)):
            arg_before = arg_tpl[i][0]
            if not pattern_match(arg_before, args[i], params):
                all_matched = False
                break
        if not all_matched:
            continue
        
        matched = True
        ret_type = pattern_apply(ret_tpl, params)
        infered[len(args)] = merge_type(infered[len(args)], ret_type)
        for i in range(len(args)):
            arg_after = arg_tpl[i][1] if len(arg_tpl[i]) == 2 else arg_tpl[i][0]
            arg_type = pattern_apply(arg_after, params)
            infered[i] = merge_type(infered[i], arg_type)
    
    if not matched:
        raise Exception('Type error for ' + fn + ' args: ' + str(args))
    return infered

def merge_type(ta, tb):
    if ta[0] == 'dynamic' or tb[0] == 'dynamic':
        return ta
    if ta[0] == 'any':
        return tb
    if tb[0] == 'any':
        return ta
    if ta[0] != tb[0]:
        return ('dynamic',)
    if ta[0] in ['none','bool','int','float','str','range','range_iterator','slice']:
        return ta
    if ta[0] in ['list', 'set']:
        return (ta[0], merge_type(ta[1],tb[1]))
    if ta[0] == 'dict':
        return ('dict', merge_type(ta[1], tb[1]), merge_type(ta[2], tb[2]))
    raise Exception('Unknown type: ' + ta[0])

def constant_type(c):
    if type(c) == type(None):
        return ('none',)
    if type(c) == bool:
        return ('bool',)
    if type(c) == int:
        return ('int',)
    if type(c) == float:
        return ('float',)
    if type(c) == str:
        return ('str',)
    if c == []:
        return ('list', ('any',))
    if c == set():
        return ('set', ('any',))
    if c == {}:
        return ('dict', ('any',), ('any',))
    raise Exception('Unknown constant: ' + str(c))

def pattern_match(template, value, params):
    #print('pattern_match', template, value)
    if type(template) == str:
        params[template] = value
        return True
    if value[0] == 'dynamic':
        for i in range(1, len(template)):
            assert pattern_match(template[i], ('dynamic',), params)
        return True
    if len(template) != len(value) or template[0] != value[0]:
        return False
    for i in range(1, len(template)):
        if not pattern_match(template[i], value[i], params):
            return False
    return True

def pattern_apply(template, params):
    if type(template) == str:
        return params[template]
    if template[0] == '$merge':
        return merge_type(pattern_apply(template[1], params), pattern_apply(template[2], params))
    ret = [template[0]]
    for i in range(1, len(template)):
        ret.append(pattern_apply(template[i], params))
    return tuple(ret)

if __name__ == '__main__':
    print(infer_type('+', [('list', ('int',)), ('list', ('any',))]))
    print(infer_type('+', [('list', ('int',)), ('list', ('list', ('str',)))]))
    print(infer_type('~', [('dynamic',)]))
    print(infer_type('+', [('dynamic',), ('int',)]))
    print(infer_type('+', [('dynamic',), ('list', ('int',))]))
    print(infer_type('append', [('list', ('int',)), ('int',)]))