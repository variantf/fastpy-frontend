def must_take(code):
    if code[0] == 'if' and code[1][0] == 'constant' and code[1][1]:
        return True
    if code[0] == 'ifnot' and code[1][0] == 'constant' and not code[1][1]:
        return True
    return False

def must_not_take(code):
    if code[0] == 'if' and code[1][0] == 'constant' and not code[1][1]:
        return True
    if code[0] == 'ifnot' and code[1][0] == 'constant' and code[1][1]:
        return True
    return False
    
def analyze_forward(src, merge_func, step_func, init_state, empty_state):
    """Forward analyzing
    merge_func: ([states]) -> state
        Must not change states
    step_func: (state_old, code) -> state_new
        Must not change state_old
    init_state: the state before the whole program
    empty_state
    """
    state_in = [empty_state for i in range(len(src))]
    state_out = [empty_state for i in range(len(src))]
    
    pre = [[] for i in range(len(src) + 1)]
    succ = [[] for i in range(len(src))]
    for i in range(len(src)):
        if src[i][0] == 'jmp':
            pre[src[i][1]].append(i)
            succ[i] = [src[i][1]]
        elif src[i][0] in ['if', 'ifnot']:
            if not must_not_take(src[i]):
                pre[src[i][2]].append(i)
                succ[i].append(src[i][2])
            if not must_take(src[i]):
                pre[i+1].append(i)
                succ[i] = [i+1]
        else:
            pre[i+1].append(i)
            succ[i] = [i+1]
    
    updated = set(range(len(src)))
    while updated:
        line = updated.pop()
        if line == len(src):
            continue
        
        from_states = [state_out[i] for i in pre[line]]
        if line == 0:
            from_states.append(init_state)
        
        if len(from_states) == 0:
            pass
        elif len(from_states) == 1:
            state_in[line] = from_states[0]
        else:
            state_in[line] = merge_func(from_states)
        
        new_state = step_func(state_in[line], src[line])
        if new_state == state_out[line]:
            continue
        state_out[line] = new_state
        
        updated.update(succ[line])
    
    return (state_in, state_out)

def analyze_backward(src, merge_func, step_func, empty_state):
    """Backward analyzing
    merge_func: ([states]) -> state
        Must not change states
    step_func: (state_old, code) -> state_new
        Must not change state_old
    empty_state
    """
    state_in = [empty_state for i in range(len(src))]
    state_out = [empty_state for i in range(len(src) + 1)]
    
    pre = [[] for i in range(len(src) + 1)]
    succ = [[] for i in range(len(src))]
    for i in range(len(src)):
        if src[i][0] == 'jmp':
            pre[src[i][1]].append(i)
            succ[i] = [src[i][1]]
        elif src[i][0] in ['if', 'ifnot']:
            if not must_not_take(src[i]):
                pre[src[i][2]].append(i)
                succ[i].append(src[i][2])
            if not must_take(src[i]):
                pre[i+1].append(i)
                succ[i] = [i+1]
        else:
            pre[i+1].append(i)
            succ[i] = [i+1]
    
    updated = set(range(len(src)))
    while updated:
        line = updated.pop()
        from_states = [state_out[i] for i in succ[line]]
        
        if len(from_states) == 0:
            pass
        elif len(from_states) == 1:
            state_in[line] = from_states[0]
        else:
            state_in[line] = merge_func(from_states)
        
        new_state = step_func(state_in[line], src[line])
        if new_state == state_out[line]:
            continue
        state_out[line] = new_state
        
        updated.update(pre[line])
    
    return (state_in, state_out)