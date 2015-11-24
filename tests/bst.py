def insert(v):
    global root
    if root == None:
        root = {
            'left': None,
            'value': v,
            'right': None
        }
        return
    
    x = root
    while True:
        if x['value'] == v:
            return
        elif x['value'] > v:
            if x['left'] == None:
                x['left'] = {
                    'left': None,
                    'value': v,
                    'right': None
                }
                return
            x = x['left']
        else:
            if x['right'] == None:
                x['right'] = {
                    'left': None,
                    'value': v,
                    'right': None
                }
                return
            x = x['right']

#def size():
#    global root
#    queue = [root]
#    qsize = 1
#    num = 0
#    while qsize:
#        qsize = qsize - 1
#        now = queue[qsize]
#        if now == None:
#            continue
#        print('qsize', qsize)
#        num = num + 1
#        if qsize < len(queue):
#            queue.append(now['left'])
#        else:
#            queue[qsize] = now['left']
#        qsize = qsize + 1
#        if qsize < len(queue):
#            queue.append(now['right'])
#        else:
#            queue[qsize] = now['right']
#        qsize = qsize + 1
#        
#    return num

seed = 1
def rand():
    global seed
    seed = ((seed * 45678) % 12306 + 789011) % 12306
    return seed

root = None
for i in range(1000000):
    insert(rand())
#print(size())