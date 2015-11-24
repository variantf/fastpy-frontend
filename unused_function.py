def unused_function(funcs):
    func_names = funcs.keys()
    queue = ['_main$']
    used = {'_main$'}
    while queue:
        func_name = queue.pop()
        for code in funcs[func_name]['code']:
            if code[0] == 'call' and code[2] in func_names and code[2] not in used:
                queue.append(code[2])
                used.add(code[2])
    return {func_name: funcs[func_name] for func_name in used}