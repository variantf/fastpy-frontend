BINARY_OPERATORS = ['+','-','*','/','%','>','<','>=','<=','&','|','^','<<','>>','==','!=']
UNARY_OPERATORS = ['=', '~']

def remove_lines(src, to_remove):
    assert to_remove == sorted(to_remove)
    next_remove = 0
    next_index = 0
    new_index = []
    for i in range(len(src)):
        if next_remove < len(to_remove) and to_remove[next_remove] == i:
            next_remove += 1
            new_index.append(next_index)
        else:
            new_index.append(next_index)
            next_index += 1
    new_index.append(next_index)
        
    new_src = []
    next_remove = 0
    for i in range(len(src)):
        if next_remove < len(to_remove) and to_remove[next_remove] == i:
            next_remove += 1
        else:
            code = src[i]
            if code[0] == 'jmp':
                new_src.append(('jmp', new_index[code[1]]))
            elif code[0] in ['if', 'ifnot']:
                new_src.append((code[0], code[1], new_index[code[2]]))
            else:
                new_src.append(code)
    return new_src

