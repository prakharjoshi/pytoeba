

class BaseGraphBackend(object):

    def __init__(self, links=[], **kwargs):
        self.init_kwargs = kwargs
        self.links = links
        self.lib_init()
        self.graph_init()
        self.populate_graph()
        super(BaseGraphBackend, self).__init__()

    def lib_init(self):
        self.lib = self.get_graph_lib()

    def graph_init(self):
        self.graph = self.get_graph()

    def get_graph_lib(self):
        """
        Import and return the graphing module here.
        """
        raise NotImplementedError("Please define how to get the graphing library")

    def get_graph(self):
        """
        Initialize a digraph using self.lib
        """
        raise NotImplementedError("Please define how to make a digraph using this library")

    def add_node(self, node, **kwargs):
        """
        Access the library using self.graph and call the
        library specific code that adds a node.
        """
        raise NotImplementedError("Please define how to add a node to the graph using this library")

    def remove_node(self, node):
        """
        Access the library using self.graph and call the
        library specific code that removes a node.
        """
        raise NotImplementedError("Please define how to add a node to the graph using this library")

    def add_edge(self, node1, node2, **kwargs):
        """
        Add an edge to the graph using self.graph
        """
        raise NotImplementedError("Please define how to add an edge to the graph using this library")

    def remove_edge(self, node1, node2):
        """
        Remove an edge to the graph using self.graph
        """
        raise NotImplementedError("Please define how to add an edge to the graph using this library")

    def _get_nodes(self, links):
        nodes = set()
        for link in links:
            nodes.add(link.side1_id)
            nodes.add(link.side2_id)
        return nodes

    def populate_graph(self, links=[]):
        """
        Override this for adding custom labels to nodes
        and edges.
        """
        if links:
            self.graph = self.get_graph()
        else:
            links = self.links

        nodes = self._get_nodes(links)
        for node in nodes:
            self.add_node(node)

        for link in links:
            self.add_edge(link.side1_id, link.side2_id)

    def get_all_paths(self):
        """
        Use self.lib and self.graph to compute all shortest
        paths in the graph. Returns the result.
        """
        raise NotImplementedError("Please define how to compute all paths shortest paths using this library")

    def get_all_distances(self):
        """
        Possibly use self.get_all_paths() and transform it into
        distances instead of paths. Returns the result.
        """
        raise NotImplementedError("Please define how to compute all paths shortest paths using this library")

    def get_recomputed_links(self):
        """
        Implement how to translate the result into Link objects
        """
        raise NotImplementedError("Please define how to turn distances into Link objects")
