from inputs import *
from create_graph import create_graph
from assign_nodes import *
from create_subgraph import subgraph_prioritized_path_cs
from create_subgraph import subgraph_prioritized_path_pdp
from visualize_subgraph import output_visualization
from evaluation import *

def main():

    input_dir,output_dir,kg_type,embedding_dimensions,weights,search_type,pdp_weight = generate_arguments()

    triples_list_file,labels_file,input_file = get_graph_files(input_dir,output_dir, kg_type)

    print("Creating knowledge graph object from inputs.....")

    g = create_graph(triples_list_file,labels_file, kg_type)
    
    print("Mapping between user inputs and KG nodes.......")
    
    s = interactive_search_wrapper(g, input_file, output_dir)

    print("Mapping complete")
    print(s)

    print("Finding subgraph using user input and KG embeddings for Cosine Similarity......")
    
    subgraph_cs,path_total_cs = subgraph_prioritized_path_cs(s,g.igraph,g.igraph_nodes,g.labels_all,g.edgelist,weights,search_type,triples_list_file,output_dir,input_dir,embedding_dimensions)

    print("Outputting CS visualization......")

    cs_noa_df = output_visualization(s,subgraph_cs,output_dir+'/CosineSimilarity')

    print("Finding subgraph using user input for PDP......")

    subgraph_pdp,path_pdp = subgraph_prioritized_path_pdp(s,g.igraph,g.igraph_nodes,g.labels_all,g.edgelist,weights,search_type,pdp_weight,output_dir)
    
    print("Outputting PDP visualization......")

    pdp_noa_df = output_visualization(s,subgraph_pdp,output_dir+'/PDP')

if __name__ == '__main__':
    main()