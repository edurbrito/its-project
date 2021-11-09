from __env__ import *
import numpy as np
import cv2
import os

class Parser():

    def __init__(self, img: str) -> None:
        self.img = str(os.path.abspath(img))
        self.nodes = None
        self.edges = None

    def parse(self) -> tuple:
        """
        Parses the image and returns the report info
        """

        img = cv2.cvtColor(cv2.imread(self.img), cv2.COLOR_BGR2RGB)

        # parsed contains the mapping between the labels and colours
        # inv_parsed contains the mapping between the colours and the labels
        parsed, inv_parsed = self.__parse_colours()

        _all = { k:[] for k in parsed}
        ln = len(img)

        # goes through all pixels and gathers them by type (label) based on the colour
        for y,l in enumerate(img):
            for x,c in enumerate(l):
                type = inv_parsed.get(str(c), False)
                if type: 
                    _all[type].append((x,ln - y))

        # gets the driving node neighbours of all the parking spots
        # creates an edge between each pair of those
        nns = self.__nearest_neighbours(
            _all["pspot"] + _all["pspot_disabled"], 
            _all["dnode"])

        # selects all the nodes
        self.nodes = {k:_all[k] for k in ["entrance", "exit", "dnode", "pspot", "pspot_disabled"]}

        # joins the previously calculated nn edges
        # with the detected edges that connect driving nodes
        self.edges = nns | self.__detect_edges(
                _all["dnode"] + _all["entrance"] + _all["exit"],
                _all["edge"],
                _all["arrow"])

        # returns the amount of nodes and edges generated
        return {k:len(self.nodes[k]) for k in self.nodes}, len(self.edges)


    """ Private Methods """


    def __hex_to_rgb(self, hex_str: str):
        """
        Converts hex colour to rgb format
        """

        hex_str = hex_str.strip()

        if hex_str[0] == '#':
            hex_str = hex_str[1:]

        if len(hex_str) != 6:
            raise ValueError(f'Input #{hex_str} is not in #RRGGBB format.')

        r, g, b = hex_str[:2], hex_str[2:4], hex_str[4:]
        rgb = [int(n, base=16) for n in (r, g, b)]

        return np.array(rgb)

    def __parse_colours(self) -> tuple:
        """
        Parses ALL colours from hex to rgb
        @ Returns a dict mapping the label and the colour
        and another dict mapping the colour and the label
        """
        
        parsed = ALL.copy()

        for k in parsed.keys():
            parsed[k] = self.__hex_to_rgb(parsed[k])
        
        inverse_parsed = { str(parsed[k]):k for k in parsed}

        return parsed, inverse_parsed

    def __euclidean_distance(self, x1, y1, x2, y2) -> float:
        """
        Calculates euclidean distance between two points
        """
        
        return np.sqrt(np.power(x1-x2,2) + np.power(y1-y2,2))

    def __nearest_neighbours(self, targets: list, neighbours: list) -> dict:
        """
        Calculates the nearest neighbour driving node of every parking spot
        """

        nns = dict()

        for target in targets:
            nn, nn_distance = None, 1000000000

            for neighbour in neighbours:
                x1,y1,x2,y2 = (target[0], target[1], neighbour[0], neighbour[1])
                dst = self.__euclidean_distance(x1,y1,x2,y2)
                if dst < nn_distance:
                    nn = neighbour
                    nn_distance = dst
            
            if nn is not None:
                # if a nearest neighbour was found
                # a directed edge is created between them
                nns[(nn, target)] = nn_distance

        return nns

    def __is_neighbour(self, x1, y1, x2, y2) -> bool:
        """
        Checks if two points are neighbours
        """

        for i,j in [(-1,0), (0,-1), (0,1), (1,0)]: # (-1,-1), (-1,1), (1,1), (1,-1)
            if x1 + i == x2 and y1 + j == y2:
                return True
        
        return False

    def __find(self, data, i):
        """
        Find (Path Compression) of Union-Find algorithm
        """

        if i != data[i]:
            data[i] = self.__find(data, data[i])

        return data[i]

    def __union(self, data, i, j):
        """
        Union of Union-Find algorithm
        """

        pi, pj = self.__find(data, i), self.__find(data, j)
        if pi != pj:
            if self.__euclidean_distance(*pi, 0,0) < self.__euclidean_distance(*pj, 0,0):
                data[pj] = pi
            else:
                data[pi] = pj

    def __detect_edges(self, dnodes, edges, arrows) -> dict:
        """
        Detects the directed and undirected edges of the graph
        """

        edges = edges + arrows
        data = {k:k for k in edges}
        lines = {}

        prev = None

        # performs union-find neighbour-based search
        # until the algorithm stabilizes
        while True:
            for e1 in edges:
                for e2 in edges:
                    if self.__is_neighbour(*e1, *e2):
                        self.__union(data, e1, e2)
            new = hash(str(data))
            if new == prev: break
            prev = new

        # joins the pixels as lines
        # based on the common parent from union-find
        for e in edges:
            k = data[e]
            if k in lines:
                lines[k][0].add(e)
            else:
                lines[k] = (set(),set())
                lines[k][0].add(e)

        # adds the corresponding start and end nodes
        # that are part of the edge
        for n in dnodes:
            for e in edges:
                if self.__is_neighbour(*e, *n):
                    lines[data[e]][1].add(n)

        result = {}

        # creates the edges based on the lines
        # either directed or undirected edges
        for l in lines:
            dots = list(lines[l][0])
            
            # check if there is an arrow for the line
            directed = None
            for a in arrows:
                if a in dots: directed = a

            # gets the two nodes associated with the line
            nodes = list(lines[l][1])
            if len(nodes) == 2:
                n1, n2 = nodes[0], nodes[1]
                if n1 != n2:
                    dst = self.__euclidean_distance(*n1,*n2)
                    
                    # creates the edge(s) for those two nodes
                    if directed is not None:
                        if self.__is_neighbour(*n1, *directed):
                            result[(n2,n1)] = dst
                        elif self.__is_neighbour(*n2, *directed):
                            result[(n1,n2)] = dst
                    else:
                        result[(n1,n2)] = dst
                        result[(n2,n1)] = dst
        
        return result