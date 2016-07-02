import math
import matplotlib.pyplot as plt

c = 100

count = 0
x = []
y = []
z1 = []

count = 0
count_misses = 0
count_correct = 0
for b in range(1,c):
    for a in range(b+1,c+1):
        x.append(count)
        count += 1
        z1.append(1)
        n1 = pow(a,a)
        n2 = pow(c-a,c-a)
        d1 = pow(b,b)
        d2 = pow(c-b,c-b)
        #y.append((float)(n1*n2)/(float)(d1*d2))
        if (float)(n1*n2)/(float)(d1*d2) < 1.0:
            if (float)(n1*n2)/(float)(d1*d2) <= 0: print b,a
            y.append((float)(n1*n2)/(float)(d1*d2))
            count_misses += 1
        elif (float)(n1*n2)/(float)(d1*d2) > 1.0:
            y.append(1.5)
            count_correct += 1
        else:
            y.append(1.0)
            count_correct += 1

print "misses = ",count_misses," hits = ",count_correct

plt.figure()
plt.plot(x,y)
plt.plot(x,z1)
#plt.legend(['P1','Base = 1'])
plt.savefig('filterflip.png')
plt.show()
plt.close()
