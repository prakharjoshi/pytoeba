from django.db.models.loading import get_model
from .base import BaseGraphBackend
import numpy as np

class SciPySparseBackend(BaseGraphBackend):

    def get_graph_lib(self):
        import apgl.graph
        return apgl.graph

    def get_graph(self, max_nodes=0):
        self._setup_nodes_links()

        if self.init_kwargs.get('max_nodes'):
            self.max_nodes = self.init_kwargs['max_nodes']
        elif max_nodes:
            self.max_nodes = max_nodes
        else:
            self.max_nodes = len(self.nodes_array)
        return self.lib.SparseGraph(self.max_nodes + 1, undirected=False, dtype='i4')

    def _add_edge(self, node1, node2, **kwargs):
        # the int conversion is a bit unfortunate, np.searchsorted returns
        # an int type that says it's np.int32 but actually isn't
        # and makes scipy choke
        self.graph[int(node1), int(node2)] = kwargs.get('weight') or 1

    def add_edge(self, node1, node2, **kwargs):
        node1 = np.searchsorted(self.nodes_array, node1)
        node2 = np.searchsorted(self.nodes_array, node2)
        self._add_edge(node1, node2, **kwargs)

    def _remove_edge(self, node1, node2):
        self.graph.removeEdge(int(node1), int(node2))

    def remove_edge(self, node1, node2):
        node1 = np.searchsorted(self.nodes_array, node1)
        node2 = np.searchsorted(self.nodes_array, node2)
        self._remove_edge(node1, node2)

    def _setup_nodes_links(self):
        self.links_array = np.array(np.zeros((len(self.links), 2)), dtype='i4')
        c = 0
        for link in self.links:
            if link.level == 1:
                self.links_array[c][0] = link.side1_id
                self.links_array[c][1] = link.side2_id
                c += 1

        # blame numpy for this monstrosity, [:,0] accesses all rows for
        # column 1 (0-indexed), argsort() returns the sorted indices
        # for the sliced array, finally, we use these indices to reorder
        # the rows by accessing links_array[]
        self.links_array = self.links_array[self.links_array[:,0].argsort()]
        # remove pesky zeros
        if self.links_array[0][0] == 0:
            one_idx = np.searchsorted(self.links_array[0:,0], 1)
            self.links_array = self.links_array[one_idx:]
        # get unique nodes for matrix index assignment
        self.nodes_array, self.nodes_idx = np.unique(self.links_array[0:,0], return_index=True)

    def populate_graph(self, links=[]):
        if links:
            self.links = links
            self.graph = self.get_graph()
        else:
            links = self.links

        # build graph, matrix index is in nodes_array
        # links_array has node id mappings
        # nodes_idx has start index of a given node id in links_array
        for i in xrange(self.max_nodes):
            node1 = i
            from_idx = self.nodes_idx[i]
            try:
                to_idx = self.nodes_idx[i+1]
            except IndexError:
                to_idx = len(self.links_array)

            for j in xrange(from_idx, to_idx):
                node2 = np.searchsorted(self.nodes_array, self.links_array[j][1])
                self._add_edge(node1, node2)

        self.original_distances = self.get_all_distances()

    def get_all_distances(self):
        return self.graph.findAllDistances()

    def _links_from_indices(self, indices):
        Link = get_model('pytoeba', 'Link')
        links = []
        for index in indices:
            node1_id = self.nodes_array[index[0]]
            node2_id = self.nodes_array[index[1]]
            level = self.new_distances[index[0]][index[1]]

            link = Link(side1_id=node1_id, side2_id=node2_id, level=level)
            links.append(link)
        return links

    def get_recomputed_links(self, created=False, updated=False, deleted=False):
        self.new_distances = self.get_all_distances()
        diff = self.original_distances - self.new_distances
        changed = self.original_distances != self.new_distances

        return_dict = {}
        if created:
            created = np.where(np.isposinf(diff) & changed == True)
            created = zip(created[0], created[1])
            return_dict['created'] = self._links_from_indices(created)

        if updated:
            updated = np.where(np.isfinite(diff) & changed == True)
            updated = zip(updated[0], updated[1])
            return_dict['updated'] = self._links_from_indices(updated)

        if deleted:
            deleted = np.where(np.isneginf(diff) & changed == True)
            deleted = zip(deleted[0], deleted[1])
            return_dict['deleted'] = self._links_from_indices(deleted)

        if not return_dict:
            created = np.where(np.isposinf(diff) & changed == True)
            created = zip(created[0], created[1])
            updated = np.where(np.isfinite(diff) & changed == True)
            updated = zip(updated[0], updated[1])
            deleted = np.where(np.isneginf(diff) & changed == True)
            deleted = zip(deleted[0], deleted[1])
            all_ = created + updated + deleted
            return_dict['all'] = self._links_from_indices(all_)

        return return_dict


class SciPyDenseBackend(SciPySparseBackend):

    def get_graph(self, max_nodes=0):
        self._setup_nodes_links()

        if self.init_kwargs.get('max_nodes'):
            self.max_nodes = self.init_kwargs['max_nodes']
        elif max_nodes:
            self.max_nodes = max_nodes
        else:
            self.max_nodes = len(self.nodes_array)
        return self.lib.DenseGraph(self.max_nodes + 1, undirected=False, dtype='i4')
