import math

m = 10
n_max = 10

count_misses = 0
count_pdt_misses = 0

for n11 in range(1,n_max):
    for n10 in range(1,n_max):
        for n00 in range(1,n_max):
            for n01 in range(1,n_max):
                for i in range(m+1):
                    a = math.pow((float)(n11+2*(m-i))/(float)(n11+n01+2*m),n11+2*(m-i))
                    b = math.pow((float)(n01+2*i)/(float)(n11+n01+2*m),n01+2*i)
                    c = math.pow((float)(n00)/(float)(n10+n00),n00)
                    d = math.pow((float)(n10)/(float)(n10+n00),n10)
                    f1 = a*b*c*d

                    a = math.pow((float)(n11)/(float)(n11+n01),n11)
                    b = math.pow((float)(n01)/(float)(n11+n01),n01)
                    c = math.pow((float)(n00+2*i)/(float)(n10+n00+2*m),n00+2*i)
                    d = math.pow((float)(n10+2*(m-i))/(float)(n10+n00+2*m),n10+2*(m-i))
                    f2 = a*b*c*d

                    a = math.pow((float)(n11+(m-i))/(float)(n11+n01+m),n11+(m-i))
                    b = math.pow((float)(n01+i)/(float)(n11+n01+m),n01+i)
                    c = math.pow((float)(n00+i)/(float)(n10+n00+m),n00+i)
                    d = math.pow((float)(n10+(m-i))/(float)(n10+n00+m),n10+(m-i))
                    f = a*b*c*d

                    if round(f1,7) < round(f,7) and round(f2,7) < round(f,7):
                        count_misses += 1
                        print "miss, params = ",n11,n01,n00,n10,i
                        print "f1 = ",f1," f2 = ",f2," f = ",f

                    if round(f1*f2,7) < round(f*f,7):
                        count_pdt_misses += 1
                        print "pdt miss, params = ",n11,n01,n00,n10,i
                        print "f1*f2 = ",f1*f2," f*f = ",f*f
                        

print "n_max = ",n_max
print "Misses = ", count_misses
print "Pdt Misses = ", count_pdt_misses
