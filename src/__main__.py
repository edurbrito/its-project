from bparser import *
from graph import Graph

if __name__ == "__main__":
    p = Parser("/home/edurbrito/Projects/UTARTU-4Y1S/intelligent-transport-systems/project/its-project/blueprints/bp-01-pixel-sm.png")

    g = Graph(p)

    g.draw()