import copy

import analyzer
from optimizer import UNARY_OPERATORS, BINARY_OPERATORS

# Simple Type Rules
REL_OP_RULES = [
    (['bool', 'bool'], 'bool'),
    (['bool', 'int'], 'bool'),
    (['bool', 'float'], 'bool'),
    (['int', 'bool'], 'bool'),
    (['int', 'int'], 'bool'),
    (['int', 'float'], 'bool'),
    (['float', 'bool'], 'bool'),
    (['float', 'int'], 'bool'),
    (['float', 'float'], 'bool')
]

TYPE_RULES = {
    '~': [
        (['bool'], 'int'),
        (['int'], 'int')
    ],
    '+': [
        (['bool', 'bool'], 'int'),
        (['bool', 'int'], 'int'),
        (['bool', 'float'], 'float'),
        (['int', 'bool'], 'int'),
        (['int', 'int'], 'int'),
        (['int', 'float'], 'float'),
        (['float', 'bool'], 'float'),
        (['float', 'int'], 'float'),
        (['float', 'float'], 'float'),
        (['str', 'str'], 'str'),
    ],
    '-': [
        (['bool', 'bool'], 'int'),
        (['bool', 'int'], 'int'),
        (['bool', 'float'], 'float'),
        (['int', 'bool'], 'int'),
        (['int', 'int'], 'int'),
        (['int', 'float'], 'float'),
        (['float', 'bool'], 'float'),
        (['float', 'int'], 'float'),
        (['float', 'float'], 'float')
    ],
    '*': [
        (['bool', 'bool'], 'int'),
        (['bool', 'int'], 'int'),
        (['bool', 'float'], 'float'),
        (['bool', 'str'], 'str'),
        (['int', 'bool'], 'int'),
        (['int', 'int'], 'int'),
        (['int', 'float'], 'float'),
        (['int', 'str'], 'str'),
        (['float', 'bool'], 'float'),
        (['float', 'int'], 'float'),
        (['float', 'float'], 'float'),
        (['str', 'bool'], 'str'),
        (['str', 'int'], 'str')
    ],
    '/': [
        (['bool', 'bool'], 'float'),
        (['bool', 'int'], 'float'),
        (['bool', 'float'], 'float'),
        (['int', 'bool'], 'float'),
        (['int', 'int'], 'float'),
        (['int', 'float'], 'float'),
        (['float', 'bool'], 'float'),
        (['float', 'int'], 'float'),
        (['float', 'float'], 'float')
    ],
    '%': [
        (['bool', 'bool'], 'int'),
        (['bool', 'int'], 'int'),
        (['bool', 'float'], 'float'),
        (['int', 'bool'], 'int'),
        (['int', 'int'], 'int'),
        (['int', 'float'], 'float'),
        (['float', 'bool'], 'float'),
        (['float', 'int'], 'float'),
        (['float', 'float'], 'float')
    ],
    '&': [
        (['bool', 'bool'], 'bool'),
        (['bool', 'int'], 'int'),
        (['int', 'bool'], 'int'),
        (['int', 'int'], 'int'),
    ],
    '|': [
        (['bool', 'bool'], 'bool'),
        (['bool', 'int'], 'int'),
        (['int', 'bool'], 'int'),
        (['int', 'int'], 'int'),
    ],
    '^': [
        (['bool', 'bool'], 'bool'),
        (['bool', 'int'], 'int'),
        (['int', 'bool'], 'int'),
        (['int', 'int'], 'int'),
    ],
    '<<': [
        (['bool', 'bool'], 'int'),
        (['bool', 'int'], 'int'),
        (['int', 'bool'], 'int'),
        (['int', 'int'], 'int'),
    ],
    '>>': [
        (['bool', 'bool'], 'int'),
        (['bool', 'int'], 'int'),
        (['int', 'bool'], 'int'),
        (['int', 'int'], 'int'),
    ],
    '>': REL_OP_RULES,
    '<': REL_OP_RULES,
    '<=': REL_OP_RULES,
    '>=': REL_OP_RULES,
    '__iter__': [
        (['range'], 'range_iterator')
    ],
    '__next__': [
        (['range_iterator'], 'int')
    ],
    '__getitem__': [
        (['str', 'int'], 'str')
    ],
    '__len__': [
        (['str'], 'int')
    ],
    '__contains__': [
        (['str', 'str'], 'bool')
    ],
    'range': [
        (['int'], 'range'),
        (['int','int'], 'range'),
        (['int','int','int'], 'range'),
    ],
    'slice': [
        (['int'], 'slice'),
        (['int','int'], 'slice'),
        (['int','int','int'], 'slice'),
    ]
}

SIMPLE_NODES = ['none', 'bool', 'int', 'float', 'str', 'range', 'range_iterator', 'slice']

def type_inference(src):
    states, states_out = analyzer.analyze_forward(src, merge, step, ({},{}), ({},{}))
    
    def add_type(v, state):
        symbols, nodes = state
        if v[0] == 'symbol':
            infered = set()
            for node_name in symbols[v[1]]:
                if node_name in SIMPLE_NODES:
                    infered.add(node_name)
                elif 'list_values' in nodes[node_name]:
                    infered.add('list')
                elif 'set_values' in nodes[node_name]:
                    infered.add('set')
                elif 'dict_values' in nodes[node_name]:
                    infered.add('dict')
                elif 'list_iterator_owners' in nodes[node_name]:
                    infered.add('list_iterator')
                elif 'set_iterator_owners' in nodes[node_name]:
                    infered.add('set_iterator')
                elif 'dict_iterator_owners' in nodes[node_name]:
                    infered.add('dict_iterator')
            return ('symbol', v[1], infered)
        if v[0] == 'constant':
            return ('constant', v[1], {constant_type(v[1])})
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
    new_symbols = dict()
    new_nodes = dict()
    for (symbols, nodes) in states:
        for sym_name in symbols:
            if sym_name not in new_symbols:
                new_symbols[sym_name] = set()
            new_symbols[sym_name] |= symbols[sym_name]
        
        for node_name in nodes:
            node = nodes[node_name]
            if node_name not in new_nodes:
                new_node = dict()
                for col_name in node.keys():
                    new_node[col_name] = set()
                new_nodes[node_name] = new_node
            else:
                new_node = new_nodes[node_name]
            
            for col_name in node:
                new_node[col_name] |= node[col_name]
    
    return (new_symbols, new_nodes)

def step(old, code, line_num):
    if code[0] in ['if','ifnot','jmp']:
        return old
    
    def get_nodes(value, new_name):
        if value[0] == 'symbol':
            return old[0].get(value[1], set())
        if value[0] == 'constant':
            c = value[1]
            if type(c) == type(None):
                return {'none'}
            if type(c) == bool:
                return {'bool'}
            if type(c) == int:
                return {'int'}
            if type(c) == float:
                return {'float'}
            if type(c) == str:
                return {'str'}
            if c == []:
                if new_name not in new[1]:
                    new[1][new_name] = {'list_values': set()}
                return {new_name}
            if c == set():
                if new_name not in new[1]:
                    new[1][new_name] = {'set_values': set()}
                return {new_name}
            if c == {}:
                if new_name not in new[1]:
                    new[1][new_name] = {'dict_keys': set(), 'dict_values': set()}
                return {new_name}
        raise Exception('Unknown value: ' + str(value))
    
    new = merge([old]) # copy the state
    new_name = str(line_num)
    if code[0] in UNARY_OPERATORS:
        return infer_type(code[0], code[1][1], [get_nodes(code[2], new_name + '.1')], new, new_name)
    if code[0] in BINARY_OPERATORS:
        return infer_type(code[0], code[1][1], [get_nodes(code[2], new_name + '.1'), get_nodes(code[3], new_name + '.2')], new, new_name)
    if code[0] == 'call':
        args = []
        for i in range(len(code[3])):
            args.append(get_nodes(code[3][i], new_name + '.' + str(i + 1)))
        target = code[1][1] if code[1] else None
        return infer_type(code[2], target, args, new, new_name)
    raise Exception('Unknown op: ' + code[0])

def infer_type(fn, target, args, state, new_name):
    def all_has(node_names, col_name):
        ret = set()
        for node_name in node_names:
            if node_name not in SIMPLE_NODES and col_name in nodes[node_name]:
                ret.add(node_name)
        return ret
    
    def chain(node_names, *col_names):
        for col_name in col_names:
            next_node_names = set()
            for node_name in node_names:
                if node_name not in SIMPLE_NODES and col_name in nodes[node_name]:
                    next_node_names.update(nodes[node_name][col_name])
            node_names = next_node_names
        return node_names
    
    symbols, nodes = state
    ret_nodes = set()
    if fn in TYPE_RULES:
        rules = TYPE_RULES[fn]
        for (rule_args, rule_ret) in rules:
            if len(rule_args) != len(args):
                continue
            for i in range(len(rule_args)):
                if rule_args[i] not in args[i]:
                    break
            else:
                ret_nodes.add(rule_ret)
    
    if fn == '=':
        ret_nodes = args[0]
    elif fn == '+':
        llists = all_has(args[0], 'list_values')
        rlists = all_has(args[1], 'list_values')
        if llists and rlists:
            list_elems = chain(llists, 'list_values') | chain(rlists, 'list_values')
            add_node(new_name + '.list', {'list_values': list_elems})
            ret_nodes.add(new_name + '.list')
    elif fn == '*':
        if 'bool' in args[0] or 'int' in args[0]:
            rlists = all_has(args[1], 'list_values')
            if rlists:
                add_node(new_name + '.list', {'list_values': chain(rlists, 'list_values')})
                ret_nodes.add(new_name + '.list')
        if 'bool' in args[1] or 'int' in args[1]:
            llists = all_has(args[0], 'list_values')
            if llists:
                add_node(new_name + '.list', {'list_values': chain(llists, 'list_values')})
                ret_nodes.add(new_name + '.list')
    elif fn in ['==', '!=']:
        ret_nodes.add('bool')
    elif fn in ['<', '>', '<=', '>=']:
        if all_has(args[0], 'list_values') and all_has(args[1], 'list_values'):
            ret_nodes.add('bool')
        if all_has(args[0], 'set_values') and all_has(args[1], 'set_values'):
            ret_nodes.add('bool')
    elif fn == '__iter__':
        list_iterator_owners = all_has(args[0], 'list_values')
        set_iterator_owners = all_has(args[0], 'set_values')
        dict_iterator_owners = all_has(args[0], 'dict_values')
        
        if list_iterator_owners:
            add_node(new_name + '.list_iterator', {'list_iterator_owners': list_iterator_owners})
            ret_nodes.add(new_name + '.list_iterator')
        if set_iterator_owners:
            add_node(new_name + '.set_iterator', {'set_iterator_owners': set_iterator_owners})
            ret_nodes.add(new_name + '.set_iterator')
        if dict_iterator_owners:
            add_node(new_name + '.dict_iterator', {'dict_iterator_owners': dict_iterator_owners})
            ret_nodes.add(new_name + '.dict_iterator')
    elif fn == '__next__':
        ret_nodes.update(chain(args[0], 'list_iterator_owners', 'list_values'))
        ret_nodes.update(chain(args[0], 'set_iterator_owners', 'set_values'))
        ret_nodes.update(chain(args[0], 'dict_iterator_owners', 'dict_keys'))
    elif fn == '__setitem__':
        lists = all_has(args[0], 'list_values')
        if lists and 'int' in args[1]:
            for node_name in lists:
                nodes[node_name]['list_values'] |= args[2]
            ret_nodes.add('none')
                
        vlists = all_has(args[2], 'list_values')
        if lists and 'slice' in args[1] and vlists:
            vlist_values = chain(vlists, 'list_values')
            for node_name in lists:
                nodes[node_name]['list_values'] |= vlist_values
            ret_nodes.add('none')
        
        dicts = all_has(args[0], 'dict_values')
        if dicts:
            for node_name in dicts:
                nodes[node_name]['dict_keys'] |= args[1]
                nodes[node_name]['dict_values'] |= args[2]
            ret_nodes.add('none')
    elif fn == '__getitem__':
        lists = all_has(args[0], 'list_values')
        if 'int' in args[1] and lists:
            ret_nodes.update(chain(lists, 'list_values'))
        if 'slice' in args[1] and lists:
            add_node(new_name + '.list', {'list_values': chain(lists, 'list_values')})
            ret_nodes.add(new_name + '.list')
        ret_nodes.update(chain(args[0], 'dict_values'))
    elif fn == '__len__':
        if all_has(args[0], 'list_values') or all_has(args[0], 'set_values') or all_has(args[0], 'dict_values'):
            ret_nodes.add('int')
    elif fn == '__contains__':
        if all_has(args[0], 'list_values') or all_has(args[0], 'set_values') or all_has(args[0], 'dict_values'):
            ret_nodes.add('bool')
    elif fn == '__delitem__':
        if all_has(args[0], 'list_values') and 'int' in args[1] or all_has(args[0], 'dict_values'):
            ret_nodes.add('none')
    elif fn == '__bool__':
        ret_nodes.add('bool')
    elif fn == 'append':
        lists = all_has(args[0], 'list_values')
        if lists:
            for node_name in lists:
                nodes[node_name]['list_values'] |= args[1]
            ret_nodes.add('none')
    elif fn == 'add':
        sets = all_has(args[0], 'set_values')
        if sets:
            for node_name in sets:
                nodes[node_name]['set_values'] |= args[1]
            ret_nodes.add('none')
    elif fn == 'remove':
        if all_has(args[0], 'set_values'):
            ret_nodes.add('none')
    elif fn == 'pop':
        ret_nodes.update(chain(args[0], 'set_values'))
    elif fn == 'print':
        ret_nodes.add('none')
    
    if target:
        symbols[target] = ret_nodes
    return state

def constant_type(c):
    if type(c) == type(None):
        return 'none'
    if type(c) == bool:
        return 'bool'
    if type(c) == int:
        return 'int'
    if type(c) == float:
        return 'float'
    if type(c) == str:
        return 'str'
    if c == []:
        return 'list'
    if c == set():
        return 'set'
    if c == {}:
        return 'dict'
    raise Exception('Unknown constant: ' + str(c))

def print_state(state):
    symbols, nodes = state
    print('Symbols:')
    for sym in symbols:
        print('\t', sym, ':', symbols[sym])
    print('Nodes:')
    for node in nodes:
        print('\t', node, ':', nodes[node])

if __name__ == '__main__':
    print(infer_type('+', [('list', ('int',)), ('list', ('any',))]))
    print(infer_type('+', [('list', ('int',)), ('list', ('list', ('str',)))]))
    print(infer_type('~', [('dynamic',)]))
    print(infer_type('+', [('dynamic',), ('int',)]))
    print(infer_type('+', [('dynamic',), ('list', ('int',))]))
    print(infer_type('append', [('list', ('int',)), ('int',)]))