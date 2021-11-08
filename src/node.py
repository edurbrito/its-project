class Node():
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y
        self.out_edges = {}

    def __str__(self) -> str:
        return str((self.x, self.y))

    def __hash__(self) -> int:
        return hash(str(self))

    def __eq__(self, o: object) -> bool:
        return self.x == o.x and self.y == o.y
    
    def add_egde(self, edge) -> None:
        if edge.snode == self:
            self.out_edges[edge.enode] = edge


class ParkingSpot(Node):
    def __init__(self, x, y) -> None:
        super().__init__(x, y)
        self.free = True
    
    def get_colour(self):
        return "green" if self.free else "red"

class ParkingSpotDisabled(ParkingSpot):
    def __init__(self, x, y) -> None:
        super().__init__(x, y)

    def get_colour(self):
        return "#EACA00" if self.free else "red"

class DrivingNode(Node):
    def __init__(self, x, y) -> None:
        super().__init__(x, y)
        
class Entrance(Node):
    def __init__(self, x, y) -> None:
        super().__init__(x, y)
        
class Exit(Node):
    def __init__(self, x, y) -> None:
        super().__init__(x, y)

class FactoryNode():

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(FactoryNode, cls).__new__(
                                cls, *args, **kwargs)
        return cls._instance

    def create_node(self, type, x, y) -> Node:
        if type == "entrance":
            return Entrance(x,y)
        elif type == "exit":
            return Exit(x,y)
        elif type == "pspot":
            return ParkingSpot(x,y)
        elif type == "pspot_disabled":
            return ParkingSpotDisabled(x,y)
        elif type == "dnode":
            return DrivingNode(x,y)
        return None