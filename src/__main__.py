from bparser import *
from graph import Graph
from __env__ import BP_SMALL, BP_MEDIUM, BP_LARGE

if __name__ == "__main__":
    p = Parser(BP_SMALL)

    g = Graph(p)

    g.draw()