#include<algorithm>
#include<map>
#include<iostream>
#include<fstream>
#include<string>
#include<stdlib.h>
#include<time.h>
#include<sstream>
#include<float.h>
#include<vector>
using namespace std;

int R = 3; //number of buckets
int m = 3; //number of workers per item
int n = 1000; //number of items

map< vector<int>, vector< vector<int> > > parents; //stores parents of node
map< vector<int>, vector< vector<int> > > children; //stores children of node
map<vector<int>, int> depth;//stores the depth of a node
map<int, vector< vector<int> > > nodes_in_depth; //stores the nodes at depth d
int num_bucketings = 0; //number of valid partial order preserving bucketings
vector< map< vector<int>, int > > bucketings; //the set of valid partial order preserving bucketings

int total_depth()
{
	int max_sum = R*m;
	int min_sum = m;
	int depth = max_sum-min_sum+1;
	return depth;
}

void index_by_depth()
{
    cout<<"Indexing by depth"<<endl;
	//cout<<"size = "<<depth.size()<<endl;
	for( map<vector<int>, int>::iterator ii=depth.begin(); ii!=depth.end(); ++ii)
	{
		//cout<<"second = "<<(*ii).second<<endl;
		nodes_in_depth[(*ii).second].push_back((*ii).first);
		//cout << (*ii).first << ": " << (*ii).second << endl;
	}
    cout<<"Indexing complete"<<endl;
}

int max_width()
{
    int w = 0;
	int d = 0;
    while(d < total_depth())
    {
		if (w < nodes_in_depth[d].size())
		{
			//cout<<"here"<<endl;
		    w = nodes_in_depth[d].size();
		}
		d++;
	}
    return w;
}

//recursive call - BFS to construct lattice
void add_next(vector<int> node, int d)
{
	//cout<<"0"<<endl;
    vector<int> last_node;
    for(int i = 0; i<(R-1); i++)
        last_node.push_back(0);
    last_node.push_back(m);
    
    /*if (node == last_node)
        //children[node] = []
        return;*/
	if (node!=last_node)
	{
		map< vector<int>, int > dont_add;
		for(int i = 0; i<(R-1); i++)
		{
			if (node[i] > 0)
			{
				//cout<<"1 "<<i<<endl;
				vector<int> new_node = node;
				new_node[i] -= 1;
				new_node[i+1] += 1;
				//cout<<"node[i] = "<<node[i]<<endl;
				//cout<<"new_node[i] = "<<new_node[i]<<endl;
				children[node].push_back(new_node);
				parents[new_node].push_back(node);

				if (depth.find(new_node)==depth.end()) //not(new_node in depth))
				{
					//print "Added", new_node
					depth[new_node] = d + 1;
					//cout<<"2 "<<i<<endl;
				}
				
				else //this node as already been seen by a path - correctly update depth
				{
					depth[new_node] = min(d+1,depth[new_node]);
					dont_add[new_node]= 1;
					//cout<<"3 "<<i<<endl;
				}
			}
		}
		
		//cout<<"child size = "<<children[node].size()<<endl;
		
		/*int a = 0;
		int k=0;
		while (k < 2)
		{
			cout<<"a = "<<a<<endl;
			a++;
			k++;
		}
		cout<<"a = "<<a<<endl;*/

		int j = 0;
		while(j<children[node].size())
		{
			//cout<<"4 "<<j<<endl;
			if (dont_add.find(children[node][j])==dont_add.end()) //not(new_node in dont_add):
				add_next(children[node][j],depth[children[node][j]]);
			j++;
		}
		
		/*for (int j=0; j++; j<children[node].size())
		{
			cout<<"4 "<<j<<endl;
			if (dont_add.find(children[node][j])==dont_add.end()) //not(new_node in dont_add):
				add_next(children[node][j],depth[children[node][j]]);
		}*/
		
		//cout<<"5"<<endl;
	}
}

//construct the lattice
void construct_lattice()
{
    cout<<"Constructing lattice\n";
    vector<int> node;// = new vector<int>();
    node.push_back(m);
    for(int i = 0; i<(R-1); i++)
        node.push_back(0);
    //parents[node] = new vector< vector<int> >();
    depth[node] = 0;
    
    add_next(node,depth[node]); //recursive function call to construct lattice
    
    //Lattice constructed - now index by depth:
    index_by_depth();
    
    cout<<"Lattice Constructed"<<endl;
}

void all_combinations_next_depth(map< vector<int>, int >curr_assign,int completed_depth);

//assigned has node-rating assignments for some nodes
//to_assign has list of remaining nodes
//curr_assign has assignments of all parent (ancestor) nodes    
void all_combinations(map< vector<int>, int >assigned, vector< vector<int> >to_assign, map< vector<int>, int >curr_assign, int curr_depth)
{
    //print "Doing depth ",curr_depth
    //print "assigned =",assigned,"\nto assign = ",to_assign,"\ncurr assign = ",curr_assign
    if (to_assign.size() == 0)
	{
		for( map<vector<int>, int>::iterator ii=assigned.begin(); ii!=assigned.end(); ++ii)
		{
			curr_assign[(*ii).first]=(*ii).second;
		}
        /*for (node,val) in assigned:
            curr_assign[node] = val*/
        //print "completed", curr_assign
        //print curr_depth
        all_combinations_next_depth(curr_assign, curr_depth);
	}
    else
	{
        vector<int> node = to_assign.back(); //all possible values for next node
		to_assign.pop_back();
        //print "next = ",node,"so far = ",curr_assign
        int max_valid = R-1;
        if (parents[node].size()!=0)
		{
		
			for(int i=0; i<parents[node].size();i++)
			{
				vector<int> temp_node = parents[node][i];
				if (curr_assign[temp_node] < max_valid)
					max_valid = curr_assign[temp_node];
			}
		
            /*for (p in parents[node])
			{
                if curr_assign[p] < max_valid:
                    max_valid = curr_assign[p]
			}*/
		}
		
        map< vector<int>, int > assigned_old = assigned;
        vector< vector<int> > to_assign_old = to_assign;
        map< vector<int>, int > curr_assign_old = curr_assign;
        int curr_depth_old = curr_depth;
        
		for (int r=0; r<(max_valid+1);r++)
		{
			assigned[node] = r;
			all_combinations(assigned, to_assign, curr_assign, curr_depth);
			assigned = assigned_old;
			to_assign = to_assign_old;
			curr_assign = curr_assign_old;
			curr_depth = curr_depth_old;
		}
	}
}

void all_combinations_next_depth(map< vector<int>, int >curr_assign,int completed_depth)
{
    if (completed_depth == total_depth() - 1) //one valid bucketing complete
	{
        num_bucketings += 1;
        bucketings.push_back(curr_assign);
	}
    else
	{
        map< vector<int>, int > assigned;
        vector< vector<int> > to_assign = nodes_in_depth[(completed_depth+1)];
        all_combinations(assigned, to_assign, curr_assign, completed_depth+1);
	}
}

void enumerate_order_preserving_bucketings()
{
    cout<<"Beginning enumeration"<<endl;
    int completed_depth = -1;
    map< vector<int>, int > curr_assign;
    all_combinations_next_depth(curr_assign,completed_depth);

    cout<<"Enumeration ended"<<endl;
}

int main()
{
	cout <<"Enter R"<<endl;
	cin>>R;
	cout<<"Enter m"<<endl;
	cin>>m;
	clock_t start = clock();
	srand((unsigned)time(NULL)); //seeding the pseudo-random generator
	construct_lattice();
    cout<<"Total number of nodes = "<<depth.size()<<endl;
    cout<<"Height of lattice = "<<total_depth()<<endl;
    cout<<"Width of lattice = "<<max_width()<<endl;
	enumerate_order_preserving_bucketings();
    cout<<"Number of bucketings = "<<num_bucketings<<endl;
	clock_t end = clock();
	double execution_time = ((double)(end-start))/((double)CLOCKS_PER_SEC);
	cout<<"Total time = "<<execution_time<<" seconds"<<endl;
	cout<<"________________________________"<<endl;
	//getchar();
	
	/*vector<int> node;// = new vector<int>();
    node.push_back(m);
    for(int i = 0; i<(R-1); i++)
        node.push_back(0);
    //parents[node] = new vector< vector<int> >();
    depth[node] = 0;

	cout<<"Node = "<<node[0]<<" "<<node[1]<<" "<<node[2]<<" "<<endl;*/
	return 0;
}

