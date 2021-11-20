from bparser import *
from graph import Graph
from __env__ import BP_SMALL, BP_MEDIUM, BP_LARGE
from sumo import SumoGenerator
from random import randint

if __name__ == "__main__":
    p = Parser(BP_LARGE)

    g = Graph(p)

    g.generate_random_state(0.7,0.5)

    g.draw()

    s = SumoGenerator(g)

    s.generate_nodes_xml()
    s.generate_edges_xml()
    
    ids = []
    routes = []
    for i in range(100):
        coming = bool(randint(0,1))
        if coming or len(ids) == 0:
            node, path = g.get_nearest_free_spot(g.entrance, False, False)
            node.free = False
            ids.append(node)
        else:
            node = ids.pop()
            node.free = True
            node, path = g.get_path(node, g.exit, False)

        route = s.generate_route(i, i, i, path)
        routes.append(route)
    
    s.generate_routes_xml(routes)
