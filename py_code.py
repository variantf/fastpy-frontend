l = [1,2,3]
l.append(4)
s = {1,2,3}
s = {a for a in range(10)}
d = {1:1, 2:2, 3:3}
d = {a:b for a in range(10) if a % 2 == 0 if a % 3 == 0 for b in range(10)}
d = {}
a = 1.0
b = a + 5
c = 'str'
d = a + b - len(c)
e = None

if a > b:
	a = 1
else:
	a = 2

if 15 > d > 10 and c[1]:
	a = 'def'

for x in range(5):
	i = 1
	while i < 10:
		i = i + 1
		break
	else:
		j = 2

	for y in range(10):
		break
	else:
	 	z = 3

d = b = [a for x in range(10)]
