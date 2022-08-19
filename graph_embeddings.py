import os
from gensim.models import Word2Vec
from gensim.models import KeyedVectors
import json

class Embeddings:

    def __init__(self, triples_file,output_dir,node2vec_script_dir,embedding_dimensions):
        self.triples_file = triples_file
        self.output_dir = output_dir
        self.node2vec_script_dir = node2vec_script_dir
        self.embedding_dimensions = embedding_dimensions

    def generate_graph_embeddings(self):
    
        base_name = self.triples_file.split('/')[-1]

        output_ints_location = self.output_dir + '/' + base_name.replace('Triples_Identifiers','Triples_Integers_node2vecInput')

        output_ints_map_location = self.output_dir + '/' + base_name.replace('Triples_Identifiers','Triples_Integer_Identifier_Map')

        with open(self.triples_file, 'r') as f_in:
            #Length matches original file length
            kg_data = set(tuple(x.split('\t')) for x in f_in.read().splitlines())
        f_in.close()

        # map identifiers to integers
        entity_map = {}
        entity_counter = 0
        graph_len = len(kg_data)

        ints = open(output_ints_location, 'w', encoding='utf-8')
        ints.write('subject' + '\t' + 'predicate' + '\t' + 'object' + '\n')

        for s, p, o in kg_data:
            subj, pred, obj = s, p, o
            if subj not in entity_map: entity_counter += 1; entity_map[subj] = entity_counter
            if pred not in entity_map: entity_counter += 1; entity_map[pred] = entity_counter
            if obj not in entity_map: entity_counter += 1; entity_map[obj] = entity_counter
            ints.write('%d' % entity_map[subj] + '\t' + '%d' % entity_map[pred] + '\t' + '%d' % entity_map[obj] + '\n')
        ints.close()

        #write out the identifier-integer map
        with open(output_ints_map_location, 'w') as file_name:
            json.dump(entity_map, file_name)

        with open(output_ints_location) as f_in:
            kg_data = [x.split('\t')[0::2] for x in f_in.read().splitlines()]
        f_in.close()

        file_out = self.output_dir + '/' + base_name.replace('Triples_Identifiers','Triples_node2vecInput_cleaned')

        with open(file_out, 'w') as f_out:
            for x in kg_data[1:]:
                f_out.write(x[0] + ' ' + x[1] + '\n')

        f_out.close()
        
        os.chdir(self.node2vec_script_dir) 

        command = "python GutMGene_sparse_custom_node2vec_wrapper.py --edgelist {} --dim {} --walklen 10 --walknum 20 --window 10"
        os.system(command.format(file_out,self.embedding_dimensions))

        embeddings_file = file_out.split('.')[0] + '_node2vec_Embeddings' + str(self.embedding_dimensions) + '_None.emb'
        
        emb = KeyedVectors.load_word2vec_format(embeddings_file, binary=False)

        return emb
