
class PKLGraph:

    def __init__(self, edgelist, labels_all, igraph, igraph_nodes):
        self.edgelist = edgelist
        self.labels_all = labels_all
        self.igraph = igraph
        self.igraph_nodes = igraph_nodes

class MonGraph:
 
    def __init__(self, edgelist, identifiers):
        self.edgelist = edgelist
        self.identifiers = identifiers
