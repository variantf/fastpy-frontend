"""
def f(x):
    if x == 0:
        return 1
    return x * f(x - 1)

print(f(3))
"""

x = 3
def f():
    return x
def g():
    x = 4
    return x + 5
def h():
    global x
    x = 4
    return x + 5
def i(x):
    x = 4
    return x + 5