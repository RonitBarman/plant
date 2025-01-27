#!/pkg/python/3.7.4/bin/python3
from all_helpers import *
from pyblant import *

def log(*args, **kwargs):
    print(*args, **kwargs)

class GraphShell:
    def __init__(self):
        # settings
        self._alph = True

        # necessary defaults
        self._mounted_gtag = None
        self._curr_node = None

    def mounted_gtag_str(self):
        return '(' + ('' if self._mounted_gtag == None else self._mounted_gtag) + ')'

    def curr_node_str(self):
        return '-' if self._curr_node == None else self._curr_node

    def gsh_read(self):
        return input(f'{self.mounted_gtag_str()} {self.curr_node_str()} $ ')

    def tick(self, command):
        splitted = command.strip().split(' ')
        head = splitted[0]
        args = splitted[1:]

        if head == 'q' or head == 'quit':
            quit()
        elif head == 'mount':
            self.mount_graph(args[0])
        elif head == 'info':
            self.graph_info()
        elif head == 'cd':
            self.change_node(args)
        elif head == 'top':
            self.log_top(int(args[0]))
        elif head == 'edge':
            self.has_edge(args[0], args[1])
        elif head == 'ninfo':
            self.log_node_info(args[0])
        else:
            log('did not understand command')

    def mount_graph(self, mount_gtag):
        self._mounted_gtag = mount_gtag
        mount_fpath = get_graph_path(mount_gtag)
        self._el = read_in_el(mount_fpath)
        self._edge_set = set(self._el)
        self._adj_set = read_in_adj_set(mount_fpath)
        self._nodes = read_in_nodes(mount_fpath)
        self._heurs = get_deg_heurs(self._nodes, self._adj_set)
        log(f'successfully mounted {mount_gtag}')
        self.graph_info()
        self.change_node([])

    def get_home_node(self):
        return None

    def change_node(self, args):
        if len(args) == 0:
            new_node = self.get_home_node()
        else:
            new_node = args[0]

        self._curr_node = new_node
        self.set_neighbors()

    def set_neighbors(self):
        if self._curr_node != None:
            self._neighs = self._adj_set[self._curr_node]
        else:
            self._neighs = self._nodes

        self._sorted_neighs = blant_sorted(self._neighs, self._heurs, self._alph)
        self._ranked_neighs = get_ranks(self._sorted_neighs, self._heurs)

    def graph_info(self):
        num_nodes = len(self._nodes)
        num_edges = len(self._el)
        log(f'{self._mounted_gtag}: {num_nodes}n {num_edges}e')

    def log_top(self, n):
        for i in range(n):
            node = self._sorted_neighs[i]
            log(f'{i}: {node} (deg {self.get_deg(node)})')

    def get_deg(self, node):
        return len(self._adj_set[node])

    def has_edge(self, node1, node2):
        way1 = node1 in self._adj_set[node2]
        way2 = node2 in self._adj_set[node1]
        assert way1 == way2, 'adj_set not symmetric'
        existence_str = 'exists' if way1 else 'does not exist'
        log(existence_str)

    def log_node_info(self, node):
        deg = self.get_deg(node)
        log(f'node: {node}')
        log(f'deg: {deg}')

    def run(self):
        while True:
            try:
                command = self.gsh_read()
                self.tick(command)
            except Exception as e:
                log(f'failed: {type(e)} {e}')


if __name__ == '__main__':
    gsh = GraphShell()
    gsh.run()
