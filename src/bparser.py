from numpy.core.numeric import array_equal
from __env__ import *
import numpy as np
import cv2

class Parser():

    def __init__(self, img: str) -> None:
        self.img = img
        self.nodes = None
        self.edges = None

    def parse(self) -> tuple:
        """
        Parses the image and returns the report info
        """

        img = cv2.cvtColor(cv2.imread(self.img), cv2.COLOR_BGR2RGB)

        parsed, inv_parsed = self.__parse_colours()

        _all = { k:[] for k in parsed}
        ln = len(img)

        for y,l in enumerate(img):
            for x,c in enumerate(l):
                type = inv_parsed.get(str(c), False)
                if type: 
                    _all[type].append((x,ln - y))

        nns = self.__nearest_neighbours(
            _all["pspot"] + _all["pspot_disabled"], 
            _all["dnode"])

        self.nodes = {k:_all[k] for k in ["entrance", "exit", "dnode", "pspot", "pspot_disabled"]}
        self.edges = nns

        print(self.__detect_edges(
                _all["dnode"],
                _all["edge"],
                _all["arrow"]))

        # return the amount of nodes and edges generated
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
            nn, nn_distance = None, 1000000

            for neighbour in neighbours:
                x1,y1,x2,y2 = (target[0], target[1], neighbour[0], neighbour[1])
                dst = self.__euclidean_distance(x1,y1,x2,y2)
                if dst < nn_distance:
                    nn = neighbour
                    nn_distance = dst
            
            if nn is not None:
                nns[target] = nn, nn_distance
        return nns

    def __is_neighbour(self, x1, y1, x2, y2) -> bool:
        for i,j in [(-1,0), (0,-1), (0,1), (1,0)]:
            if x1 + i == x2 and y1 + j == y2:
                return True
        return False

    def __find(self, data, i):
        if i != data[i]:
            data[i] = self.__find(data, data[i])
        return data[i]

    def __union(self, data, i, j):
        pi, pj = self.__find(data, i), self.__find(data, j)
        if pi != pj:
            if self.__euclidean_distance(*pi, 0,0) < self.__euclidean_distance(*pj, 0,0):
                data[pj] = pi
            else:
                data[pi] = pj

    def __detect_edges(self, dnodes, edges, arrows) -> dict:
        data = {k:k for k in edges}
        nedges = {n:set() for n in dnodes}

        for e1 in edges:
            for e2 in edges:
                if self.__is_neighbour(*e1, *e2):
                    self.__union(data, e1, e2)
        
        for n in dnodes:
            for e in edges:
                if self.__is_neighbour(*data[e], *n):
                    nedges[n].add(data[e])

        print(data)
        print()
        print(nedges)
