class Edge():
    def __init__(self, snode, enode, dst) -> None:
        self.snode = snode
        self.enode = enode
        self.weight = dst

    def __hash__(self) -> int:
        return hash(str(self.snode) + str(self.enode))