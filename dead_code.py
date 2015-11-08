import analyzer
from optimizer import remove_lines

def dead_code(src):
    def merge(states):
        return any(states)
    def step(old_state,code,line_num):
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

