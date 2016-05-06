a = [1, '1']
a[2] = a[1]
print(a[2] + a[1])



a = [1, '1']
if len(a[2]) == 1:
    a[1] = '1'
print(a[2] + '1')


def max_num(a,b):
    if a > b:
        return a;
    return b;

print(max_num(1,2))

print(max_num(1.0, 2.0))
