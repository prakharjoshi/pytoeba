from .base import BaseGraphBackend
from collections import defaultdict
from pytoeba.utils import NestedDict
from django.db.models.loading import get_model

class NetworkxBackend(BaseGraphBackend):

    def get_graph_lib(self):
        import networkx
        return networkx

    def get_graph(self):
        return self.lib.DiGraph()

    def add_node(self, node, **kwargs):
        self.graph.add_node(node, kwargs)

    def remove_node(self, node):
        self.graph.remove_node(node)

    def add_edge(self, node1, node2, **kwargs):
        self.graph.add_edge(node1, node2, weight=1, **kwargs)

    def remove_edge(self, node1, node2):
        self.graph.remove_edge(node1, node2)

    def populate_graph(self, links=[]):
        if links:
            self.graph = self.get_graph()
        else:
            links = self.links

        nodes = self._get_nodes(links)
        for node in nodes:
            self.add_node(node)

        self.links_dict = NestedDict()
        for link in links:
            if link.level == 1:
                self.add_edge(link.side1_id, link.side2_id)
            self.links_dict[link.side1_id][link.side2_id]['id'] = link.id

        self.original_distances = self.get_all_distances()

    def get_all_paths(self):
        return self.lib.all_pairs_shortest_path(self.graph)

    def get_all_distances(self):
        return self.lib.all_pairs_shortest_path_length(self.graph)

    def _tuplize_distances(self, distances):
        tuples = set()
        created_tuples = []
        for node1, mappings in distances.iteritems():
            for node2, distance in mappings.iteritems():
                if node1 != node2:
                    link_id = self.links_dict[node1][node2]['id']
                    if link_id:
                        tuples.add((node1, node2, distance, link_id))
                    else:
                        created_tuples.append((node1, node2, distance))
        return tuples, created_tuples

    def _links_from_tuples(self, distances, link_id=True):
        Link = get_model('pytoeba', 'Link')
        links = []
        for distance in distances:
            if link_id:
                link = Link(
                    side1_id=distance[0], side2_id=distance[1],
                    level=distance[2], id=distance[3]
                    )
            else:
                link = Link(
                    side1_id=distance[0], side2_id=distance[1],
                    level=distance[2],
                    )
            links.append(link)
        return links

    def get_recomputed_links(self, created=False, updated=False, deleted=False):
        old_distances, _ = self._tuplize_distances(self.original_distances)

        new_distances, created_distances = self._tuplize_distances(self.get_all_distances())

        return_dict = {}
        if created:
            return_dict['created'] = self._links_from_tuples(created_distances, link_id=False)

        if updated:
            updated_distances = new_distances - old_distances
            return_dict['updated'] = self._links_from_tuples(updated_distances)

        if deleted:
            deleted_distances = old_distances - new_distances
            return_dict['deleted'] = self._links_from_tuples(deleted_distances)

        if not return_dict:
            created_links = self._links_from_tuples(created_distances, link_id=False)
            updated_distances = new_distances - old_distances
            updated_links = self._links_from_tuples(updated_distances)
            deleted_distances = old_distances - new_distances
            deleted_links = self._links_from_tuples(deleted_distances)
            all_ = []
            all_.extend(created_links)
            all_.extend(updated_links)
            all_.extend(deleted_links)
            return_dict['all'] = self._links_from_tuples(all_)

        return return_dict
