from graph import KnowledgeGraph
import pandas as pd
import csv
import json
from igraph import * 


###Read in all files, outputs triples and labels as a df
def process_pkl_files(triples_file,labels_file):

    triples_df = pd.read_csv(triples_file,sep = '	')
    triples_df.columns.str.lower()

    #labels = pd.read_csv(labels_file, sep = '	')
    #labels.columns.str.lower()
    
    
    # In order to show all the labels available in the labels_file tab deliminated txt file, read the file with pandas fixed-width lines reader
    # (this will destroy the frame of the file though!!!)
    all_labels = pd.read_fwf(labels_file)
    print("The total number of labels is", len(all_labels))
    
    '''extract the labels from the fwf_labels file.
    This will extract the linsk without the "<>" on border on each string  ''' 
    labels = []
    row_num = 0
    for i in labels_fwf.iloc[:,0]:
        i = i.split('<')
        i= i[1].split('>')
        labels_from_fwf.append(i[0])
        row_num +=1

    return triples_df,labels

#Creates igraph object and a list of nodes
def create_igraph_graph(edgelist_df,labels):

    edgelist_df = edgelist_df[['subject', 'object', 'predicate']]

#    uri_labels = labels[['Identifier']]
# Different uri column in PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_NodeLabels.txt. 
    uri_labels = labels[['entity_uri']]

    g = Graph.DataFrame(edgelist_df,directed=True,use_vids=False)

    g_nodes = g.vs()['name']

    return g,g_nodes 

# Wrapper function
def create_pkl_graph(triples_file,labels_file):

    triples_df,labels = process_pkl_files(triples_file,labels_file)

    g_igraph,g_nodes_igraph = create_igraph_graph(triples_df,labels)

    # Created a PKL class instance
    pkl_graph = KnowledgeGraph(triples_df,labels,g_igraph,g_nodes_igraph)

    return pkl_graph
