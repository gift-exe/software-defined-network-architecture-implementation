d = {}
d.setdefault(1, {})

print(d)
d[1][0] = 1
print(d)

import mininet
from ryu.app import simple_switch_13


s = set()

l = [1, 2, 4]

for d in l:
    s.add(d)
print(s)