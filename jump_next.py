from optimizer import remove_lines
def jump_next(funcs):
    for func_name in funcs:
        funcs[func_name]['code'] = do_jump_next(funcs[func_name]['code'])
    return funcs
    
def do_jump_next(src):
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
