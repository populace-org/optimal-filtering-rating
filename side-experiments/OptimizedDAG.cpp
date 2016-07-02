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
#include<pthread.h>
using namespace std;

int R = 3; //number of buckets
int m = 3; //number of workers per item
int n = 1000; //number of items

int prune = 1; //prune set of mappings using heuristic

map< int, vector<int> > node_at_index; //indexes nodes with int id
map< vector<int>, int > index_of_node; //id of a given node

map< int, vector<int> > parents; //stores parents of node
map< int, vector<int> > children; //stores children of node
map<int, int> depth;//stores the depth of a node
map<int, vector<int> > nodes_in_depth; //stores the nodes at depth d
int num_bucketings = 0; //number of valid partial order preserving bucketings
vector< map< int, int > > bucketings; //the set of valid partial order preserving bucketings

int node_counter = 0; //id for nodes in lattice

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

	for( map<int, int>::iterator ii=depth.begin(); ii!=depth.end(); ++ii)
	{
		nodes_in_depth[(*ii).second].push_back((*ii).first);
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
		    w = nodes_in_depth[d].size();
		}
		d++;
	}
    return w;
}

//recursive call - BFS to construct lattice
void add_next(vector<int> node, int d)
{
    vector<int> last_node;
    for(int i = 0; i<(R-1); i++)
        last_node.push_back(0);
    last_node.push_back(m);
    
	if (node!=last_node)
	{
		map< int, int > dont_add;
		for(int i = 0; i<(R-1); i++)
		{
			if (node[i] > 0)
			{
				vector<int> new_node = node;
				new_node[i] -= 1;
				new_node[i+1] += 1;
				
				if (index_of_node.find(new_node)==index_of_node.end()) //node not seen before, need to index
				{
					node_at_index[node_counter] = new_node;
					index_of_node[new_node] = node_counter;
					node_counter++;
				}
				
				children[index_of_node[node]].push_back(index_of_node[new_node]);
				parents[index_of_node[new_node]].push_back(index_of_node[node]);

				if (depth.find(index_of_node[new_node])==depth.end()) //not(new_node in depth))
				{
					depth[index_of_node[new_node]] = d + 1;
				}
				
				else //this node as already been seen by a path - correctly update depth
				{
					depth[index_of_node[new_node]] = min(d+1,depth[index_of_node[new_node]]);
					dont_add[index_of_node[new_node]]= 1;
				}
			}
		}
		
		int j = 0;
		while(j<children[index_of_node[node]].size())
		{
			if (dont_add.find(children[index_of_node[node]][j])==dont_add.end()) //not(new_node in dont_add):
				add_next(node_at_index[children[index_of_node[node]][j]],depth[children[index_of_node[node]][j]]);
			j++;
		}
	}
}

//construct the lattice
void construct_lattice()
{
    cout<<"Constructing lattice\n";
    vector<int> node;
    node.push_back(m);
    for(int i = 0; i<(R-1); i++)
        node.push_back(0);

    depth[node_counter] = 0;
	node_at_index[node_counter] = node;
	index_of_node[node] = node_counter;
	node_counter++;
    
    add_next(node,0); //recursive function call to construct lattice
    
    //Lattice constructed - now index by depth:
    index_by_depth();
    
    cout<<"Lattice Constructed"<<endl;
}



void all_combinations_next_depth(map< int, int >curr_assign,int completed_depth);

//assigned has node-rating assignments for some nodes in next depth
//to_assign has list of remaining nodes in next depth
//assigned + to_assign == nodes being explored in next depth
//curr_assign has assignments of all parent (ancestor) nodes (upper layers)
void all_combinations(map< int, int >assigned, vector< int >to_assign, map< int, int >curr_assign, int curr_depth)
{
    if (to_assign.size() == 0)
	{
		for( map<int, int>::iterator ii=assigned.begin(); ii!=assigned.end(); ++ii)
		{
			curr_assign[(*ii).first]=(*ii).second;
		}
        
		all_combinations_next_depth(curr_assign, curr_depth);
	}
    else
	{
        int node = to_assign.back(); //all possible values for next node
		to_assign.pop_back();
        
        int max_valid = R-1;
        if (parents[node].size()>0)
		{
			//assume all parents have been assigned, and now assigning all possible buckets for child
		
			for(int i=0; i<parents[node].size();i++)
			{
				int temp_node = parents[node][i];
				if (curr_assign[temp_node] < max_valid)
					max_valid = curr_assign[temp_node];
			}
		}
		
        map< int, int > assigned_old = assigned;
        vector< int > to_assign_old = to_assign;
        map< int, int > curr_assign_old = curr_assign;
        int curr_depth_old = curr_depth;

		if (prune == 1)
		{
			int posn = -1;
			for(int i=0; i<R; i++)
				if (node_at_index[node][i] == m)
					posn = i;
			
			if (posn != -1)
			{
				assigned[node] = R-1-posn;
				all_combinations(assigned, to_assign, curr_assign, curr_depth);
				assigned = assigned_old;
				to_assign = to_assign_old;
				curr_assign = curr_assign_old;
				curr_depth = curr_depth_old;

			}
			
			else
			{
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
		
		else
		{
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
}

void all_combinations_next_depth(map< int, int >curr_assign,int completed_depth)
{
    if (completed_depth == total_depth() - 1) //one valid bucketing complete
	{
        num_bucketings += 1;
        bucketings.push_back(curr_assign);
	}
    else
	{
        map< int, int > assigned;
        vector< int > to_assign = nodes_in_depth[(completed_depth+1)];
        all_combinations(assigned, to_assign, curr_assign, completed_depth+1);
	}
}

void enumerate_order_preserving_bucketings()
{
    cout<<"Beginning enumeration"<<endl;
    int completed_depth = -1;
    map< int, int > curr_assign;
    all_combinations_next_depth(curr_assign,completed_depth);

    cout<<"Enumeration ended"<<endl;
}


int main()
{
	cout <<"Enter R"<<endl;
	cin>>R;
	cout<<"Enter m"<<endl;
	cin>>m;
	cout<<"Do you wish to prune? Enter 0/1"<<endl;
	cin>>prune;
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
	
	return 0;
}

