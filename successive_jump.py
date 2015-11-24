def successive_jump(funcs):
    for func_name in funcs:
        funcs[func_name]['code'] = do_successive_jump(funcs[func_name]['code'])
    return funcs

def do_successive_jump(src):
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