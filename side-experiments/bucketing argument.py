import math
import matplotlib.pyplot as plt

max_per_bucket = 10
m = 2

n1 = {]
n0 = {}

for j1 in range(m+1):
    for j2 in range(m+1):
        for j3 in range(m+1):
            for j4 in range(m+1):
                for j5 in range(m+1):
                    for j6 in range(m+1):
                        if j1+j2+j3 == 0 or j4+j5+j6 == 0:
                            continue
                        else:
                            n1[0] = j1
                            n1[1] = j2
                            n1[2] = j3
                            n0[0] = j4
                            n0[1] = j5
                            n0[2] = j6

plt.figure()
plt.plot(x,y)

plt.savefig('bucketingarg.png')
plt.show()
plt.close()
