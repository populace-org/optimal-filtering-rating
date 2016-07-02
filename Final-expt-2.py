import math
from collections import defaultdict
#import matplotlib.pyplot as matplotlib.pyplot
from matplotlib.pyplot import *
import copy
import time
import random


def nchoosek(n, k):
    return reduce(lambda a, b: a*(n-b)/(b+1), xrange(k), 1)

random.seed()

##############################################################
#####Lattice parameters
##############################################################

'''R = 3 #number of ratings - 1,2,...,R
m = 3 #num qns per item'''

#keys of following dictionaries are *tuples*, NOT *lists*
parents = defaultdict(list)  # stores parents of node
children = defaultdict(list)  # stores children of node
depth = {}  # stores the depth of a node
nodes_in_depth = defaultdict(list)  # stores the nodes at depth d
num_bucketings = 0 #number of valid partial order preserving bucketings = [] #the set of valid partial order preserving bucketings
bucketings = [] #the set of valid partial order preserving bucketings

bucketings_B = [] #the set of flipped (opposite direction) bucketings

#NOTE:--- Ratings are mapped from 1 to R and not 0 to R-1 (careful while using the bucketings!!)

avg = {} #stores the weighted average of every node's ratings
rule = 1
#rule = 1 if all bucketings allowed
#rule = 2 if only >= avg-1 allowed 
#rule = 3 if only <= avg+1
#rule = 4 if avg-1<=r<=avg+1
##############################################################



##############################################################
##############################################################
#The lattice and everything inside
##############################################################
##############################################################

# function to return depth of the tree
def total_depth():
    global R, m
    max_sum = R*m
    min_sum = m
    depth = max_sum - min_sum + 1
    return depth

#function returns total number of nodes in the lattice
def num_nodes():
    return nchoosek(R+m-1,R-1)

def num_nodes_by_depth():
    global R, m, parents, children, depth, nodes_in_depth
    
    x = []
    y = []
    for d in range(total_depth()):
        x.append(d)
        y.append(len(nodes_in_depth[d]))
    #print "Number of nodes by depth = ",y
    print "Plotting number of nodes by depth"
    matplotlib.pyplot.figure()
    matplotlib.pyplot.plot(x,y)
    matplotlib.pyplot.ylabel('Number of nodes')
    matplotlib.pyplot.xlabel('Depth')
    matplotlib.pyplot.title('Lattice: #nodes by depth, R='+str(R)+', m='+str(m))
    matplotlib.pyplot.savefig('Num nodes by depth, R='+str(R)+', m='+str(m)+'.png')
    #matplotlib.pyplot.show()
    matplotlib.pyplot.close()


def nodes_by_depth(time="not input"):
    global R, m, parents, children, depth, nodes_in_depth
    print "Writing lattice to file"
    f = open("Nodes by depth for R = "+str(R)+", m = "+str(m), "w")
    f.write("Time taken to construct lattice = "+str(time)+"s"+"\n")
    f.write("Total number of nodes = "+str(len(depth))+"\n")
    f.write("Height of lattice = "+str(total_depth())+"\n")
    f.write("Width of lattice = "+str(max_width())+"\n\n")
    #print "Nodes by depth: \n"
    for d in range(total_depth()):
        f.write("Depth "+str(d)+":\n")
        for node in nodes_in_depth[d]:
            f.write(str(node)+" ")
        f.write("\n")
    f.close()


def index_by_depth():
    global R, m, parents, children, depth, nodes_in_depth
    print "Indexing by depth"
    for node in depth:
        nodes_in_depth[depth[node]].append(node)
        compute_average(node)
    print "Indexing complete"


def compute_average(node):
    global R, m, parents, children, depth, nodes_in_depth, avg
    s = 0
    for r in range(R):
        s += (R-1-r)*node[r]
    avg[node] = (float)(s)/(float)(m)
    lower = int(max(0,math.ceil(avg[node]-1)))
    upper = int(min(R-1,math.floor(avg[node]+1)))
    #print "node = ",node,", average = ",avg[node]," lower = ",lower,", upper = ",upper
    return


def max_width():
    global R, m, parents, children, depth, nodes_in_depth
    w = 0
    for d in range(total_depth()):
        if w < len(nodes_in_depth[d]):
            w = len(nodes_in_depth[d])
    return w


def construct_two_classes_lattice_general():
    global R, m, parents, children, depth, nodes_in_depth
    print "Constructing lattice\n"

    assert R == 2
    assert m == 2

    node = []
    node.append(m)
    for i in range(R-1):
        node.append(0)
    node2 = tuple(node)
    parents[node2] = []
    depth[node2] = 0
    
    #print "Added", node2
    add_next(node2, depth[node2]) #recursive function call to construct lattice
    
    #Lattice constructed - now index by depth:
    index_by_depth()
    nodes_by_depth()

        
#construct the lattice
def construct_lattice():
    global R, m, parents, children, depth, nodes_in_depth
    print "Constructing lattice\n"
    node = []
    node.append(m)
    for i in range(R-1):
        node.append(0)
    node2 = tuple(node)
    parents[node2] = []
    depth[node2] = 0
    
    #print "Added", node2
    add_next(node2,depth[node2]) #recursive function call to construct lattice
    
    #Lattice constructed - now index by depth:
    index_by_depth()
    
    print "Lattice Constructed, R , m = ",R,",",m,"\n"
    
#recursive call - BFS to construct lattice
def add_next(node,d):
    global R, m, parents, children, depth, nodes_in_depth
    last_node = []
    for i in range(R-1):
        last_node.append(0)
    last_node.append(m)
    last_node2 = tuple(last_node)
    if node == last_node2:
        children[node] = []
        return
    for i in range(R-1):
        if node[i] > 0:
            new_node_list = list(node)
            new_node_list[i] -= 1
            new_node_list[i+1] += 1
            new_node = tuple(new_node_list)
            children[node].append(new_node)
            parents[new_node].append(node)
            dont_add = {}
            if not(new_node in depth):
                #print "Added", new_node
                depth[new_node] = d + 1
            else: #this node as already been seen by a path - correctly update depth
                depth[new_node] = min(d+1,depth[new_node])
                dont_add[new_node]= "True"

    for new in  children[node]:
        if not(new in dont_add):
            add_next(new,depth[new])
    return

def enumerate_order_preserving_bucketings():
    global R, m, parents, children, depth, nodes_in_depth, num_bucketings, bucketings
    print "Beginning enumeration, R , m = ",R,",",m
    completed_depth = -1
    curr_assign = {}
    all_combinations_next_depth(curr_assign,completed_depth)

    print "Enumeration ended\n"


def all_combinations_next_depth(curr_assign,completed_depth):
    global R, m, parents, children, depth, nodes_in_depth, num_bucketings, bucketings
    if completed_depth == total_depth() - 1: #one valid bucketing complete
        #print "1" 
        num_bucketings += 1
        bucketings.append(curr_assign)

    else:
        #print "2"
        assigned = []
        #print "completed depth =",completed_depth,"nodes in depth = ",nodes_in_depth
        to_assign = copy.deepcopy(nodes_in_depth[(completed_depth+1)])
        #print completed_depth,"...",to_assign
        '''assigned_old = assigned[:]
        to_assign_old = to_assign[:]
        curr_assign_old = copy.deepcopy(curr_assign)
        completed_depth_old = completed_depth'''

        all_combinations(assigned, to_assign, curr_assign, completed_depth+1)
        '''assigned = assigned_old[:]
        to_assign = to_assign_old[:]
        curr_assign = copy.deepcopy(curr_assign_old)
        completed_depth = completed_depth_old'''

        
#assigned has node-rating assignments for some nodes
#to_assign has list of remaining nodes
#curr_assign has assignments of all parent (ancestor) nodes    
def all_combinations(assigned, to_assign, curr_assign, curr_depth):
    global R, m, parents, children, depth, nodes_in_depth, num_bucketings, bucketings, rule, avg
    #print "Doing depth ",curr_depth
    #print "assigned =",assigned,"\nto assign = ",to_assign,"\ncurr assign = ",curr_assign
    if len(to_assign) == 0:
        #print "3"
        for (node,val) in assigned:
            curr_assign[node] = val
        #print "completed", curr_assign
        #print curr_depth
        all_combinations_next_depth(curr_assign, curr_depth)

    else:
        #print "4"
        node = to_assign.pop() #all possible values for next node
        #print "next = ",node,"so far = ",curr_assign
        #max_valid = R-1
        min_valid = 0
        if not(len(parents[node])==0):
            for p in parents[node]:
                if curr_assign[p] > min_valid:
                    min_valid = curr_assign[p]
                #if curr_assign[p] < max_valid:
                    #max_valid = curr_assign[p]

        assigned_old = assigned[:]
        to_assign_old = to_assign[:]
        curr_assign_old = copy.deepcopy(curr_assign)
        curr_depth_old = curr_depth
        
        if rule == 1:
            #for r in range(max_valid+1):
            for r in range(min_valid,R):
                assigned.append((node,r))
    
                all_combinations(assigned, to_assign, curr_assign, curr_depth)
    
                assigned = assigned_old[:]
                to_assign = to_assign_old[:]
                curr_assign = copy.deepcopy(curr_assign_old)
                curr_depth = curr_depth_old


##############################################################
#####Parameters outside the lattice
##############################################################

#n = 10000 #number of items
T = {} #true values of items
item_M = {} #key = item index, value = realization tuple
lattice_M = {} #key = lattice node, value = number of items satisfying

s_rule = 1 #determines selectivity parameters
#s_rule == 1 -- uniform item dist across all ratings
#s_rule == 2 -- all items' true value == 0
#NOTE: uniform up to boundary - ceil(R/2) gets all spillover extra
s = {} #actual selectivity vector

####NOTE -- e[(i,j)] = 0 if no item of true rating j exists, or has seen rating i

#e_rule = 4 #determines e_gen parameters
#e_rule == 1 -- correct answer prob double of every other
#e_rule == 2 -- 0.9,0.09,0.01
#e_rule == 3 -- 0.7,0.2,0.1
#e_rule == 4 -- 0.6,0.3,0.1
e_gen = {} #actual error matrix used to generate
#e[(i,j)] - is p(i|true==j)
e_calc = {} #error matrix calculated from M, T

#Now, e[j,(r,r_true)], j =  worker from 0 to m-1

e_calc_constraints = 1
#1 --> no constraints
#2 --> P_ii > P_ji
##############################################################


##############################################################
##############################################################
#Stuff outside the lattice
##############################################################
##############################################################

#assign true values and s[]
def assign_true_value():
    global R, n, T, item_M, lattice_M, s_rule, e_rule, s, e_gen, e_calc
    #print "Assigning true values and selectivity"
    for r in range(R):
        s[r] = 0.0
    
    if s_rule == 1:
        for r in range(R):
            for i in range(n/R):
                T[r*(n/R)+i] = r
        for i in range(n):
            if i not in T: 
                T[i] = (int)(math.ceil(R/2))
            s[T[i]] += 1
    
    #following rules are hard-coded for R = 3
    elif R == 3 and s_rule == 2:
        #print "2"
        s[0] = (int)(0.2*n)
        #print s[0]
        s[1] = (int)(0.6*n)
        #print s[1]
        s[2] = n - s[0] - s[1]
        #print s[2]

        for i in range(n):
            if i < s[0]:
                T[i] = 0
            elif i < s[0]+s[1]:
                T[i] = 1
            else:
                T[i] = 2
    
    elif R == 3 and s_rule == 3:
        s[0] = (int)(0.4*n)
        s[1] = (int)(0.2*n)
        s[2] = n - s[0] - s[1]
        count = 0
        for i in range(n):
            if count < s[0]:
                T[i] = 0
            elif count < s[0]+s[1]:
                T[i] = 1
            else:
                T[i] = 2
            count += 1

    elif R == 3 and s_rule == 4:
        s[0] = (int)(0.7*n)
        s[1] = (int)(0.2*n)
        s[2] = n - s[0] - s[1]
        count = 0
        for i in range(n):
            if count < s[0]:
                T[i] = 0
            elif count < s[0]+s[1]:
                T[i] = 1
            else:
                T[i] = 2
            count += 1

    elif R == 3 and s_rule == 5:
        s[0] = (int)(0.6*n)
        s[1] = (int)(0.3*n)
        s[2] = n - s[0] - s[1]
        count = 0
        for i in range(n):
            if count < s[0]:
                T[i] = 0
            elif count < s[0]+s[1]:
                T[i] = 1
            else:
                T[i] = 2
            count += 1


    #for R==2
    elif R == 2 and s_rule == 2:
        s[0] = (int)(0.3*n)
        s[1] = n - s[0]

        for i in range(n):
            if i < s[0]:
                T[i] = 0
            else:
                T[i] = 1

    elif R == 2 and s_rule == 3:
        s[0] = (int)(0.1*n)
        #s[0] = (int)(0.2*n)
        s[1] = n - s[0]

        for i in range(n):
            if i < s[0]:
                T[i] = 0
            else:
                T[i] = 1

            
    
    for r in range(R):
        s[r] /= float(n)
    
    #print "Selectivity: ",s
    return

#sets e_gen
injecting_random = True
injection_frac = 0.15
def set_error(random_e):
    global R, n, T, item_M, lattice_M, s_rule, e_rule, s, e_gen, e_calc, m, max_workers

    random.seed()
    
    for j in range(max_workers):
        for r1 in range(R):
            for r2 in range(R):
                e_gen[j,(r1,r2)] = 0.0
        
        if random_e == 0:
            if e_rule == 4:
                for r in range(R):
                    for r_true in range(R):
                        if r == r_true:
                            e_gen[j,(r,r_true)] = 2.0/(float)(R+1)
                        else:
                            e_gen[j,(r,r_true)] = 1.0/(float)(R+1)
            
            elif e_rule == 1 and R == 3:
                e_gen[j,(0,0)] = 0.9
                e_gen[j,(1,0)] = 0.09
                e_gen[j,(2,0)] = 0.01
                e_gen[j,(0,1)] = 0.01
                e_gen[j,(1,1)] = 0.98
                e_gen[j,(2,1)] = 0.01
                e_gen[j,(0,2)] = 0.01
                e_gen[j,(1,2)] = 0.09
                e_gen[j,(2,2)] = 0.9
                
            elif e_rule == 2 and R == 3:
                e_gen[j,(0,0)] = 0.7
                e_gen[j,(1,0)] = 0.2
                e_gen[j,(2,0)] = 0.1
                e_gen[j,(0,1)] = 0.15
                e_gen[j,(1,1)] = 0.7
                e_gen[j,(2,1)] = 0.15
                e_gen[j,(0,2)] = 0.1
                e_gen[j,(1,2)] = 0.2
                e_gen[j,(2,2)] = 0.7
                
            elif e_rule == 3 and R == 3:
                e_gen[j,(0,0)] = 0.6
                e_gen[j,(1,0)] = 0.3
                e_gen[j,(2,0)] = 0.1
                e_gen[j,(0,1)] = 0.2
                e_gen[j,(1,1)] = 0.6
                e_gen[j,(2,1)] = 0.2
                e_gen[j,(0,2)] = 0.1
                e_gen[j,(1,2)] = 0.3
                e_gen[j,(2,2)] = 0.6

            elif e_rule == 5 and R == 3:
                e_gen[j,(0,0)] = 0.6
                e_gen[j,(1,0)] = 0.3
                e_gen[j,(2,0)] = 0.1
                e_gen[j,(0,1)] = 0.4
                e_gen[j,(1,1)] = 0.2
                e_gen[j,(2,1)] = 0.4
                e_gen[j,(0,2)] = 0.1
                e_gen[j,(1,2)] = 0.3
                e_gen[j,(2,2)] = 0.6


            elif e_rule == 6 and R == 3:
                e_gen[j,(0,0)] = 0.34
                e_gen[j,(1,0)] = 0.33
                e_gen[j,(2,0)] = 0.33
                e_gen[j,(0,1)] = 0.33
                e_gen[j,(1,1)] = 0.34
                e_gen[j,(2,1)] = 0.33
                e_gen[j,(0,2)] = 0.33
                e_gen[j,(1,2)] = 0.33
                e_gen[j,(2,2)] = 0.34


            elif e_rule == 7 and R == 3:
                e_gen[j,(0,0)] = 0.2
                e_gen[j,(1,0)] = 0.4
                e_gen[j,(2,0)] = 0.4
                e_gen[j,(0,1)] = 0.4
                e_gen[j,(1,1)] = 0.2
                e_gen[j,(2,1)] = 0.4
                e_gen[j,(0,2)] = 0.2
                e_gen[j,(1,2)] = 0.4
                e_gen[j,(2,2)] = 0.4


            elif e_rule == 8 and R == 3:
                e_gen[j,(0,0)] = 0.1
                e_gen[j,(1,0)] = 0.3
                e_gen[j,(2,0)] = 0.6
                e_gen[j,(0,1)] = 0.4
                e_gen[j,(1,1)] = 0.2
                e_gen[j,(2,1)] = 0.4
                e_gen[j,(0,2)] = 0.6
                e_gen[j,(1,2)] = 0.3
                e_gen[j,(2,2)] = 0.1


            elif e_rule == 1 and R == 2:
                e_gen[j,(0,0)] = 0.9
                e_gen[j,(1,0)] = 0.1
                e_gen[j,(0,1)] = 0.1
                e_gen[j,(1,1)] = 0.9
                
            elif e_rule == 2 and R == 2:
                e_gen[j,(0,0)] = 0.7
                e_gen[j,(1,0)] = 0.3
                e_gen[j,(0,1)] = 0.3
                e_gen[j,(1,1)] = 0.7
                
            elif e_rule == 3 and R == 2:
                e_gen[j,(0,0)] = 0.6
                e_gen[j,(1,0)] = 0.4
                e_gen[j,(0,1)] = 0.4
                e_gen[j,(1,1)] = 0.6

            elif e_rule == 5 and R == 2:
                e_gen[j,(0,0)] = 0.4
                e_gen[j,(1,0)] = 0.6
                e_gen[j,(0,1)] = 0.6
                e_gen[j,(1,1)] = 0.4
                
            elif e_rule == 6 and R == 2:
                e_gen[j,(0,0)] = 0.3
                e_gen[j,(1,0)] = 0.7
                e_gen[j,(0,1)] = 0.7
                e_gen[j,(1,1)] = 0.3


            if e_rule == 4 and R == 2: #overwrite
                e_gen[j,(0,0)] = 0.5
                e_gen[j,(1,0)] = 0.5
                e_gen[j,(0,1)] = 0.5
                e_gen[j,(1,1)] = 0.5

        #randomized worker matrix, but p(error) increases with distance
        elif random_e == 1:
            if R == 2:
                if injecting_random and random.random() < injection_frac:
                    e_gen[j,(0,0)] = random.random()
                    e_gen[j,(1,0)] = 1.0 - e_gen[j,(0,0)]
                    e_gen[j,(1,1)] = random.random()
                    e_gen[j,(0,1)] = 1.0 - e_gen[j,(1,1)]
                else:
                    e_gen[j,(0,0)] = random.uniform(0.5,1.0)
                    e_gen[j,(1,0)] = 1.0 - e_gen[j,(0,0)]
                    e_gen[j,(1,1)] = random.uniform(0.5,1.0)
                    e_gen[j,(0,1)] = 1.0 - e_gen[j,(1,1)]

            elif R == 3:
                if injecting_random and random.random() < injection_frac:
                    e_gen[j,(0,0)] = random.random()
                    e_gen[j,(1,0)] = random.uniform(0.0,1.0-e_gen[j,(0,0)])
                    e_gen[j,(2,0)] = 1.0-e_gen[j,(0,0)]-e_gen[j,(1,0)]

                    e_gen[j,(1,1)] = random.random()
                    e_gen[j,(0,1)] = random.uniform(0.0,1.0-e_gen[j,(1,1)])
                    e_gen[j,(2,1)] = 1.0-e_gen[j,(1,1)]-e_gen[j,(0,1)]
                    
                    e_gen[j,(2,2)] = random.random()
                    e_gen[j,(1,2)] = random.uniform(0.0,1.0-e_gen[j,(2,2)])
                    e_gen[j,(0,2)] = 1.0-e_gen[j,(2,2)]-e_gen[j,(1,2)]
                else:
                    e_gen[j,(0,0)] = random.uniform(1.0/3.0,1.0)
                    e_gen[j,(1,0)] = random.uniform((1.0-e_gen[j,(0,0)])/2.0,min(e_gen[j,(0,0)],1-e_gen[j,(0,0)]))
                    e_gen[j,(2,0)] = 1.0-e_gen[j,(0,0)]-e_gen[j,(1,0)]
                    
                    e_gen[j,(1,1)] = random.uniform(1.0/3.0,1.0)
                    e_gen[j,(0,1)] = random.uniform(max(0.0,1-2*e_gen[j,(1,1)]),min(e_gen[j,(1,1)],1-e_gen[j,(1,1)]))
                    e_gen[j,(2,1)] = 1.0-e_gen[j,(1,1)]-e_gen[j,(0,1)]
                    
                    e_gen[j,(2,2)] = random.uniform(1.0/3.0,1.0)
                    e_gen[j,(1,2)] = random.uniform((1.0-e_gen[j,(2,2)])/2.0,min(e_gen[j,(2,2)],1-e_gen[j,(2,2)]))
                    e_gen[j,(0,2)] = 1.0-e_gen[j,(2,2)]-e_gen[j,(1,2)]

        #completely randomized worker matrix
        elif random_e == 2:
            if R == 2:
                e_gen[j,(0,0)] = random.random()
                e_gen[j,(1,0)] = 1.0 - e_gen[j,(0,0)]
                e_gen[j,(1,1)] = random.random()
                e_gen[j,(0,1)] = 1.0 - e_gen[j,(1,1)]

            elif R == 3:
                e_gen[j,(0,0)] = random.random()
                e_gen[j,(1,0)] = random.uniform(0.0,1.0-e_gen[j,(0,0)])
                e_gen[j,(2,0)] = 1.0-e_gen[j,(0,0)]-e_gen[j,(1,0)]

                e_gen[j,(1,1)] = random.random()
                e_gen[j,(0,1)] = random.uniform(0.0,1.0-e_gen[j,(1,1)])
                e_gen[j,(2,1)] = 1.0-e_gen[j,(1,1)]-e_gen[j,(0,1)]
                
                e_gen[j,(2,2)] = random.random()
                e_gen[j,(1,2)] = random.uniform(0.0,1.0-e_gen[j,(2,2)])
                e_gen[j,(0,2)] = 1.0-e_gen[j,(2,2)]-e_gen[j,(1,2)]

        #two worker classes [bad, good]
        elif random_e == 3:
            if R == 2:
                e_gen[j,(0,0)] = random.choice([0.7,0.9])
                e_gen[j,(1,0)] = 1.0 - e_gen[j,(0,0)]
                e_gen[j,(1,1)] = random.choice([0.7,0.9])
                e_gen[j,(0,1)] = 1.0 - e_gen[j,(1,1)]

            elif R == 3:
                e_gen[j,(0,0)] = random.choice([0.5,0.7])
                if e_gen[j,(0,0)] == 0.5:
                    e_gen[j,(1,0)] = 0.3
                    e_gen[j,(2,0)] = 0.2
                else:
                    e_gen[j,(1,0)] = 0.2
                    e_gen[j,(2,0)] = 0.1

                e_gen[j,(1,1)] = random.choice([0.5,0.7])
                if e_gen[j,(1,1)] == 0.5:
                    e_gen[j,(0,1)] = 0.25
                    e_gen[j,(2,1)] = 0.25
                else:
                    e_gen[j,(0,1)] = 0.15
                    e_gen[j,(2,1)] = 0.15
                
                e_gen[j,(2,2)] = random.choice([0.5,0.7])
                if e_gen[j,(2,2)] == 0.5:
                    e_gen[j,(1,2)] = 0.3
                    e_gen[j,(0,2)] = 0.2
                else:
                    e_gen[j,(1,2)] = 0.2
                    e_gen[j,(0,2)] = 0.1
                


    '''print "E_Gen: "
    for r_true in range(R):
        print r_true,"---> ",
        for r in range(R):
            print "(",r,":",e_gen[(r,r_true)],")",
        print ""'''

def plot_error():
    global R, n, T, item_M, lattice_M, s_rule, e_rule, s, e_gen, e_calc
    x = range(R)
    y = []
    for r in range(R):
        y.append(e_gen[(r,0)])

    matplotlib.pyplot.figure()
    matplotlib.pyplot.plot(x,y,'x-')
    matplotlib.pyplot.ylabel('Probability')
    matplotlib.pyplot.xlabel('Distance from True Value')
    matplotlib.pyplot.title('E_rule = '+str(e_rule))
    matplotlib.pyplot.savefig('E_rule = '+str(e_rule)+'.png')
    #matplotlib.pyplot.show()
    matplotlib.pyplot.close()

#generates M from T and e_gen and calculates e_calc
full_realization = defaultdict(list) #full_realization[i] = [responses by list of workers in range(m)]
workers_answered = defaultdict(list) #workers_answered[i] = workers who answered item i
def generate_M():
    global R, n, T, item_M, lattice_M, s_rule, e_rule, s, e_gen, e_calc, depth
    

    workers_answered.clear()
    full_realization.clear()
    for i in range(n):
        workers_answered[i] = []
        for j in range(max_workers):
            full_realization[i].append(-1)


    #initialize lattice_M
    for node in depth:
        lattice_M[node] = 0
    
    #initialize e_calc
    for r1 in range(R):
        for r2 in range(R):
            e_calc[(r1,r2)] = 0.0
    
    total_responses = []
    for i in range(R):
        total_responses.append(0.0) #for normalization
        
    #print "\nGenerating realizations for items:\n"
    for i in range(n):
        item_M[i] = generate_realization(i)
        #print "Item",i,", Realization",item_M[i],", true value",T[i]
        lattice_M[item_M[i]] += 1
        realization_list = list(item_M[i]) #just to use as list
        for r in range(R):
            total_responses[T[i]] += (float)(realization_list[r])
            e_calc[(r,T[i])] += (float)(realization_list[r])
    
    #normalize e_calc        
    for r1 in range(R):
        for r2 in range(R):
            if total_responses[r2] > 0.0:
                e_calc[(r1,r2)] /= total_responses[r2]
            else: 
                e_calc[(r1,r2)] = 0.0    
    return

def generate_realization(i):
    global R, m, n, T, item_M, lattice_M, s_rule, e_rule, s, e_gen, e_calc
    realization = []
    for r in range(R):
        realization.append(0)
    
    set_of_workers = random.sample(range(max_workers),m)
    for j in set_of_workers:
        prob_pdt = 1.0
        for r in range(R):
            if random.random() < e_gen[j,(r,T[i])]/(float)(prob_pdt):
                realization[r] += 1
                full_realization[i][j] = r
                workers_answered[i].append(j)
                #full_realization
                break
            else:
                prob_pdt *= (1.0 - e_gen[j,(r,T[i])]/(float)(prob_pdt))
    
    return tuple(realization)

#calculate P(M|f)

#f passed has key: tuple (node in lattice) and value: mapped rating
def calc_e(f,full=False):
    global R, n, T, item_M, lattice_M, s_rule, e_rule, s, e_gen, e_calc, depth, e_calc_constraints
    if full == True:
        return calc_e_full(f)

    e = {}
    for r1 in range(R):
        for r2 in range(R):
            e[(r1,r2)] = 0.0
    
    total_responses = []
    for i in range(R):
        total_responses.append(0.0) #for normalization
        
    for node in lattice_M:
        realization_list = list(node) #just to use as list
        true_r = f[node]
        for r in range(R):
            #print "-------------\ntotal_responses = ",total_responses
            #print "f[node] = ",f[node]
            #print "realization_list = ",realization_list
            #print "r = ",r
            total_responses[true_r] += lattice_M[node]*(float)(realization_list[r])
            e[(r,true_r)] += lattice_M[node]*(float)(realization_list[r])
    
    #here e[(r,r_true)] holds counts a_ij
    
    if e_calc_constraints == 1:
        #normalize e_calc      
        #print "111"  
        for r1 in range(R):
            for r2 in range(R):
                if total_responses[r2] > 0.0:
                    e[(r1,r2)] /= total_responses[r2]
                else:
                    e[(r1,r2)] = 1.0/(float)(R)
                    #e[(r1,r2)] = 0.0
                    
    return e

#f passed has key: item (range(n)) and value: mapped rating
#return per worker rating
def calc_e_full(f):
    global R, n, T, m, item_M, lattice_M, s_rule, e_rule, s, e_gen, e_calc, depth, e_calc_constraints, max_workers
    global workers_answered
    e = {}
    for j in range(max_workers):
        for r1 in range(R):
            for r2 in range(R):
                e[j,(r1,r2)] = 0.0
    
    for j in range(max_workers):
        total_responses = []
        for r in range(R):
            total_responses.append(0.0) #for normalization
            
        for i in range(n):
            if j in workers_answered[i]:
                true_r = f[i]
                total_responses[true_r] += 1.0
                e[j,(full_realization[i][j],true_r)] += 1.0
        
        #here e[(r,r_true)] holds counts a_ij
        
        if e_calc_constraints == 1:
            #normalize e_calc      
            #print "111"  
            for r1 in range(R):
                for r2 in range(R):
                    if total_responses[r2] > 0.0:
                        e[j,(r1,r2)] /= total_responses[r2]
                    else:
                        e[j,(r1,r2)] = 1.0/(float)(R)
                    #e[(r1,r2)] = 0.0

    return e

#f passed has key: tuple (node in lattice) and value: mapped rating
def compute_likelihood(f,full=False):
    global R, m, n, T, item_M, lattice_M, s_rule, e_rule, s, e_gen, e_calc
    if full == True:
        return compute_likelihood_full(f)

    prob = 0.0 #0 and add because using log()
    #else start with 1.0 and multiply
    #prob = 1.0
    err = calc_e(f)
    for node in lattice_M:
        if lattice_M[node] == 0:
            continue
        p_node = 0.0 #0 and add because using log()
        #p_node = 1.0
        true_r = f[node]
        realization_list = list(node)
        for r in range(R):
            if realization_list[r] > 0 and err[(r,true_r)]==0:
                print "ERROR"
            elif err[(r,true_r)] > 0:
                p_node += realization_list[r]*math.log(err[(r,true_r)])
            '''if realization_list[r] > 0: #implies err[(r,true_r)] > 0
                if err[(r,true_r)] > 0:
                    p_node += realization_list[r]*math.log(err[(r,true_r)])'''
                
        p_node = lattice_M[node]*p_node
        prob += p_node
               
    return prob

#f passed has key: item (range(n)) and value: mapped rating
def compute_likelihood_full(f):
    global R, m, n, T, item_M, lattice_M, s_rule, e_rule, s, e_gen, e_calc, full_realization, workers_answered

    prob = 0.0 #0 and add because using log()
    #else start with 1.0 and multiply
    #prob = 1.0
    err = calc_e(f,True)

    for i in range(n):
        true_r = f[i]
        for j in workers_answered[i]:
            prob += math.log(err[j,(full_realization[i][j],true_r)])
               
    return prob

def calc_s(f):
    return

def Return_em_bucketing(start):
    em_assn = {}
    for node in lattice_M:
        em_assn[node] = 0
        
    #currently done for R == 3 - do for rest later
    '''if R!=3:
        return em_assn'''
    
    num_iterations = 40
    e_est = {}
    '''elif start == 2:
    e_est[(0,0)] = 0.34
    e_est[(1,0)] = 0.33
    e_est[(2,0)] = 0.33
    e_est[(0,1)] = 0.33
    e_est[(1,1)] = 0.34
    e_est[(2,1)] = 0.33
    e_est[(0,2)] = 0.33
    e_est[(1,2)] = 0.33
    e_est[(2,2)] = 0.34'''
    if R==3:
        if start == 3:
            e_est[(0,0)] = 0.07
            e_est[(1,0)] = 0.33
            e_est[(2,0)] = 0.6
            e_est[(0,1)] = 0.33
            e_est[(1,1)] = 0.34
            e_est[(2,1)] = 0.33
            e_est[(0,2)] = 0.6
            e_est[(1,2)] = 0.33
            e_est[(2,2)] = 0.07
        elif start == 2:
            e_est[(0,0)] = 1.0/3.0
            e_est[(1,0)] = 1.0/3.0
            e_est[(2,0)] = 1.0/3.0
            e_est[(0,1)] = 1.0/3.0
            e_est[(1,1)] = 1.0/3.0
            e_est[(2,1)] = 1.0/3.0
            e_est[(0,2)] = 1.0/3.0
            e_est[(1,2)] = 1.0/3.0
            e_est[(2,2)] = 1.0/3.0
        elif start == 1:
            e_est[(0,0)] = 0.6
            e_est[(1,0)] = 0.33
            e_est[(2,0)] = 0.07
            e_est[(0,1)] = 0.33
            e_est[(1,1)] = 0.34
            e_est[(2,1)] = 0.33
            e_est[(0,2)] = 0.07
            e_est[(1,2)] = 0.33
            e_est[(2,2)] = 0.6

    elif R==2:
        if start == 1:
            e_est[(0,0)] = 0.75
            e_est[(1,0)] = 0.25
            e_est[(0,1)] = 0.25
            e_est[(1,1)] = 0.75
        if start == 2:
            e_est[(0,0)] = 0.5
            e_est[(1,0)] = 0.5
            e_est[(0,1)] = 0.5
            e_est[(1,1)] = 0.5
        if start == 3:
            e_est[(0,0)] = 0.25
            e_est[(1,0)] = 0.75
            e_est[(0,1)] = 0.75
            e_est[(1,1)] = 0.25

    else:
        for true_r in range(R):
            total = 0.0
            for r in range(R-1):
                e_est[(r,true_r)] = 1.0/(float)(R)
                total += e_est[(r,true_r)]
            e_est[(R-1,true_r)] = 1.0 - total
        
    for i in range(num_iterations):
        #M step - update em_assn
        for node in lattice_M:
            temp_assn = 0
            temp_max = 0
            for true_r in range(R):
                p_node = 0.0 #0 and add because using log()
                realization_list = list(node)
                for r in range(R):
                    if realization_list[r] > 0: #implies err[(r,true_r)] > 0
                        if e_est[(r,true_r)] > 0:
                            p_node += realization_list[r]*math.log(e_est[(r,true_r)])

                if true_r == 0:
                    temp_max = p_node
                    temp_assn = true_r
                elif temp_max < p_node:
                    temp_max = p_node
                    temp_assn = true_r

            em_assn[node] = temp_assn
                    
        #E step - update e_est
        e_est = calc_e(em_assn)

    return em_assn

def Return_em_general_bucketing(start):
    global R,m,n,workers_answered
    em_assn = {} #rating per item
    for i in range(n):
        em_assn[i] = 0
        
    #currently done for R == 3 - do for rest later
    '''if R!=3:
        return em_assn'''
    
    num_iterations = 40
    e_est = {}

    for j in range(max_workers):
		if R==3:
			if start == 3:
				e_est[j,(0,0)] = 0.07
				e_est[j,(1,0)] = 0.33
				e_est[j,(2,0)] = 0.6
				e_est[j,(0,1)] = 0.33
				e_est[j,(1,1)] = 0.34
				e_est[j,(2,1)] = 0.33
				e_est[j,(0,2)] = 0.6
				e_est[j,(1,2)] = 0.33
				e_est[j,(2,2)] = 0.07
			elif start == 2:
				e_est[j,(0,0)] = 1.0/3.0
				e_est[j,(1,0)] = 1.0/3.0
				e_est[j,(2,0)] = 1.0/3.0
				e_est[j,(0,1)] = 1.0/3.0
				e_est[j,(1,1)] = 1.0/3.0
				e_est[j,(2,1)] = 1.0/3.0
				e_est[j,(0,2)] = 1.0/3.0
				e_est[j,(1,2)] = 1.0/3.0
				e_est[j,(2,2)] = 1.0/3.0
			elif start == 1:
				e_est[j,(0,0)] = 0.6
				e_est[j,(1,0)] = 0.33
				e_est[j,(2,0)] = 0.07
				e_est[j,(0,1)] = 0.33
				e_est[j,(1,1)] = 0.34
				e_est[j,(2,1)] = 0.33
				e_est[j,(0,2)] = 0.07
				e_est[j,(1,2)] = 0.33
				e_est[j,(2,2)] = 0.6

		elif R==2:
			if start == 1:
				e_est[j,(0,0)] = 0.75
				e_est[j,(1,0)] = 0.25
				e_est[j,(0,1)] = 0.25
				e_est[j,(1,1)] = 0.75
			if start == 2:
				e_est[j,(0,0)] = 0.5
				e_est[j,(1,0)] = 0.5
				e_est[j,(0,1)] = 0.5
				e_est[j,(1,1)] = 0.5
			if start == 3:
				e_est[j,(0,0)] = 0.25
				e_est[j,(1,0)] = 0.75
				e_est[j,(0,1)] = 0.75
				e_est[j,(1,1)] = 0.25

		else:
			for true_r in range(R):
				total = 0.0
				for r in range(R-1):
					e_est[j,(r,true_r)] = 1.0/(float)(R)
					total += e_est[j,(r,true_r)]
				e_est[j,(R-1,true_r)] = 1.0 - total
        
    '''print "full realization = "
    print full_realization
    print "e_est = "
    print e_est'''
    for t in range(num_iterations):
        for i in range(n):
            #M step - update em_assn
            temp_assn = 0
            temp_max = 0
            for true_r in range(R):
                p_node = 0.0 #0 and add because using log(), prob of i's best guess being true_r
                #realization_list = list(node)
                for j in workers_answered[i]:
                    '''print "HERE"
                    print j
                    print full_realization[i][j]
                    print true_r
                    print e_est'''
                    p_node += e_est[j,(full_realization[i][j],true_r)]
                    
                if true_r == 0:
                    temp_max = p_node
                    temp_assn = true_r
                elif temp_max < p_node:
                    temp_max = p_node
                    temp_assn = true_r

            em_assn[i] = temp_assn
                    
        #E step - update e_est
        e_est = calc_e_full(em_assn)

    return em_assn

def Return_AVG_bucketing():
    avg_assn = {}
    for node in lattice_M:
        s = 0
        for r in range(R):
            s += r*node[r]
            #s += (R-1-r)*node[r]
        avg = (float)(s)/(float)(m)
        avg_assn[node]=(int)(round(avg))

    return avg_assn

def Return_median_bucketing():
    median_assn = {}
    for node in lattice_M:
        s = 0
        for r in range(R):
            s += node[r]
            if s > m/2:
                median = r
                #median = (R-1-r)
                break
        median_assn[node]=(int)(round(median))

    return median_assn

def Return_random_bucketing():
    random_assn = {}
    for node in lattice_M:
        random_assn[node]=random.randint(0,R-1)

    return random_assn

##############################################################

#main1 --- for generating the lattice

def compute_min_max_f():
    global R, m, parents, children, depth, nodes_in_depth, num_bucketings, bucketings, rule
    global n, T, item_M, lattice_M, s_rule, e_rule, s, e_gen, e_calc

    global likelihood_OPT, likelihood_avg, likelihood_median, likelihood_random
    global score_OPT, score_avg, score_median, score_random

    count = 0
    max2_set = False

    for b in bucketings:
        #initialize
        #print "count =",count
        b_B = {}
        for key in b:
            b_B[key] = R-1-b[key]
        
        if count == 0:
            min = compute_likelihood(b)
            max = min
            min_bucketing = b
            max_bucketing = b

            min_B = compute_likelihood(b_B)
            max_B = min_B
            min_bucketing_B = b_B
            max_bucketing_B = b_B
            
            count += 1
        
        else:
            count += 1
            current = compute_likelihood(b)
            current_B = compute_likelihood(b_B)
            if min > current:
                min = current
                min_bucketing = b
            elif max < current:
                max = current
                max_bucketing = b

            if min_B > current_B:
                min_B = current_B
                min_bucketing_B = b_B
            elif max_B < current_B:
                max_B = current_B
                max_bucketing_B = b_B


        if R==3: #currently hard coded check for R=3... do others later
            e2 = calc_e(b)
            if max2_set == False:
                if e2[(1,1)]>=e2[(0,1)] and e2[(1,1)]>=e2[(2,1)]:
                    max_bucketing2 = b
                    max2 = compute_likelihood(b)
                    max2_set = True
            elif e2[(1,1)]>=e2[(0,1)] and e2[(1,1)]>=e2[(2,1)]:
                current = compute_likelihood(b)
                if max2 < current:
                    max2 = current
                    max_bucketing2 = b

        elif R==2:
            max2 = max
            max_bucketing2 = max_bucketing
            
        '''elif R==2: #currently hard coded check for R=3... do others later
            e2 = calc_e(b)
            if max2_set == False:
                if e2[(1,1)]>=e2[(0,1)] and e2[(0,0)]>=e2[(1,0)]:
                    max_bucketing2 = b
                    max2 = compute_likelihood(b)
                    max2_set = True
            elif e2[(1,1)]>=e2[(0,1)] and e2[(0,0)]>=e2[(1,0)]:
                current = compute_likelihood(b)
                if max2 < current:
                    max2 = current
                    max_bucketing2 = b'''

    #temporary fix to check if the max bucketing is coming from full version of EM
    max_from_full_EM = False

    '''print "############################"
    print "OPTIMAL"    
    print "Max likelihood =",max
    '''
    likelihood_OPT.append(max/m)
    
    #print "Corresponding bucketing =",max_bucketing
    e_max = calc_e(max_bucketing)
    '''e_max_corrected = {} #above e_max is inverted
    for r_true in range(R):
        for r in range(R):
            e_max_corrected[(r,r_true)] = e_max[(R-r-1,r_true)]'''
    e_max_corrected = e_max
    '''print "Calculated error from this -"
    print "E: "
    for r_true in range(R):
        print r_true,"---> ",
        for r in range(R):
            print "(",r,":",e_max_corrected[(r,r_true)],")",
        print ""'''
    #print "\nDiff_Score =",diff_score(e_max)

    temp2 = emd_score(e_max_corrected,max_bucketing)
    #print "\nEMD Score =",temp2
    
    score_OPT.append(temp2)

    '''print "############################"
    print "OPTIMAL*"    
    print "Max likelihood * =",max_B
    '''
    likelihood_OPT_B.append(max_B/m)
    
    #print "Corresponding bucketing =",max_bucketing
    e_max_B = calc_e(max_bucketing_B)
    '''e_max_corrected = {} #above e_max is inverted
    for r_true in range(R):
        for r in range(R):
            e_max_corrected[(r,r_true)] = e_max[(R-r-1,r_true)]'''
    e_max_corrected_B = e_max_B
    '''print "Calculated error from this -"
    print "E: "
    for r_true in range(R):
        print r_true,"---> ",
        for r in range(R):
            print "(",r,":",e_max_corrected[(r,r_true)],")",
        print ""'''
    #print "\nDiff_Score =",diff_score(e_max)

    temp2 = emd_score(e_max_corrected_B,max_bucketing_B)
    #print "\nEMD Score =",temp2
    
    score_OPT_B.append(temp2)


    '''print "############################"
    print "EM(1)"'''
    em_bucketing1 = Return_em_bucketing(1)
    temp = compute_likelihood(em_bucketing1)
    #print "Median algo likelihood =",temp
    
    em_bucketing_max = em_bucketing1
    em_likelihood_max = temp

    likelihood_em1.append(temp/m)
    
    #print "Corresponding bucketing =",median_bucketing
    e_em1 = calc_e(em_bucketing1)
    e_em_corrected1 = e_em1
    '''e_em_corrected = {} #above e_max is inverted
    for r_true in range(R):
        for r in range(R):
            e_em_corrected[(r,r_true)] = e_em[(R-r-1,r_true)]'''
    '''print "Calculated error from this -"
    print "E: "
    for r_true in range(R):
        print r_true,"---> ",
        for r in range(R):
            print "(",r,":",e_em_corrected[(r,r_true)],")",
        print ""'''
    #print "\nDiff_Score =",diff_score(e_max)
    temp2 = emd_score(e_em_corrected1,em_bucketing1)
    #print "\nEMD Score =",temp2
    score_em1.append(temp2)

    '''print "############################"
    print "EM(2)"'''
    ##HERE DOING GENERAL EM!
    #em_bucketing2 = Return_em_bucketing(2)
    em_bucketing2 = Return_em_general_bucketing(1)
    #temp = compute_likelihood(em_bucketing2)
    temp = compute_likelihood(em_bucketing2,True)
    #print "Median algo likelihood =",temp

    if temp > em_likelihood_max:
        em_bucketing_max = em_bucketing2
        em_likelihood_max = temp
        #using EM full version here for now so --
        max_from_full_EM = True
    
    likelihood_em2.append(temp/m)
    
    #print "Corresponding bucketing =",median_bucketing
    #e_em2 = calc_e(em_bucketing2)
    e_em2 = calc_e(em_bucketing2,True)
    e_em_corrected2 = e_em2

    #print "\nDiff_Score =",diff_score(e_max)
    temp2 = emd_score(e_em_corrected2,em_bucketing2,True)
    #print "\nEMD Score =",temp2
    score_em2.append(temp2)

    '''print "############################"
    print "EM(3)"'''
    em_bucketing3 = Return_em_bucketing(3)
    temp = compute_likelihood(em_bucketing3)
    #print "Median algo likelihood =",temp

    if temp > em_likelihood_max:
        em_bucketing_max = em_bucketing3
        em_likelihood_max = temp
        max_from_full_EM = False
    
    likelihood_em3.append(temp/m)
    
    #print "Corresponding bucketing =",median_bucketing
    e_em3 = calc_e(em_bucketing3)
    e_em_corrected3 = e_em3
    '''e_em_corrected = {} #above e_max is inverted
    for r_true in range(R):
        for r in range(R):
            e_em_corrected[(r,r_true)] = e_em[(R-r-1,r_true)]'''
    '''print "Calculated error from this -"
    print "E: "
    for r_true in range(R):
        print r_true,"---> ",
        for r in range(R):
            print "(",r,":",e_em_corrected[(r,r_true)],")",
        print ""'''
    #print "\nDiff_Score =",diff_score(e_max)
    temp2 = emd_score(e_em_corrected3,em_bucketing3)
    #print "\nEMD Score =",temp2
    score_em3.append(temp2)

    '''print "############################"
    print "EM(*)"'''
    temp = compute_likelihood(em_bucketing_max,max_from_full_EM) #in case max from general EM
    
    likelihood_em_max.append(temp/m)
    
    #print "Corresponding bucketing =",median_bucketing
    e_em_max = calc_e(em_bucketing_max,max_from_full_EM)
    e_em_corrected_max = e_em_max
    '''e_em_corrected = {} #above e_max is inverted
    for r_true in range(R):
        for r in range(R):
            e_em_corrected[(r,r_true)] = e_em[(R-r-1,r_true)]'''
    '''print "Calculated error from this -"
    print "E: "
    for r_true in range(R):
        print r_true,"---> ",
        for r in range(R):
            print "(",r,":",e_em_corrected[(r,r_true)],")",
        print ""'''
    #print "\nDiff_Score =",diff_score(e_max)
    temp2 = emd_score(e_em_corrected_max,em_bucketing_max,max_from_full_EM)
    #print "\nEMD Score =",temp2
    score_em_max.append(temp2)

def compute_algo(algo):
    global R, m, parents, children, depth, nodes_in_depth, num_bucketings, bucketings, rule
    global n, T, item_M, lattice_M, s_rule, e_rule, s, e_gen, e_calc

    #global likelihood_OPT, likelihood_avg, likelihood_median, likelihood_random
    #global score_OPT, score_avg, score_median, score_random
    global likelihood
    global score

    count = 0
    max2_set = False

    time_start = time.time()

    if algo == "OPT":
        for b in bucketings:
            #initialize
            #print "count =",count
            b_B = {}
            for key in b:
                b_B[key] = R-1-b[key]
            
            if count == 0:
                min = compute_likelihood(b)
                max = min
                min_bucketing = b
                max_bucketing = b

                min_B = compute_likelihood(b_B)
                max_B = min_B
                min_bucketing_B = b_B
                max_bucketing_B = b_B
                
                count += 1
            
            else:
                count += 1
                current = compute_likelihood(b)
                current_B = compute_likelihood(b_B)
                if min > current:
                    min = current
                    min_bucketing = b
                elif max < current:
                    max = current
                    max_bucketing = b

                if min_B > current_B:
                    min_B = current_B
                    min_bucketing_B = b_B
                elif max_B < current_B:
                    max_B = current_B
                    max_bucketing_B = b_B


            if R==3: #currently hard coded check for R=3... do others later
                e2 = calc_e(b)
                if max2_set == False:
                    if e2[(1,1)]>=e2[(0,1)] and e2[(1,1)]>=e2[(2,1)]:
                        max_bucketing2 = b
                        max2 = compute_likelihood(b)
                        max2_set = True
                elif e2[(1,1)]>=e2[(0,1)] and e2[(1,1)]>=e2[(2,1)]:
                    current = compute_likelihood(b)
                    if max2 < current:
                        max2 = current
                        max_bucketing2 = b

            elif R==2:
                max2 = max
                max_bucketing2 = max_bucketing

        '''print "############################"
        print "OPTIMAL"    
        print "Max likelihood =",max
        '''
        likelihood[algo].append(max/m)
        
        e_max = calc_e(max_bucketing)
        e_max_corrected = e_max
        temp2 = emd_score(e_max_corrected,max_bucketing)

        like_out = max
        score_out = temp2
        score[algo].append(temp2)

        '''print "############################"
        print "OPTIMAL*"    
        print "Max likelihood * =",max_B

        likelihood[algo].append(max_B/m)
        
        e_max_B = calc_e(max_bucketing_B)
        e_max_corrected_B = e_max_B
        temp2 = emd_score(e_max_corrected_B,max_bucketing_B)
        
        score[algo].append(temp2)'''

    elif algo == "EM(*)":
        '''print "############################"
        print "EM(1)"'''
        em_bucketing1 = Return_em_bucketing(1)
        temp = compute_likelihood(em_bucketing1)
        
        em_bucketing_max = em_bucketing1
        em_likelihood_max = temp

        likelihood["EM(1)"].append(temp/m)
        
        e_em1 = calc_e(em_bucketing1)
        e_em_corrected1 = e_em1
        temp2 = emd_score(e_em_corrected1,em_bucketing1)
        score["EM(1)"].append(temp2)

        '''print "############################"
        print "EM(2)"'''
        ##HERE DOING GENERAL EM!
        em_bucketing2 = Return_em_bucketing(2)
        #em_bucketing2 = Return_em_general_bucketing(1)
        temp = compute_likelihood(em_bucketing2)#,True)

        if temp > em_likelihood_max:
            em_bucketing_max = em_bucketing2
            em_likelihood_max = temp
        
        likelihood["EM(2)"].append(temp/m)
        
        e_em2 = calc_e(em_bucketing2)#,True)
        e_em_corrected2 = e_em2
        temp2 = emd_score(e_em_corrected2,em_bucketing2)#,True)
        score["EM(2)"].append(temp2)

        '''print "############################"
        print "EM(3)"'''
        em_bucketing3 = Return_em_bucketing(3)
        temp = compute_likelihood(em_bucketing3)

        if temp > em_likelihood_max:
            em_bucketing_max = em_bucketing3
            em_likelihood_max = temp
        
        likelihood["EM(3)"].append(temp/m)
        e_em3 = calc_e(em_bucketing3)
        e_em_corrected3 = e_em3
        temp2 = emd_score(e_em_corrected3,em_bucketing3)
        score["EM(3)"].append(temp2)

        '''print "############################"
        print "EM(*)"'''
        temp = compute_likelihood(em_bucketing_max)#,max_from_full_EM) #in case max from general EM
        
        likelihood["EM(*)"].append(temp/m)
        e_em_max = calc_e(em_bucketing_max)#,max_from_full_EM)
        e_em_corrected_max = e_em_max
        temp2 = emd_score(e_em_corrected_max,em_bucketing_max)#,max_from_full_EM)
        score["EM(*)"].append(temp2)

    elif algo == "GEN_EM":
        ##HERE DOING GENERAL EM!
        #em_bucketing2 = Return_em_bucketing(2)
        em_bucketing2 = Return_em_general_bucketing(1)
        temp = compute_likelihood(em_bucketing2,True)

        likelihood[algo].append(temp/m)
        
        e_em2 = calc_e(em_bucketing2,True)
        e_em_corrected2 = e_em2
        temp2 = emd_score(e_em_corrected2,em_bucketing2,True)
        score[algo].append(temp2)

    time_end = time.time()
    return time_end - time_start


metric_func = ""

#choose between emd and jsdist for now
#full == true only if passed "f" is f[item] and not f[node] -- only in case of general EM
def emd_score(e,f,full=False):
    global R, m, parents, children, depth, nodes_in_depth, num_bucketings, bucketings, rule
    global n, T, item_M, lattice_M, s_rule, e_rule, s, e_gen, e_calc
    global metric_func
    if metric_func == "emd":
        s = []
        CDF_e = {}
        CDF_e_calc = {}
        for r_true in range(R):
            for r in range(R):
                CDF_e[(r,r_true)] = 0
                CDF_e_calc[(r,r_true)] = 0

        for r_true in range(R):
            for r in range(R):
                #print r, r_true
                if r == 0:
                    CDF_e[(r,r_true)] = e[(r,r_true)]
                    CDF_e_calc[(r,r_true)] = e_calc[r,r_true]
                else:
                    CDF_e[(r,r_true)] += CDF_e[(r-1,r_true)]+e[(r,r_true)]
                    CDF_e_calc[(r,r_true)] = CDF_e_calc[(r-1,r_true)]+e_calc[(r,r_true)]

        sum = 0
        for r_true in range(R):
            s.append(0)
            for r in range(R):
                s[r_true] += math.fabs(CDF_e[(r,r_true)]-CDF_e_calc[(r,r_true)])
            sum += s[r_true]
        #return s
        return sum

    elif metric_func == "jsd":
        return JS_dist(e,f,full )

    elif metric_func == "frac_correct":
        return Frac_correct(e,f,full)

    elif metric_func == "dist_weighted":
        return Dist_wtd(e,f,full)

def Frac_correct(e,f,full=False):
    global R, m, parents, children, depth, nodes_in_depth, num_bucketings, bucketings, rule
    global n, T, item_M, lattice_M, s_rule, e_rule, s, e_gen, e_calc

    if full == False:
        frac_wrong = 0.0
        for i in T:
            if f[item_M[i]] != T[i]:
                frac_wrong += 1.0
                #print item_M[i], f[item_M[i]], T[i]

        frac_wrong /= len(T)
        return frac_wrong
    else:
        frac_wrong = 0.0
        for i in T:
            if f[i] != T[i]:
                frac_wrong += 1.0
                #print item_M[i], f[item_M[i]], T[i]

        frac_wrong /= len(T)
        return frac_wrong

def Dist_wtd(e,f,full=False):
    global R, m, parents, children, depth, nodes_in_depth, num_bucketings, bucketings, rule
    global n, T, item_M, lattice_M, s_rule, e_rule, s, e_gen, e_calc

    if full == False:
        score = 0.0
        for i in T:
            if f[item_M[i]] != T[i]:
                score += math.fabs(f[item_M[i]] - T[i])
                #print item_M[i], f[item_M[i]], T[i]

        score /= len(T)
        return score

    else:
        score = 0.0
        for i in T:
            if f[i] != T[i]:
                score += math.fabs(f[i] - T[i])
                #print item_M[i], f[item_M[i]], T[i]

        score /= len(T)
        return score


def JS_dist(e,f,full=False):
    global R, m, parents, children, depth, nodes_in_depth, num_bucketings, bucketings, rule
    global n, T, item_M, lattice_M, s_rule, e_rule, s, e_gen, e_calc

    e_M = {}
    for r_true in range(R):
        for r in range(R):
            e_M[(r,r_true)] = 0.5*e[(r,r_true)] + 0.5*e_calc[(r,r_true)]

    jsdist = 1 #for pdt of different distances across rows
    jsdist = 0 #for sum of different distances across rows
    for r_true in range(R):
        row_dist = 0
        for r in range(R):
            if e[(r,r_true)] != 0 and e_calc[(r,r_true)] != 0:
                row_dist += 0.5*(e[(r,r_true)]*math.log(e[(r,r_true)]/e_M[(r,r_true)])+e_calc[(r,r_true)]*math.log(e_calc[(r,r_true)]/e_M[(r,r_true)]))
            elif e[(r,r_true)] == 0 and e_calc[(r,r_true)] != 0:
                row_dist += 0.5*(e_calc[(r,r_true)]*math.log(e_calc[(r,r_true)]/e_M[(r,r_true)]))
            elif e[(r,r_true)] != 0 and e_calc[(r,r_true)] == 0:
                row_dist += 0.5*(e[(r,r_true)]*math.log(e[(r,r_true)]/e_M[(r,r_true)]))
            else:
                print "e_calc and e both zero Error"
                sys.exit(0)

        jsdist += row_dist
        #j_dist *= row_dist

    return jsdist


##############################################################
##############################################################
#MAIN FUNCTIONS
##############################################################
##############################################################


def main1():
    global R, m, parents, children, depth, nodes_in_depth, num_bucketings, bucketings, rule
    t1 = time.clock()
    parents.clear() #stores parents of node
    children.clear() #stores children of node
    depth.clear() #stores the depth of a node
    nodes_in_depth.clear() #stores the nodes at depth d
    num_bucketings = 0 #number of valid partial order preserving bucketings = [] #the set of valid partial order preserving bucketings
    bucketings[:] = [] #the set of valid partial order preserving bucketings

    #print "R = ",R,", m = ",m
    construct_lattice()
    #print "Total number of nodes = ",len(depth)
    #print "Height of lattice = ",total_depth()
    #print "Width of lattice = ",max_width()
    #t2 = time.clock()
    #nodes_by_depth(t2-t1)
    #num_nodes_by_depth()
    
    t3 = time.clock()
    enumerate_order_preserving_bucketings()
    t4 = time.clock()
    #print "Time taken to generate bucketings = ",t4-t3,"s"
    #print "Number of bucketings = ",num_bucketings," under rule ",rule
    #print "Writing valid bucketings to file"
    #f = open("Bucketings for R = "+str(R)+", m = "+str(m)+", Rule "+str(rule),"w")
    #f.write("Number of bucketings = "+str(num_bucketings)+"\n")    
    #print "Complete"

#main2 --- for generating s,e,I(n),M
def main2(random_e):
    T.clear() #true values of items
    item_M.clear() #key = item index, value = realization tuple
    lattice_M.clear() #key = lattice node, value = number of items satisfying

    assign_true_value()
    set_error(random_e)
    generate_M()

#Plotting Variables:


likelihood = defaultdict(list)

score = defaultdict(list)

time_taken = defaultdict(list)

likelihood_all = []
score_all = []
time_taken_all = []

#main3 --- for evaluating different bucketings
def main3():
    global R, m, parents, children, depth, nodes_in_depth, num_bucketings, bucketings, rule
    global n, T, item_M, lattice_M, s_rule, e_rule, s, e_gen, e_calc
    global max_workers

    #global likelihood_OPT, likelihood_OPT2
    #global score_OPT, score_OPT2
    #global likelihood_all, score_all

    global e_random_gen_rule

    #global num_trials

    global metric_func


    #for e_rule in [1,2,3,4,5,6]:
    #for e_rule in [1,2,3,4,5,6,7,8]:
    x = []

    #mean in each vertical scatter plot for a given m
    mean_likelihood = defaultdict(list)
    
    #mean in each vertical scatter plot for a given m
    mean_score = defaultdict(list)

    #mean in each vertical scatter plot for a given m
    mean_time = defaultdict(list)

    mean_x = []
    
    #CHANGE HERE DEPENDING ON IF VARYING M OR MAX_WORKER

    #m_range = [1,2,3,4,5,6]
    if R == 2: m_range = [3,4,5,6,7,8,9,10]
    #m_range = [1,2,3]
    #m_range = [3,4,5,6]
    if R == 3: m_range = [2,3,4,5,6]#[2,3,4,5,6]

    max_worker_range = [4,40,400,4000]#,20000,40000]
    # max_worker_range = [1000, 2000, 3000, 4000, 5000]
    # max_worker_range = [10,50,250,1250,6250]

    #num_trials_range = [100,100,10,10]
    num_trials_range = [100,100,10,10,10]
    
    #algo_range = ["OPT", "EM(*)"]
    algo_range = ["OPT", "GEN_EM"]
    #vary = "m"
    vary = "max_workers"
    if vary == "max_workers":
        #algo_range.append("GEN_EM")
        algo_range = ["OPT", "GEN_EM"]

    m = 4
    #max_workers = max(m_range)
    max_workers = 1000

    rd = 0 #round number - to vary num_trials
    for max_workers in max_worker_range:
    #for m in m_range:
        #if vary == "m": max_workers = 1
        main1()

        s_likelihood = {}
        s_score = {}
        s_time = {}
        for algo in algo_range:
            if algo == "EM(*)":
                s_likelihood["EM(1)"] = 0.0
                s_likelihood["EM(2)"] = 0.0
                s_likelihood["EM(3)"] = 0.0
                s_likelihood["EM(*)"] = 0.0

                s_score["EM(1)"] = 0.0
                s_score["EM(2)"] = 0.0
                s_score["EM(3)"] = 0.0
                s_score["EM(*)"] = 0.0

                '''s_time["EM(1)"] = 0.0
                s_time["EM(2)"] = 0.0
                s_time["EM(3)"] = 0.0'''
                s_time["EM(*)"] = 0.0

            else:
                s_likelihood[algo] = 0.0
                s_score[algo] = 0.0
                s_time[algo] = 0.0

        # if vary == "m": num_trials = num_trials_base
        num_trials = num_trials_base
        # elif vary == "max_workers": num_trials = num_trials_range[rd]
        # num_trials = num_trials_base
        rd += 1
        for i in range(num_trials):
            if vary == "m": x.append(m)
            elif vary == "max_worker": x.append(max_workers)
            #main2(0) for old, specific e_rules, main2(1) for random+reasonable worker e matrix, main2(2) for random e matrix
            main2(e_random_gen_rule)
            for algo in algo_range:
                s_time[algo] += compute_algo(algo)

                s_likelihood[algo] += likelihood[algo][len(likelihood[algo])-1] #add last added point for this n
                s_score[algo] += score[algo][len(score[algo])-1] #add last added point for this n

                if algo == "EM(*)":
                    s_likelihood["EM(1)"] += likelihood["EM(1)"][len(likelihood["EM(1)"])-1] #add last added point for this n
                    s_likelihood["EM(2)"] += likelihood["EM(2)"][len(likelihood["EM(2)"])-1] #add last added point for this n
                    s_likelihood["EM(3)"] += likelihood["EM(3)"][len(likelihood["EM(3)"])-1] #add last added point for this n

                    s_score["EM(1)"] += score["EM(1)"][len(score["EM(1)"])-1] #add last added point for this n
                    s_score["EM(2)"] += score["EM(2)"][len(score["EM(2)"])-1] #add last added point for this n
                    s_score["EM(3)"] += score["EM(3)"][len(score["EM(3)"])-1] #add last added point for this n

    
            #x.append(i+1)

        for algo in algo_range:
            s_likelihood[algo] /= num_trials
            mean_likelihood[algo].append(s_likelihood[algo])
            s_score[algo] /= num_trials
            mean_score[algo].append(s_score[algo])
            s_time[algo] /= num_trials
            mean_time[algo].append(s_time[algo])
            if algo == "EM(*)":
                for t in [1,2,3]:
                    tempname = "EM("+(str)(t)+")"
                    s_likelihood[tempname] /= num_trials
                    mean_likelihood[tempname].append(s_likelihood[tempname])
                    s_score[tempname] /= num_trials
                    mean_score[tempname].append(s_score[tempname])

        if vary == "m": mean_x.append(m)
        elif vary == "max_workers": mean_x.append(max_workers)


    print s_time

    #### PLOT LIKELIHOOD
    matplotlib.pyplot.figure()
    leg = []
    for algo in algo_range:
        if algo == "OPT":
            marker_val = '^'
            markersize_val = 12
            linestyle_val = '-'
        elif algo == "GEN_EM" or algo == "EM(*)":
            marker_val = 'v'
            markersize_val = 12
            linestyle_val = '-'

        leg.append(algo)
        matplotlib.pyplot.plot(mean_x, mean_likelihood[algo], linestyle=linestyle_val, linewidth=2, marker=marker_val, markersize=markersize_val)
        if algo == "EM(*)" and vary == "m":
            for t in [1,2,3]:
                marker_val = 'o'
                markersize_val = 9
                linestyle_val = '--'
                temp_name = "EM("+(str)(t)+")"
                matplotlib.pyplot.plot(mean_x,mean_likelihood[temp_name],linestyle=linestyle_val, linewidth=2, marker=marker_val, markersize=markersize_val)
                leg.append(temp_name)

    matplotlib.pyplot.ylabel('(Normalized) Log Likelihood', fontsize=18)
    
    if vary == "m": 
        matplotlib.pyplot.xlabel('m',fontsize=18)
        matplotlib.pyplot.xticks(range(min(mean_x), max(mean_x)+1, 1))
    elif vary == "max_workers": 
        matplotlib.pyplot.xlabel('max_workers',fontsize=18)
        matplotlib.pyplot.xscale('log')
    
    #matplotlib.pyplot.xticks(range(min(mean_x), max(mean_x)+1, 1))
    
    if vary == "m": matplotlib.pyplot.title('Log Likelihood', fontsize=22)
    elif vary == "max_workers": matplotlib.pyplot.title('Log Likelihood', fontsize=22)

    matplotlib.pyplot.legend(leg,prop={'size':18})
    #matplotlib.pyplot.legend(['OPT','EM(1)','EM(2)','EM(3)','EM(*)'],prop={'size':18})
    #matplotlib.pyplot.legend(['OPT','EM(1)','GEN_EM','EM(3)','EM(*)'],prop={'size':18})
    if R == 3:
        matplotlib.pyplot.savefig('rating-like, vary '+vary+'.png')
    elif R == 2:
        matplotlib.pyplot.savefig('filter-like, vary '+vary+'.png')
    else:
        matplotlib.pyplot.savefig('TEMP LIKE.png')

    matplotlib.pyplot.show()
    matplotlib.pyplot.close()
    

    #### PLOT SCORE
    matplotlib.pyplot.figure()
    leg = []
    for algo in algo_range:
        if algo == "OPT":
            marker_val = '^'
            markersize_val = 12
            linestyle_val = '-'
        elif algo == "GEN_EM" or algo == "EM(*)":
            marker_val = 'v'
            markersize_val = 12
            linestyle_val = '-'

        leg.append(algo)
        matplotlib.pyplot.plot(mean_x,mean_score[algo],linestyle=linestyle_val, linewidth=2, marker=marker_val, markersize=markersize_val)
        if algo == "EM(*)" and vary == "m":
            for t in [1,2,3]:
                marker_val = 'o'
                markersize_val = 9
                linestyle_val = '--'
                temp_name = "EM("+(str)(t)+")"
                matplotlib.pyplot.plot(mean_x,mean_score[temp_name],linestyle=linestyle_val, linewidth=2, marker=marker_val, markersize=markersize_val)
                leg.append(temp_name)


    if metric_func == "dist_weighted":
        matplotlib.pyplot.ylabel('Distance weighted score', fontsize=18)
    elif metric_func == "frac_correct":
        matplotlib.pyplot.ylabel('Fraction incorrect', fontsize=18)
    elif metric_func == "emd":
        matplotlib.pyplot.ylabel('EMD Score', fontsize=18)
    elif metric_func == "jsd":
        matplotlib.pyplot.ylabel('JSD Score', fontsize=18)
    
    if vary == "m": 
        matplotlib.pyplot.xlabel('m',fontsize=18)
        matplotlib.pyplot.xticks(range(min(mean_x), max(mean_x)+1, 1))
    elif vary == "max_workers": 
        matplotlib.pyplot.xlabel('max_workers',fontsize=18)
        matplotlib.pyplot.xscale('log')
    
    #matplotlib.pyplot.xticks(range(min(mean_x), max(mean_x)+1, 1))

    if metric_func == "frac_correct" or metric_func == "dist_weighted":
        matplotlib.pyplot.title('Item rating predictions', fontsize=22)
    else:
        matplotlib.pyplot.title('Worker quality predictions', fontsize=22, fontweight='light')

    #matplotlib.pyplot.legend(['OPT','EM(1)','GEN_EM','EM(3)','EM(*)'],prop={'size':18})
    #matplotlib.pyplot.legend(['OPT','EM(1)','EM(2)','EM(3)','EM(*)'],prop={'size':18})
    if R == 2 and vary == "max_workers": matplotlib.pyplot.legend(leg,prop={'size':18},loc='lower right')
    else: matplotlib.pyplot.legend(leg, prop={'size':18}, loc='upper left')

    if R == 3 and metric_func == "dist_weighted":
        matplotlib.pyplot.savefig('rating-dist_wtd, vary '+vary+'.png')

    elif R == 3 and metric_func == "emd" and s_rule == 1:
        matplotlib.pyplot.savefig('rating-emd, vary '+vary+'.png')

        
    elif R == 3 and metric_func == "jsd" and s_rule == 1:
        matplotlib.pyplot.savefig('rating-jsd, vary '+vary+'.png')
    elif R == 3 and metric_func == "jsd" and s_rule == 2:
        matplotlib.pyplot.savefig('rating-jsd,s=2, vary '+vary+'.png')
    elif R == 3 and metric_func == "jsd" and s_rule == 3:
        matplotlib.pyplot.savefig('rating-jsd,s=3, vary '+vary+'.png')
        
    elif R == 2 and metric_func == "emd" and s_rule == 1:
        matplotlib.pyplot.savefig('filter-emd,s=5, vary '+vary+'.png')
    elif R == 2 and metric_func == "emd" and s_rule == 2:
        matplotlib.pyplot.savefig('filter-emd,s=7, vary '+vary+'.png')
    elif R == 2 and metric_func == "emd" and s_rule == 3:
        matplotlib.pyplot.savefig('filter-emd,s=9, vary '+vary+'.png')
        

    elif R == 2 and metric_func == "frac_correct" and s_rule == 1:
        matplotlib.pyplot.savefig('filter-frac_incorrect, vary '+vary+'.png')
    elif R == 2 and metric_func == "frac_correct" and s_rule == 2:
        matplotlib.pyplot.savefig('filter-frac_incorrect,s=7, vary '+vary+'.png')
    elif R == 2 and metric_func == "frac_correct" and s_rule == 3:
        matplotlib.pyplot.savefig('filter-frac_incorrect,s=9, vary '+vary+'.png')

    elif R == 2 and metric_func == "jsd" and s_rule ==1:
        matplotlib.pyplot.savefig('filter-jsd, vary '+vary+'.png')
    elif R == 2 and metric_func == "jsd" and s_rule ==2:
        matplotlib.pyplot.savefig('filter-jsd,s=7, vary '+vary+'.png')
    elif R == 2 and metric_func == "jsd" and s_rule ==3:
        matplotlib.pyplot.savefig('filter-jsd,s=9, vary '+vary+'.png')

    else:
        matplotlib.pyplot.savefig('TEMP METRIC.png')

    matplotlib.pyplot.show()
    matplotlib.pyplot.close()

    #### PLOT TIME
    matplotlib.pyplot.figure()
    leg = []
    for algo in algo_range:
        if algo == "OPT":
            marker_val = '^'
            markersize_val = 12
            linestyle_val = '-'
        elif algo == "GEN_EM" or algo == "EM(*)":
            marker_val = 'v'
            markersize_val = 12
            linestyle_val = '-'

        leg.append(algo)
        matplotlib.pyplot.plot(mean_x, mean_time[algo], linestyle=linestyle_val, linewidth=2, marker=marker_val, markersize=markersize_val)

    matplotlib.pyplot.ylabel('Time taken', fontsize=18)

    if vary == "m":
        matplotlib.pyplot.xlabel('m',fontsize=18)
        matplotlib.pyplot.xticks(range(min(mean_x), max(mean_x)+1, 1))
    elif vary == "max_workers": 
        matplotlib.pyplot.xlabel('max_workers', fontsize=18)
        #matplotlib.pyplot.xscale('log')

    #matplotlib.pyplot.xticks(range(min(mean_x), max(mean_x)+1, 1))

    matplotlib.pyplot.title('Time taken', fontsize=22)

    matplotlib.pyplot.legend(leg, prop={'size': 18}, loc='upper left')
    #matplotlib.pyplot.legend(['OPT','EM(1)','EM(2)','EM(3)','EM(*)'],prop={'size':18})
    #matplotlib.pyplot.legend(['OPT','EM(1)','GEN_EM','EM(3)','EM(*)'],prop={'size':18})
    if R == 3:
        matplotlib.pyplot.savefig('rating-time, vary '+vary+'.png')
    elif R == 2:
        matplotlib.pyplot.savefig('filter-time, vary '+vary+'.png')
    else:
        matplotlib.pyplot.savefig('TEMP TIME.png')

    matplotlib.pyplot.show()
    matplotlib.pyplot.close()

    # write all output to file
    all_out_file = 'basic-synthetic.out.txt'
    with open(all_out_file, "a+") as fp:
        fp.write("---------------------")
        # params
        fp.write('{},{},{},{}\n'.format(vary, R, metric_func, num_trials_base))
        fp.write('{},{},{},{}\n'.format(m, m_range, max_workers, max_worker_range))
        # x
        fp.write('{}\n'.format(mean_x))
        for algo in algo_range:
            # like
            fp.write('{}\n'.format(mean_likelihood[algo]))
            # score
            fp.write('{}\n'.format(mean_score[algo]))
            # time
            fp.write('{}\n'.format(mean_time[algo]))

    print "############################"


metric_func = "frac_correct"
#metric_func = "jsd"
#metric_func = "emd"
#metric_func = "dist_weighted"

R = 2 #number of ratings - 1,2,...,R
m = 3 #num qns per item


s_rule = 1 #even dist
#s_rule = 2 #0.7 for filter
#s_rule = 3 #0.9 for filter

n = 1024 #number of items
max_workers = 1024 #maximum worker pool, although each item still gets 'm' answers

num_trials_base = 1

#e_random_gen_rule = 0 #uses old e_rules
e_random_gen_rule = 1 #generates random worker matrix assuming 'good' worker behaviour
#e_random_gen_rule = 2 #generates unconstrained random worker matrix
#e_random_gen_rule = 3 #two worker classes, 0.7, 0.9, workers randomly assigned one of the two

#num_trials = 10

t5 = time.clock()
#print "\n\n----------------------------------------------------------\nNow generating item set, selectivity, error, realization\n----------------------------------------------------------\n\n"
#main2()
print "\n\n----------------------------------------------------------\nNow computing likelihoods of different mappings\n----------------------------------------------------------\n\n"
main3()
t6 = time.clock()
print "Total time = ",t6-t5,"s"

#return (1 if n1 > n2), (-1 if n1 < n2), and (0 if incomparable)
#def dominates(node1,node2):1
