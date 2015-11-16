n = None
b = True
i = 12
f = 12.456
s = 'str'
l = [n, b]
st = {1,2,3}
d = {1:2, 3:4, 5:6}

print(b + i)
print(i + f)
print(f + b)
print(f + f)
print(b - i)
print(i - f)
print(f - b)
print(f - f)
print(s * b)
print(i * l)
print(f % i)
print(i % b)
print(1 < 2)
print(3.0 < False)
print(45 >= 36)
print(False < 38)
print(1 == 2)
print(True == False)
print(3.0 != 'str')
print(None != {})

print(i ^ i)
print(b & b)
print(~b)
print(~i)
print(i | b)
print(b | i)
print(i << b)
print(b >> b)
print(b >> i)
print(not 1)
print(not True)

for i in st:
    print(i)
    print('\n')

for i in d:
    print(i)
    print(d[i])
    print('\n')
