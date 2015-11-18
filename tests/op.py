n = None
b = True
i = 12
f = 12.456
s = 'str'
l = [f, s, i]
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
print(not [])
print(not True)

#del l[0]
#st.remove(2)
#st.pop()
#st.add(3)
l.append(456)
d[1] = 456
#del d[1]
#print(1 in l)
#print(2 in st)
#print(3 in d)
#print(l[:1])
#print(l[:-1])

print(len(l))
print(len(s))
print(len(d))
print(len(st))
print(bool(st))

for i in l:
    print(i)
    print('\n')

for i in st:
    print(i)
    print('\n')

for i in d:
    print(i)
    print(d[i])
    print('\n')
