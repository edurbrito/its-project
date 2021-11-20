from bparser import Parser
from node import *
from edge import Edge
import networkx as nx
import matplotlib.pyplot as plt
from random import randint
import math

class Graph():
    def __init__(self, nodes: dict, edges: dict) -> None:
        self.nodes = nodes
        self.edges = edges

    def __init__(self, parser: Parser) -> None:
        if parser.img is not None:
            presult = parser.parse()

        self.info = {"pspot": 0, "pspot_disabled": 0}
        self.entrance = None
        self.exit = None
        self.nodes = self.__get_nodes(parser)
        self.edges = self.__get_edges(parser)
        self.G = nx.DiGraph()

        for k in self.nodes:
            n = self.nodes[k]
            self.G.add_node(n, pos=k)

        for k in self.edges:
            self.G.add_edge(self.edges[k].snode, self.edges[k].enode)

        self.all_pairs_distance = dict(nx.all_pairs_shortest_path_length(self.G))
        self.all_pairs_path = dict(nx.all_pairs_shortest_path(self.G))
        
        if sum(presult[0].values()) != len(self.nodes) or presult[1] != len(self.edges):
            raise Exception("Number of nodes/edges not correct")

    def generate_random_state(self, prob_pspot: float, prob_pspotdisabled: float) -> None:
        
        lpspot = self.info["pspot"]
        lpspot_disabled = self.info["pspot_disabled"]

        for n in self.nodes:
            node = self.nodes[n]
            if isinstance(node, ParkingSpot):
                node.free = self.__get_prob(prob_pspot, randint(1,lpspot), lpspot)
            elif isinstance(node, ParkingSpotDisabled):
                node.free = self.__get_prob(prob_pspotdisabled, randint(1,lpspot_disabled), lpspot_disabled)

    def get_stats(self) -> dict:

        current_stats = {"pspot": 0, "pspot_disabled": 0}

        for n in self.nodes:
            node = self.nodes[n]
            if isinstance(node, ParkingSpot):
                if not node.free:
                    current_stats["pspot"] += 1
            elif isinstance(node, ParkingSpotDisabled):
                if not node.free:
                    current_stats["pspot_disabled"] += 1

        for k in current_stats:
            current_stats[k] = current_stats[k] / self.info[k]

        return current_stats

    def get_path(self, start_node: Node, end_node: Node, visualize: bool) -> tuple:
        dst = self.all_pairs_distance[start_node][end_node]
        path = self.all_pairs_path[start_node][end_node]

        if visualize:
            self.draw(path)

        return dst, path

    def get_nearest_free_spot(self, start_node: Node, is_disabled: bool, visualize: bool) -> tuple:
        all_distances = self.all_pairs_distance[start_node]
        min_dist, nearest_node = math.inf, None
        path = []

        for node in all_distances:
            if isinstance(node, ParkingSpot) and not is_disabled:
                if node.free and all_distances[node] < min_dist:
                    min_dist = all_distances[node]
                    nearest_node = node
            elif isinstance(node, ParkingSpotDisabled) and is_disabled:
                if node.free and all_distances[node] < min_dist:
                    min_dist = all_distances[node]
                    nearest_node = node

        if nearest_node is not None:
            path = self.all_pairs_path[start_node][nearest_node]
        
        if visualize and nearest_node is not None:
            self.draw(path)

        return (nearest_node, path)

    def draw(self, path=None) -> None:
        """
        Draws the directed graph using networkx library
        """

        colors = {}
        sizes = []

        for k in self.nodes:
            n = self.nodes[k]
            if isinstance(n, ParkingSpot):
                colors[n] = n.get_colour()
                sizes.append(100)
            elif isinstance(n, ParkingSpotDisabled):
                colors[n] = n.get_colour()
                sizes.append(100)
            elif isinstance(n, Entrance):
                colors[n] = "orange"
                sizes.append(250)
            elif isinstance(n, Exit):
                colors[n] = "lightgreen"
                sizes.append(250)
            else:
                colors[n] = "blue"
                sizes.append(50)
        
        if path is not None:
            
            for i, n in enumerate(path):
                if i == 0: colors[path[i]] = "#FF34B3"
                elif i == len(path) - 1: colors[path[i]] = "#AAFF00"
                else: colors[path[i]] = "#00FFFF"


        pos = nx.get_node_attributes(self.G,'pos')
            
        nx.draw(self.G, pos, node_color=colors.values(), node_size=sizes)
        mng = plt.get_current_fig_manager()
        mng.full_screen_toggle()
        plt.show()


    """ Private Methods """
       
    def __get_prob(self, prob: float, random_int: int, length: int) -> bool:
        return (random_int / length) > prob

    def __get_nodes(self, parser) -> dict:
        """
        Creates all the nodes' objects from the info returned by the parser
        """

        _all = {}
        factory = FactoryNode()

        for k in parser.nodes:
            nodes = parser.nodes[k]
            for node in nodes:
                _all[node] = factory.create_node(k, node[0], node[1])
                if isinstance(_all[node], ParkingSpot):
                    self.info["pspot"] += 1
                elif isinstance(_all[node], ParkingSpotDisabled):
                    self.info["pspot_disabled"] += 1
                elif isinstance(_all[node], Entrance):
                    self.entrance = _all[node]
                elif isinstance(_all[node], Exit):
                    self.exit = _all[node]

        return _all

    def __get_edges(self, parser) -> dict:
        """
        Creates all the edges' objects from the info returned by the parser
        """

        _all = {}

        if len(self.nodes) != 0:
            
            for k in parser.edges:
                sn, en, dst = k[0], k[1], parser.edges[k]
                edge = Edge(self.nodes[sn], self.nodes[en], dst)
                _all[edge] = edge

        return _all