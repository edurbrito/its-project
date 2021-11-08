from bparser import Parser
from node import *
from edge import Edge
import networkx as nx
import matplotlib.pyplot as plt

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
        G = nx.Graph()

        for k in self.nodes:
            G.add_node(self.nodes[k], pos=k)

        for k in self.edges:
            G.add_edge(self.edges[k].snode, self.edges[k].enode)
        
        pos = nx.get_node_attributes(G,'pos')

        colors = []

        for n in G.nodes:
            if isinstance(n, ParkingSpot):
                colors.append("red")
            elif isinstance(n, ParkingSpotDisabled):
                colors.append("yellow")
            elif isinstance(n, Entrance):
                colors.append("orange")
            elif isinstance(n, Exit):
                colors.append("green")
            else:
                colors.append("blue")
            
        
        nx.draw(G, pos, node_color=colors)
        plt.show()


    """ Private Methods """
       

    def __get_nodes(self, parser) -> dict:
        
        _all = {}
        factory = FactoryNode()

        for k in parser.nodes:
            nodes = parser.nodes[k]
            for node in nodes:
                _all[node] = factory.create_node(k, node[0], node[1])

        return _all

    def __get_edges(self, parser) -> dict:

        _all = {}

        if len(self.nodes) != 0:
            
            for k in parser.edges:
                sn, en, dst = k[0], k[1], parser.edges[k]
                edge = Edge(self.nodes[sn], self.nodes[en], dst)
                _all[edge] = edge

        return _all