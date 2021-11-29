from graph import Graph
from edge import Edge
from random import randint

class SumoGenerator():

    def __init__(self, graph: Graph) -> None:
        self.graph = graph


    def generate_nodes_xml(self) -> bool:
        """
        Generates Sumo Nodes XML file
        """

        result = ["<nodes>"]

        for n in self.graph.nodes:
            node = self.graph.nodes[n]

            line = f"<node id=\"{node.__hash__()}\" x=\"{node.x}\" y=\"{node.y}\" />"

            result.append(line)

        result.append("</nodes>")

        try:
            with open("./src/out/nodes.xml", "w") as f:
                f.write("\n".join(result))
        except:
            return False
        
        return True


    def generate_edges_xml(self) -> bool:
        """
        Generates Sumo Edges XML file
        """

        result = ["<edges>"]

        for e in self.graph.edges:
            edge = self.graph.edges[e]
            snode = edge.snode
            enode = edge.enode

            line = f"<edge from=\"{snode.__hash__()}\" id=\"{edge.__hash__()}\" to=\"{enode.__hash__()}\" />"

            result.append(line)

        result.append("</edges>")

        try:
            with open("./src/out/edges.xml", "w") as f:
                f.write("\n".join(result))
        except:
            return False
        
        return True


    def generate_route(self, route_id: int, id:int, depart:int, path: list) -> str:
        """
        Generates a Sumo route based on some path
        """

        edges = ""

        for i in range(1,len(path)):
            node1 = path[i-1]
            node2 = path[i]

            edge = Edge(node1, node2, 0)

            edges += str(edge.__hash__()) + " "

        return f"""
        <route id="{route_id}" edges="{edges}"/>
        <vehicle depart="{depart}" id="{id}" route="{route_id}" type="Car{randint(0,2)}" />
        """


    def generate_random_routes(self, nroutes: int=100) -> list:        
        ids = []
        routes = []
        for i in range(nroutes):
            coming = bool(randint(0,1))
            if coming or len(ids) == 0:
                node, path = self.graph.get_nearest_free_spot(self.graph.entrance, False, False)
                node.free = False
                ids.append(node)
            else:
                node = ids.pop()
                node.free = True
                node, path = self.graph.get_path(node, self.graph.exit, False)

            route = self.generate_route(i, i, i, path)
            routes.append(route)
        
        return routes


    def generate_routes_xml(self, routes: list) -> bool:
        """
        Generates Sumo Routes XML file
        """

        result = ["<routes>"]

        result.append("<vType accel=\"1.0\" decel=\"5.0\" id=\"Car0\" length=\"2.0\" maxSpeed=\"10.0\" sigma=\"0.0\" />")
        result.append("<vType accel=\"2.0\" decel=\"6.0\" id=\"Car1\" length=\"1.7\" maxSpeed=\"15.0\" sigma=\"0.0\" />")
        result.append("<vType accel=\"1.0\" decel=\"4.0\" id=\"Car2\" length=\"1.2\" maxSpeed=\"12.0\" sigma=\"0.0\" />")

        for r in routes:
            result.append(r)

        result.append("</routes>")

        try:
            with open("./src/out/routes.xml", "w") as f:
                f.write("\n".join(result))
        except:
            return False
        
        return True