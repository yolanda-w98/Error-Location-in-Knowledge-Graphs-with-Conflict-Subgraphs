import csv
from collections import defaultdict
import time
import networkx as nx

def read_single_triplets(file_path):
    triplets = {}
    with open(file_path, 'r') as file:
        for line in file:
            head, tail, relation, label = line.strip().split()
            triplets[(head, tail, relation)] = {'label': label, 'error_count': 0, 'all_count': 0}
    return triplets

def count_rings_in_triplets(rings_file, triplets, count_key):
    with open(rings_file, 'r') as file:
        for line in file:
            ring = line.strip().split()
            for i in range(len(ring)):
                head, tail = ring[i], ring[(i + 1) % len(ring)]
                for key in triplets.keys():
                    if key[0] == head and key[1] == tail:
                        triplets[key][count_key] += 1
                        break 

def write_results(triplets, file_path):
    with open(file_path, 'w') as file:
        for (head, tail, relation), data in triplets.items():
            file.write(f"{head} {tail} {relation} {data['label']} {data['error_count']} {data['all_count']}\n")


def read_triplets(file_path):
    triplets = []
    with open(file_path, 'r') as file:
        reader = csv.reader(file, delimiter=' ')
        for row in reader:
            if int(row[4]) == 0 and int(row[5]) == 0:
                 continue
            triplets.append({
                'head': int(row[0]),
                'tail': int(row[1]),
                'relation': int(row[2]),
                'error_count': int(row[4]),
                'all_count': int(row[5])
            })
    return triplets

def read_rings(file_path):
    rings = []
    with open(file_path, 'r') as file:
        for line in file:
            ring = [int(node) for node in line.strip().split()]
            rings.append(ring)
    return rings

def update_coverage(triplet, rings):
    covered_rings = set()
    for i, ring in enumerate(rings):
        for j in range(len(ring) - 1):  
            ring_triplet = (ring[j], ring[(j + 1) % len(ring)])
            if ring_triplet[0] == triplet['head'] and ring_triplet[1] == triplet['tail']:
                # print(ring)
                covered_rings.add(i)
                break
    return covered_rings


# fixed strategy
def select_triplets_minus(triplets, error_rings, all_rings):
    error_ring_set = set(range(len(error_rings))) 
    all_ring_set = set(range(len(all_rings)))     


    for triplet in triplets:
        triplet['covered_error_rings'] = update_coverage(triplet, error_rings)
        triplet['covered_all_rings'] = update_coverage(triplet, all_rings)

    result = []

    while error_ring_set:
        for triplet in triplets:
            triplet['error_count'] = len(triplet['covered_error_rings'] & error_ring_set)
            triplet['all_count'] = len(triplet['covered_all_rings'] & all_ring_set)
            triplet['conflict_coverage'] = triplet['error_count'] / len(error_ring_set) if error_ring_set else 0
            triplet['set_coverage'] = triplet['all_count'] / len(all_ring_set) if all_ring_set else 0

        triplet = min(triplets, key=lambda x: (x['set_coverage'] - x['conflict_coverage']))
        if not triplet:
            break
        result.append(triplet)
        error_ring_set -= triplet['covered_error_rings']
        all_ring_set -= triplet['covered_all_rings']

    return result


def select_triplets_all_minus(triplets, error_rings, all_rings):
    error_ring_set = set(range(len(error_rings)))  
    all_ring_set = set(range(len(all_rings)))     


    for triplet in triplets:
        triplet['covered_error_rings'] = update_coverage(triplet, error_rings)
        triplet['covered_all_rings'] = update_coverage(triplet, all_rings)

    result = []

    for triplet in triplets:
        triplet['error_count'] = len(triplet['covered_error_rings'] & error_ring_set)
        triplet['all_count'] = len(triplet['covered_all_rings'] & all_ring_set)
        triplet['conflict_coverage'] = triplet['error_count'] / len(error_ring_set) if error_ring_set else 0
        triplet['set_coverage'] = triplet['all_count'] / len(all_ring_set) if all_ring_set else 0

    eligible_triplets = [t for t in triplets if t['set_coverage'] - t['conflict_coverage'] <= 0]

    return eligible_triplets


def write_simplified_triplets_to_file(selected_triplets, file_path):
    with open(file_path, 'w') as file:
        for triplet in selected_triplets:
            file.write(f"{triplet['head']}\t{triplet['tail']}\t{triplet['relation']}\n")

def load_replace_triples(file_path):
    replace_triples = {}
    with open(file_path, 'r') as file:
        for line in file:
            head, tail, _, label = line.strip().split()
            replace_triples[(head, tail)] = label
    return replace_triples

def label_3hop_triples(hitting_set_file, replace_triples, output_file):
    with open(hitting_set_file, 'r') as file, open(output_file, 'w') as out:
        for line in file:
            head, tail, relation = line.strip().split()
            label = replace_triples.get((head, tail), 'unknown')
            out.write(f"{head}\t{tail}\t{relation}\t{label}\n")


replacement_ratio = 0.1
base_path = "/data/HitCon/nell/"

# 3hop
triplet_file = base_path + 'sample/3hop_replace_'+ str(replacement_ratio*100) + 'nell_5_3.txt'
error_ring_file = base_path + 'circles/error_ring_3hop_'+ str(replacement_ratio*100) + 'nell_5_3.txt'
all_ring_file = base_path + 'circles/all_ring_3hop_'+ str(replacement_ratio*100) + 'nell_5_3.txt'
output_file = base_path + 'circles/count_3hop_error_ring_'+ str(replacement_ratio*100) + 'nell_5_3.txt'
triplet_file_path = base_path + 'circles/count_3hop_error_ring_'+ str(replacement_ratio*100) + 'nell_5_3.txt'

# shortest
# triplet_file = base_path + 'sample/replace_'+ str(replacement_ratio*100) + 'nell_5_3.txt'
# error_ring_file = base_path + 'circles/shortest_ring_'+ str(replacement_ratio*100) + 'nell_5_3.txt'
# all_ring_file = base_path + 'circles/nell_5_3.txt'
# output_file = base_path + 'circles/new/count_shortest_ring_'+ str(replacement_ratio*100) + 'nell_5_3.txt'
# triplet_file_path = base_path + 'circles/new/count_shortest_ring_'+ str(replacement_ratio*100) + 'nell_5_3.txt'

triplets = read_single_triplets(triplet_file)
count_rings_in_triplets(error_ring_file, triplets, 'error_count')
count_rings_in_triplets(all_ring_file, triplets, 'all_count')
write_results(triplets, output_file)


triplets = read_triplets(triplet_file_path)
error_rings = read_rings(error_ring_file)
all_rings = read_rings(all_ring_file)
print("loading finish!")

# dynamic strategy
# 3hop
start = time.time()
selected_triplets = select_triplets_all_minus(triplets, error_rings, all_rings)
end = time.time()
hitting_set_file_path = base_path + 'results/all_limit_hitting_set_for_3hop_'+ str(replacement_ratio*100) + 'nell_5_3.txt'

# shortest
# start = time.time()
# selected_triplets = select_triplets_all_minus(triplets, error_rings, all_rings)
# end = time.time()
# hitting_set_file_path = base_path + 'results/all_limit_hitting_set_for_shortest_'+ str(replacement_ratio*100) + 'nell_5_3.txt'

# fixed strategy
# 3hop
# start = time.time()
# selected_triplets = select_triplets_minus(triplets, error_rings, all_rings)
# end = time.time()
# hitting_set_file_path = base_path + 'results/minus_hitting_set_for_3hop_'+ str(replacement_ratio*100) + 'nell_5_3.txt'

# shortest
# start = time.time()
# selected_triplets = select_triplets_minus(triplets, error_rings, all_rings)
# end = time.time()
# hitting_set_file_path = base_path + 'results/minus_hitting_set_for_shortest_'+ str(replacement_ratio*100) + 'nell_5_3.txt'

write_simplified_triplets_to_file(selected_triplets, hitting_set_file_path)
print(end-start)

# label
replace_file_path = base_path + 'sample/3hop_replace_' + str(replacement_ratio*100) + 'nell_5_3.txt'
# dynamic
# 3hop
hitting_set_file_path = base_path + 'results/all_limit_hitting_set_for_3hop_'+ str(replacement_ratio*100) + 'nell_5_3.txt'
output_file_path = base_path + 'results/labeled_all_limit_hitting_set_for_3hop' + str(replacement_ratio*100) + 'nell_5_3.txt'
# shortest
# hitting_set_file_path = base_path + 'results/all_limit_hitting_set_for_shortest_'+ str(replacement_ratio*100) + 'nell_5_3.txt'
# output_file_path = base_path + 'results/labeled_all_limit_hitting_set_for_shortest_' + str(replacement_ratio*100) + 'nell_5_3.txt'

# fixed
# 3hop
# hitting_set_file_path = base_path + 'results/minus_hitting_set_for_3hop_'+ str(replacement_ratio*100) + 'nell_5_3.txt'
# output_file_path = base_path + 'results/labeled_minus_hitting_set_for_3hop' + str(replacement_ratio*100) + 'nell_5_3.txt'
# shortest
# hitting_set_file_path = base_path + 'results/minus_hitting_set_for_shortest_'+ str(replacement_ratio*100) + 'nell_5_3.txt'
# output_file_path = base_path + 'results/labeled_minus_hitting_set_for_shortest_'+ str(replacement_ratio*100) + 'nell_5_3.txt'

replace_triples = load_replace_triples(replace_file_path)
label_3hop_triples(hitting_set_file_path, replace_triples, output_file_path)
