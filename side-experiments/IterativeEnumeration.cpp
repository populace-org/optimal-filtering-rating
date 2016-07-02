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
#include<list>
#include<pthread.h>
using namespace std;

int R = 3; //number of buckets
int m = 3; //number of workers per item
int num_nodes = 0; //number of items

int prune = 1; //prune set of mappings using heuristic

map< int, vector<int> > node_at_index; //indexes nodes with int id
map< vector<int>, int > index_of_node; //id of a given node

map< int, vector<int> > parents; //stores parents of node
map< int, vector<int> > children; //stores children of node
map<int, int> depth;//stores the depth of a node
map<int, vector<int> > nodes_in_depth; //stores the nodes at depth d

//AFTER REORDERING
map< int, int> new_index;
map< int, int> original_index;

int num_bucketings = 0; //number of valid partial order preserving bucketings
vector< map< int, int > > bucketings; //the set of valid partial order preserving bucketings

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

//reorder dag to give increasing index with increasing depth
void reorder_dag()
{
	int t = 0;
	for (int d=0; d<total_depth(); d++)
	{
		for (int i = 0; i < nodes_in_depth[d].size(); i++)
		{
			new_index[nodes_in_depth[d][i]] = t;
			original_index[t] = nodes_in_depth[d][i];
			t++;
		}
	}
}

//recursive call - BFS to construct dag
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
					node_at_index[num_nodes] = new_node;
					index_of_node[new_node] = num_nodes;
					num_nodes++;
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
void construct_dag()
{
    cout<<"Constructing DAG\n";
    vector<int> node;
    node.push_back(m);
    for(int i = 0; i<(R-1); i++)
        node.push_back(0);

    depth[num_nodes] = 0;
	node_at_index[num_nodes] = node;
	index_of_node[node] = num_nodes;
	num_nodes++;
    
    add_next(node,0); //recursive function call to construct dag
    
    //Lattice constructed - now index by depth:
    index_by_depth();
	
	reorder_dag();
    
    cout<<"DAG Constructed"<<endl;
}

//Enumerate all possible bucketings and store in bucketings
void enumerate_consistent_mappings()
{
	map <int, int> new_mapping;
	for (int r=0; r<R; r++)
	{
		new_mapping.clear();
		new_mapping[0] = r;
		bucketings.push_back(new_mapping);
	}
	
	new_mapping.clear();
	
	//each iteration inserts node i into all valid mappings
	vector< map<int, int> > new_bucketings; //will store new set at end of iteration
	
	
	map< int, int > current_mapping; //holds current bucket to be expanded
		
	
	for (int k=1; k<num_nodes; k++)
	{
		num_bucketings = bucketings.size();
		cout<<"Number of bucketings before node "<<k<<" = "<<num_bucketings<<endl;
		clock_t start = clock();
	
		//k iterates in order of new index - layer by layer
		//i holds corresponding old index value
		int i = original_index[k];
	
		//cout<<"Number of mappings = "<<bucketings.size()<<endl;
		
		new_bucketings.clear();
		
		for(int b=0; b < bucketings.size(); b++)		
		{
			current_mapping.clear();
			current_mapping = bucketings[b];
			//bucketings.pop_back();
			int min_valid = 0;
			
			for(int j=0; j<parents[i].size();j++)
			{
				int curr_parent = parents[i][j];
				if (current_mapping[curr_parent] > min_valid)
					min_valid = current_mapping[curr_parent];
					
				//to reduce space usage of bucketings (only counting mappings, not enumerating) -- if all children of a parent of the new node i have been seen, can delete parent -- only keep frontier of dag that is necessary to grow further
				bool delete_parent = true;
				for(int l=0; l<children[parents[i][j]].size(); l++)
				{
					int curr_child = children[parents[i][j]][l];
					if ((curr_child!=i) && (bucketings[b].find(curr_child) == bucketings[b].end()))
					{
						delete_parent = false;
						break;
					}
				}
				
				if (delete_parent)
				{
					bucketings[b].erase(curr_parent);
					current_mapping.erase(curr_parent);
				}
			}
			
			new_mapping.clear();
			new_mapping = current_mapping;
			
			for(int r=min_valid; r<R; r++)
			{
				new_mapping[i] = r;
				new_bucketings.push_back(new_mapping);
			}
			
			//cout<<"Printing old and new bucketings"<<endl;
		}
		bucketings.clear();
		bucketings = new_bucketings;
		
		clock_t end = clock();
		double execution_time = ((double)(end-start))/((double)CLOCKS_PER_SEC);
		cout<<"Time for node "<<k<<" = "<<execution_time<<" seconds"<<endl;
		cout<<"Time per bucketing for node "<<k<<" = "<<execution_time/((double)num_bucketings)<<" seconds"<<endl;
		cout<<"_______________________________________"<<endl;
	}
	
	num_bucketings = bucketings.size();
}

int main()
{
	cout <<"Enter R"<<endl;
	cin>>R;
	cout<<"Enter m"<<endl;
	cin>>m;
	clock_t start = clock();
	srand((unsigned)time(NULL)); //seeding the pseudo-random generator
	construct_dag();
    cout<<"Total number of nodes = "<<depth.size()<<endl;
    cout<<"Height of DAG = "<<total_depth()<<endl;
    cout<<"Width of DAG = "<<max_width()<<endl;
	
	cout<<"________________________________"<<endl;
	
	/*
	for (int k=0; k<num_nodes; k++)
	{
		//k iterates in order of new index - layer by layer
		//i holds corresponding old index value
		int i = original_index[k];
		cout<<"Node "<<k<<" = [ ";
		for(int r=0; r<R; r++)
			cout<<node_at_index[i][r]<<" ";
		cout<<"]"<<endl;
		cout<<"Parents = ";
		for(int p=0; p<parents[i].size(); p++)
		{
			cout<<"[ ";
			for(int r=0; r<R; r++)
				cout<<node_at_index[parents[i][p]][r]<<" ";
			cout<<"], ";
		}
		cout<<endl;
		cout<<"Children = ";
		for(int p=0; p<children[i].size(); p++)
		{
			cout<<"[ ";
			for(int r=0; r<R; r++)
				cout<<node_at_index[children[i][p]][r]<<" ";
			cout<<"], ";
		}
		cout<<"\n________________________________"<<endl;
	}*/
	
	
	enumerate_consistent_mappings();
    cout<<"Number of bucketings = "<<num_bucketings<<endl;
	clock_t end = clock();
	double execution_time = ((double)(end-start))/((double)CLOCKS_PER_SEC);
	cout<<"Total time = "<<execution_time<<" seconds"<<endl;
	cout<<"________________________________"<<endl;
	
	return 0;
}
