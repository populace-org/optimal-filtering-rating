import math
import matplotlib.pyplot as plt


def LHS(P, m, k):
    return (math.pow(1.0 - P, k) / math.pow(P, m-k-1))


def RHS(p, m, k):
    return (math.pow(1.0 - p, k+1) / math.pow(p, m-k))

m = 10

P_range = [float(i) / 100.0 for i in xrange(80, 100)]
p_range = [float(i) / 100.0 for i in xrange(60, 80)]
for k in range(0, m + 1):
    x = [LHS(P, m, k) for P in P_range]
    y = [RHS(p, m, k) for p in p_range]
    plt.figure()
    plt.plot(x, y, 'o')
    plt.plot(x, x)
    plt.savefig('p vs P for '+str(k))
    plt.close()


P = 1.0
p_range = [float(i) / 100.0 for i in xrange(80, 100)]

for k in range(0, m + 1):
    y = [LHS(P, m, k) - RHS(p, m, k) for p in p_range]
    plt.figure()
    plt.plot(p_range, y)
    plt.savefig('LHS - RHS vs p for '+str(k))
    plt.close()
