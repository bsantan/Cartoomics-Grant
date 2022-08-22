from graph_embeddings import Embeddings
from paths import *
import numpy as np
import pandas as pd
from scipy import spatial
from scipy.spatial import distance
from collections import defaultdict



#Go from label to entity_uri (for PKL original labels file) or Label to Idenifier (for microbiome PKL)
def get_uri(labels,value):

    uri = labels.loc[labels['Label'] == value,'Identifier'].values[0]
    
    return uri

def get_label(labels,value):

    label = labels.loc[labels['Identifier'] == value,'Label'].values[0]
    
    return label


def get_key(dictionary,value):

    for key, val in dictionary.items():
        if val == value:
            return key

def define_path_triples(g_nodes,triples_df,path_nodes,search_type):

    #Dict to store all dataframes of shortest mechanisms for this node pair
    mechanism_dfs = {}
    #Keep track of # of mechanisms generated for this node pair in file name for all shortest paths
    count = 1 

    #When there is no connection in graph, path_nodes will equal 1 ([[]])
    if len(path_nodes[0]) != 0:
        for p in range(len(path_nodes)):
            n1 = g_nodes[path_nodes[p][0]]  
            for i in range(1,len(path_nodes[p])):
                n2 = g_nodes[path_nodes[p][i]]
                if search_type.lower() == 'all':
                    #Try first direction which is n1 --> n2
                    df = triples_df.loc[(triples_df['subject'] == n1) & (triples_df['object'] == n2)]
                    if len(df) == 0:
                        #If no results, try second direction which is n2 --> n1
                        df = triples_df.loc[(triples_df['object'] == n1) & (triples_df['subject'] == n2)]
                elif search_type.lower() == 'out':
                    #Only try direction n1 --> n2
                    df = triples_df.loc[(triples_df['subject'] == n1) & (triples_df['object'] == n2)]
                df = df.reset_index(drop=True)
                n1 = n2

        #For shortest path search
        if len(path_nodes) == 1:
            #Generate df
            df.columns = ['S','P','O']
            return df

        #For all shortest path search
        else:
            #Generate df
            df.columns = ['S','P','O']
            mechanism_dfs['mech#_'+str(count)] = df
            count += 1

    if len(path_nodes) > 1:
        return mechanism_dfs

def find_all_shortest_paths(start_node,end_node,graph,g_nodes,labels_all,triples_df,weights,search_type):

    node1 = get_uri(labels_all,start_node)
    node2 = get_uri(labels_all,end_node)

    #Add weights if specified
    if weights:
        w = graph.es["weight"]
    else:
        w = None

    #Dict to store all dataframes of shortest mechanisms for this node pair
    mechanism_dfs = {}

    #list of nodes
    path_nodes = graph.get_all_shortest_paths(v=node1, to=node2, weights=w, mode=search_type)

    #Dictionary of all triples that are shortest paths, not currently used
    mechanism_dfs = define_path_triples(g_nodes,triples_df,path_nodes,search_type)
    
    return path_nodes

def get_embedding(emb,node):

    embedding_array = emb[str(node)]
    embedding_array = np.array(embedding_array)

    return embedding_array

def calc_cosine_sim(emb,path_nodes,g_nodes,triples_df,search_type,labels_all):

    target_emb = get_embedding(emb,path_nodes[0][len(path_nodes[0])-1])

    #Dict of all embeddings to reuse if they exist
    embeddings = defaultdict(list)

    #List of total cosine similarity for each path in path_nodes, should be same length as path_nodes
    paths_total_cs = []

    for l in path_nodes:
        cs = 0
        for i in range(0,len(l)-1):
            if l[i] not in list(embeddings.keys()):
                e = get_embedding(emb,l[i])
                embeddings[l[i]] = e
            else:
                e = embeddings[l[i]]
            cs += 1 - spatial.distance.cosine(e,target_emb)
        paths_total_cs.append(cs)

    chosen_path_nodes_cs = select_path(paths_total_cs,path_nodes)

    #Will only return 1 dataframe
    df = define_path_triples(g_nodes,triples_df,chosen_path_nodes_cs,search_type)

    df = convert_to_labels(df,labels_all)

    return df

def calc_pdp(path_nodes,graph,w,g_nodes,triples_df,search_type):

    #List of pdp for each path in path_nodes, should be same length as path_nodes
    paths_pdp = []

    for l in path_nodes:
        pdp = 1
        for i in range(0,len(l)-1):
            dp = graph.degree(l[i],mode='all',loops=True)
            dp_damped = pow(dp,-w)
            pdp = pdp*dp_damped

        paths_pdp.append(pdp)

    chosen_path_nodes_pdp = select_path(paths_pdp,path_nodes)

    #Will only return 1 dataframe
    df = define_path_triples(g_nodes,triples_df,chosen_path_nodes_pdp,search_type)

    df = convert_to_labels(df,labels_all)

    return df

def select_path(value_list,path_nodes):

    #Get max cs from total_cs_path, use that idx of path_nodes then create mechanism
    max_index = value_list.index(max(value_list))
    #Must be list of lists for define_path_triples function
    chosen_path_nodes = [path_nodes[max_index]]

    return chosen_path_nodes

def convert_to_labels(df,labels_all):

    for i in range(len(df)):
        df.iloc[i].loc['S'] = labels_all.loc[labels_all['Identifier'] == df.iloc[i].loc['S'],'Label'].values[0]
        df.iloc[i].loc['P'] = labels_all.loc[labels_all['Identifier'] == df.iloc[i].loc['P'],'Label'].values[0]
        df.iloc[i].loc['O'] = labels_all.loc[labels_all['Identifier'] == df.iloc[i].loc['O'],'Label'].values[0]

    df = df.reset_index(drop=True)
    return df

# Wrapper functions
#Returns the path as a dataframe of S/P/O of all triples' labels within the path
def find_shortest_path(start_node,end_node,graph,g_nodes,labels_all,triples_df,weights,search_type):

    node1 = get_uri(labels_all,start_node)
    node2 = get_uri(labels_all,end_node)

    #Add weights if specified
    if weights:
        w = graph.es["weight"]
    else:
        w = None

    #list of nodes
    path_nodes = graph.get_shortest_paths(v=node1, to=node2, weights=w, mode=search_type)

    df = define_path_triples(g_nodes,triples_df,path_nodes,search_type)

    df = convert_to_labels(df,labels_all)

    return df

def prioritize_path_cs(start_node,end_node,graph,g_nodes,labels_all,triples_df,weights,search_type,triples_file,output_dir,node2vec_script_dir,embedding_dimensions):

    path_nodes = find_all_shortest_paths(start_node,end_node,graph,g_nodes,labels_all,triples_df,False,'all')

    e = Embeddings(triples_file,output_dir,node2vec_script_dir,embedding_dimensions)
    emb = e.generate_graph_embeddings()

    df = calc_cosine_sim(emb,path_nodes,g_nodes,triples_df,search_type,labels_all)

    return df

def prioritize_path_pdp(start_node,end_node,graph,g_nodes,labels_all,triples_df,weights,search_type,pdp_weight):

    path_nodes = find_all_shortest_paths(start_node,end_node,graph,g_nodes,labels_all,triples_df,False,'all')

    df = calc_pdp(path_nodes,graph,pdp_weight,g_nodes,triples_df,search_type)

    return df
