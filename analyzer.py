def analyze_forward(src, merge_func, step_func, init_state):
    """Forward analyzing
    merge_func: ([states]) -> state
        Must not change states
    step_func: (state_old, code) -> state_new
        Must not change state_old
    init_state: the state before the whole program
    """
    state_in = [None for i in range(len(src) + 1)]
    state_out = [None for i in range(len(src))]
    
    pre = [[] for i in range(len(src) + 1)]
    for i in range(len(src)):
        if src[i][0] == 'jmp':
            pre[src[i][1]].append(i)
        elif src[i][0] in ['if', 'ifnot']:
            pre[src[i][2]].append(i)
            pre[i+1].append(i)
        else:
            pre[i+1].append(i)
    
    updated = [0]
    while updated:
        line = updated.pop()
        from_states = [state_out[i] for i in pre[line]]
        if line == 0:
            from_states.append(init_state)
        from_states = [s for s in from_states if s is not None]
        
        if len(from_states) == 0:
            raise Exception("Update from 0 states")
        elif len(from_states) == 1:
            state_in[line] = from_states[0]
        else:
            state_in[line] = merge_func(from_states)
        
        if line == len(src):
            continue
        
        code = src[line]
        if code[0] in ['jmp', 'if', 'ifnot']:
            new_state = state_in[line]
        else:
            new_state = step_func(state_in[line], code)
        if new_state == state_out[line]:
            continue
        state_out[line] = new_state
        
        if code[0] == 'jmp':
            updated.append(code[1])
        elif code[0] in ['if', 'ifnot']:
            updated.append(line + 1)
            updated.append(code[2])
        else:
            updated.append(line + 1)
    
    return (state_in, state_out)