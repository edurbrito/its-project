from bparser import Parser
from node import *
from edge import Edge
import networkx as nx
import matplotlib.pyplot as plt
from random import randint

class Graph():
    def __init__(self, nodes: dict, edges: dict) -> None:
        self.nodes = nodes
        self.edges = edges

    def __init__(self, parser: Parser) -> None:
        if parser.img is not None:
            presult = parser.parse()

        self.nodes = self.__get_nodes(parser)
        self.edges = self.__get_edges(parser)

        if sum(presult[0].values()) != len(self.nodes) or presult[1] != len(self.edges):
            raise Exception("Number of nodes/edges not correct")

    def draw(self) -> None:
        """
        Draws the directed graph using networkx library
        """

        G = nx.DiGraph()

        for k in self.nodes:
            G.add_node(self.nodes[k], pos=k)

        for k in self.edges:
            G.add_edge(self.edges[k].snode, self.edges[k].enode)
        
        pos = nx.get_node_attributes(G,'pos')

        colors = []
        sizes = []

        for n in G.nodes:
            if isinstance(n, ParkingSpot):
                n.free = bool(randint(0,1)) # TODO
                colors.append(n.get_colour())
                sizes.append(100)
            elif isinstance(n, ParkingSpotDisabled):
                n.free = bool(randint(0,1)) # TODO
                colors.append(n.get_colour())
                sizes.append(100)
            elif isinstance(n, Entrance):
                colors.append("orange")
                sizes.append(250)
            elif isinstance(n, Exit):
                colors.append("lightgreen")
                sizes.append(250)
            else:
                colors.append("blue")
                sizes.append(100)
            
        nx.draw(G, pos, node_color=colors, node_size=sizes)
        mng = plt.get_current_fig_manager()
        mng.full_screen_toggle()
        plt.show()


    """ Private Methods """
       

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