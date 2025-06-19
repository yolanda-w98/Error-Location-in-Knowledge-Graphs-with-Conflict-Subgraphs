import random
from collections import OrderedDict
import networkx as nx
import logging
import time

def read_triples(file_path):
    triplets = []

    with open(file_path, 'r') as file:
        for line in file:
            triplet = line.strip().split()
            triplet.append('1')
            triplets.append(triplet)

    return triplets

def replace_relations(triplets, replacement_ratio):
    num_to_replace = int(len(triplets) * replacement_ratio)
    indices_to_replace = random.sample(range(len(triplets)), num_to_replace)

    for idx in indices_to_replace:
        original_triplet = triplets[idx]
        new_relation = str(random.randint(int(original_triplet[2]), 200))
        triplets[idx] = [original_triplet[0], original_triplet[2], new_relation, '0']  # 替换关系并标注为0

    return triplets

def save_triples(triplets, file_path):
    with open(file_path, 'w') as file:
        for triplet in triplets:
            file.write('\t'.join(triplet) + '\n')

def read_error_triples(file_path):
    error_triples = set()
    with open(file_path, 'r') as file:
        for line in file:
            src, dst, relation, label = line.strip().split()
            if label == '0':
                error_triples.add((src, dst))
    return error_triples

def read_rings(file_path):
    with open(file_path, 'r') as file:
        return [line.strip().split() for line in file]

def find_rings_with_errors(rings, error_triples):
    rings_with_errors = set()
    found_error_triples = set()
    for ring in rings:
        for i in range(len(ring) - 1):
            edge = (ring[i], ring[i + 1])
            if edge in error_triples and edge not in found_error_triples:
                rings_with_errors.add(tuple(ring)) 
                found_error_triples.add(edge)
                break
    return rings_with_errors

def write_rings_to_file(rings, file_path):
    with open(file_path, 'w') as file:
        for ring in rings:
            file.write('\t'.join(ring) + '\n')

class Graph:
    def __init__(self, vertices):
        self.vertices = vertices
        self.adjacency_list = {}
        self.visited = [False] * vertices
        self.circle_flag = [False] * vertices 
        self.stack = []
        self.all_cycles = []
        self.count = 0
        self.unique_cycles = OrderedDict()
        self.name = 'default'

    def add_edge(self, u, v):
        if u in self.adjacency_list:
            self.adjacency_list[u].append(v)
        else:
            self.adjacency_list[u] = [v]

    def find_cycles(self, lb, ub):
        self.circle_flag = [False] * self.vertices 
        for node in range(self.vertices):
            if self.circle_flag[node]:
                continue
            self.dfs(node, lb, ub)

    def dfs(self, node, lb, ub, path):
        self.visited[node] = True   # 这个visited我忘了干啥的了，你再看看，但不是我们需要的那个visited
        self.stack.append(node)
        
        f = open(path, 'a') # 环存储路径
        if node in self.adjacency_list and len(self.stack) <= ub: #这里是上界
            for neighbor in self.adjacency_list[node]:
                if not self.visited[neighbor]:
                    self.dfs(neighbor, lb, ub)
                elif neighbor in self.stack:
                    cycle = self.stack[self.stack.index(neighbor):]
                    if len(cycle) >= lb:             #这里是下界
                        cycle_string = ' '.join(map(str, cycle))
                        if cycle_string not in self.unique_cycles:  # 检查环是否已经存在
                            self.unique_cycles[cycle_string] = cycle
                            for item in cycle:
                                self.circle_flag[item] = True
                                f.write(str(item) + "\t")
                            f.write("\n")
                            self.count += 1
            f.close()
        self.stack.pop()
        self.visited[node] = False

    def find_cycles_wp(self, lb, ub, path):
        for node in range(self.vertices):
            self.dfs_wp(node, lb, ub, path)

    def dfs_wp(self, node, lb, ub, path):
        self.visited[node] = True   # 这个visited我忘了干啥的了，你再看看，但不是我们需要的那个visited 用于记录深度优先遍历中是否已经处理过
        self.stack.append(node)
        
        f = open(path, 'a') # 环存储路径
        if node in self.adjacency_list and len(self.stack) <= ub: #这里是上界
            for neighbor in self.adjacency_list[node]:
                if not self.visited[neighbor]:
                    self.dfs_wp(neighbor, lb, ub, path)
                elif neighbor in self.stack:
                    cycle = self.stack[self.stack.index(neighbor):]
                    if len(cycle) >= lb:             #这里是下界
                        cycle_string = ' '.join(map(str, cycle))
                        if cycle_string not in self.unique_cycles:  # 检查环是否已经存在
                            self.unique_cycles[cycle_string] = cycle
                            for item in cycle:
                                f.write(str(item) + "\t")
                            f.write("\n")
                            self.count += 1
            f.close()
        self.stack.pop()
        self.visited[node] = False

def read_edges_from_file(file_path):
    with open(file_path, "r") as file:
        lines = file.readlines()
    # vertices = max([int(line.split()[0]) for line in lines]) + 1
    vertices = 5000000
    g = Graph(vertices)
    for line in lines:
        u, v, c, l = map(int, line.strip().split()) 
        if u not in g.adjacency_list.keys():
            g.add_edge(u, v)
        if v in g.adjacency_list[u]:
            continue    
        g.add_edge(u, v)
    return g

def read_error_triples(file_path):
    error_triples = set()
    with open(file_path, 'r') as file:
        for line in file:
            src, dst, relation, label = line.strip().split()
            if label == '0':
                error_triples.add((src, dst))
    return error_triples

def read_rings(file_path):
    with open(file_path, 'r') as file:
        return [line.strip().split() for line in file]

def find_rings_with_errors(rings, error_triples):
    rings_with_errors = []
    for ring in rings:
        for i in range(len(ring)):
            if i < len(ring) - 1 and (ring[i], ring[i + 1]) in error_triples:
                rings_with_errors.append(ring)
                break
    return rings_with_errors

def write_rings_to_file(rings, file_path):
    with open(file_path, 'w') as file:
        for ring in rings:
            file.write('\t'.join(ring) + '\n')

def read_graph(file_path):
    G = nx.DiGraph()
    edge_info = {}
    with open(file_path, 'r') as file:
        for line in file:
            src, dst, relation, label = line.strip().split()
            G.add_edge(src, dst)
            edge_info[(src, dst)] = (relation, label)
    return G, edge_info

def read_error_rings(file_path):
    rings = []
    with open(file_path, 'r') as file:
        for line in file:
            nodes = line.strip().split()
            rings.append(nodes)
    return rings

def get_x_hop_neighbors(G, node):
    edges_within_hops = nx.bfs_edges(G, source=node, depth_limit=2)
    neighbors = set()
    for u, v in edges_within_hops:
        neighbors.add(v)
        if u != node:
            neighbors.add(u)
    neighbors.discard(node)
    return neighbors
    # return nx.single_source_shortest_path_length(G, node, cutoff=3)

def find_subgraph(G, edge_info, rings):
    subgraph_triplets = set()
    for ring in rings:
        for node in ring:
            neighbors = get_x_hop_neighbors(G, node)
            for neighbor in neighbors:
                if G.has_edge(node, neighbor):
                    relation, label = edge_info[(node, neighbor)]
                    subgraph_triplets.add((node, neighbor, relation, label))
                if G.has_edge(neighbor, node):
                    relation, label = edge_info[(neighbor, node)]
                    subgraph_triplets.add((neighbor, node, relation, label))
    return subgraph_triplets


def write_subgraph_to_file(subgraph, file_path):
    label_0_count = 0
    with open(file_path, 'w') as file:
        for src, dst, relation, label in subgraph:
            file.write(f'{src} {dst} {relation} {label}\n')
            if label == '0':
                label_0_count += 1

    total_count = len(subgraph)
    label_0_proportion = label_0_count / total_count if total_count > 0 else 0
    return label_0_count, label_0_proportion

# inject conflict
replacement_ratio = 0.1
base_path = "/data/HitCon/nell/"
file_path = base_path + "sample/nell_5_3.txt"
error_triples_path = base_path + "sample/replace_" + str(replacement_ratio*100) + "nell_5_3.txt"

triplets = read_triples(file_path)
triplets_with_replaced_relations = replace_relations(triplets, replacement_ratio)
save_triples(triplets_with_replaced_relations, error_triples_path)

# get shortest rings
rings_file = base_path + 'circles/nell_5_3.txt'
shortest_file = base_path + 'circles/shortest_ring_' + str(replacement_ratio*100) + 'nell_5_3.txt'

error_triples = read_error_triples(error_triples_path)
all_rings = read_rings(rings_file)

rings_with_errors = find_rings_with_errors(all_rings, error_triples)
write_rings_to_file(rings_with_errors, shortest_file)

# get 3 hops triples
output_file_path = base_path + 'sample/3hop_replace_'+ str(replacement_ratio*100) +'nell_5_3.txt'
G, edge_info = read_graph(error_triples_path)
error_rings = read_error_rings(shortest_file)
subgraph_triplets = find_subgraph(G, edge_info, error_rings)
label_0_count, label_0_proportion = write_subgraph_to_file(subgraph_triplets, output_file_path)

print(f"Label 0 count: {label_0_count}, Proportion: {label_0_proportion:.2f}")

# get rings with 3-5 length
file_path = base_path + 'sample/3hop_replace_'+ str(replacement_ratio*100) +'nell_5_3.txt'
rings_path = base_path + "circles/all_ring_3hop_" + str(replacement_ratio*100) + "nell_5_3.txt"

g = read_edges_from_file(file_path)
print("loading finish!")

g.find_cycles_wp(3, 5, rings_path)
print(g.count)

# get error rings
error_triples_file = base_path + 'sample/3hop_replace_' + str(replacement_ratio*100) + 'nell_5_3.txt'
output_file = base_path + 'circles/error_ring_3hop_' + str(replacement_ratio*100) + 'nell_5_3.txt'

error_triples = read_error_triples(error_triples_file)
rings = read_rings(rings_path)
rings_with_errors = find_rings_with_errors(rings, error_triples)
write_rings_to_file(rings_with_errors, output_file)