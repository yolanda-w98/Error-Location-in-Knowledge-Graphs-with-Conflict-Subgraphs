import time
from collections import defaultdict

def read_triplets_with_labels(file_path):
    """读取包含标签的三元组文件 (txt格式)"""
    triplets = {}
    with open(file_path, 'r') as file:
        for line in file:
            head, tail, relation, label = line.strip().split()
            triplets[(head, tail, relation)] = label
    return triplets

def read_rings(file_path):
    """读取环文件 (txt格式)"""
    rings = []
    with open(file_path, 'r') as file:
        for line in file:
            ring = line.strip().split()
            rings.append(ring)
    return rings

# 函数：为给定的三元组找到指定数量的包含它的环
def find_rings_for_triplet(triplet, rings, num_rings):
    found_rings = []
    for ring in rings:
        for i in range(len(ring)):
            head, tail = ring[i], ring[(i + 1) % len(ring)]
            if int(triplet[0]) == int(head) and int(triplet[1]) == int(tail):
                found_rings.append(ring)
                # print(ring)
                break
        if len(found_rings) == num_rings:
            break
    return found_rings

# 函数：检查环中是否存在large_triplets中标签为0的三元组
def check_rings_for_label_zero(rings, large_triplets):
    count = 0
    flag = False
    for ring in rings:
        for i in range(len(ring)):
            head = ring[i]
            tail = ring[(i + 1) % len(ring)]
            # 检查大的三元组列表中是否存在与当前头尾节点匹配的且标签为0的三元组
            for key in large_triplets:
                if key[0] == head and key[1] == tail and large_triplets[key] == '0':
                    flag = True
                    break
            if flag:
                count += 1
                break
    if count == len(rings):
        return True 
    return False


def write_selected_triplets_to_file(selected_triplets, file_path):
    with open(file_path, 'w') as file:
        for triplet in selected_triplets:
            file.write(f"{triplet[0]} {triplet[1]} {triplet[2]} {triplet[3]}\n")

def read_triplets(file_path):
    triplets = {}
    with open(file_path, 'r') as file:
        for line in file:
            head, tail, relation, label = line.strip().split()
            # triplets[(head, tail)] = (relation, label)
            triplets[(head, tail)] = label
    return triplets

def read_rings(file_path):
    rings = []
    with open(file_path, 'r') as file:
        for line in file:
            rings.append(line.strip().split())
    return rings

def count_cooccurrences(triplets, rings):
    cooccurrence_count = defaultdict(int)
    for ring in rings:
        ring_triplets = set()
        for i in range(len(ring)):
            head = ring[i]
            tail = ring[(i + 1) % len(ring)]
            if (head, tail) in triplets:
                ring_triplets.add((head, tail))

        for triplet1 in ring_triplets:
            for triplet2 in ring_triplets:
                if triplet1 != triplet2:
                    label1 = triplets[triplet1]
                    label2 = triplets[triplet2]
                    if label1 == '1' and label2 == '0':
                        cooccurrence_count[(triplet1[0], triplet1[1])] += 1

    return cooccurrence_count

def mark_triplets(triplets, cooccurrence_count, threshold=1):
    marked_triplets = {}
    for (head, tail), label in triplets.items():
        triplet_key = (head, tail)
        if label == '1':
            marked_label = 0 if cooccurrence_count[triplet_key] > threshold else 1
            marked_triplets[triplet_key] = (label, marked_label)
        if label == '0':
            marked_label = 0
            marked_triplets[triplet_key] = (label, marked_label)
    return marked_triplets

def write_marked_triplets(file_path, marked_triplets):
    with open(file_path, 'w') as file:
        for (head, tail), (original_label, marked_label) in marked_triplets.items():
            file.write(f"{head}\t{tail}\t{original_label}\t{marked_label}\n")

replacement_ratio = 0.1
base_path = "/data/HitCon/nell/"
rings_file = base_path + 'circles/nell_5_3.txt'
# graph_file = base_path + 'sample/replace_' + str(replacement_ratio*100) + 'nell_5_3.txt'
graph_file = base_path + 'sample/3hop_replace_' + str(replacement_ratio*100) + 'nell_5_3.txt'

# shortest
# hitting_triples_file =  base_path + 'results/labeled_hitting_set_for_shortest_'+ str(replacement_ratio*100) + 'nell_5_3.txt'
# detect_file_path = base_path + 'final_result/detect_hitting_shortest_ring_' + str(replacement_ratio*100) + 'nell_5_3.txt'

# fixed
# hitting_triples_file = base_path + 'results/labeled_minus_hitting_set_for_3hop' + str(replacement_ratio*100) + 'nell_5_3.txt'
# detect_file_path = base_path + 'final_result/detect_minus_hitting_3hop_error_ring_' + str(replacement_ratio*100) + 'nell_5_3.txt'

# dynamic

hitting_triples_file = base_path + 'results/labeled_all_limit_hitting_set_for_3hop' + str(replacement_ratio*100) + 'nell_5_3.txt'
detect_file_path = base_path + 'results/detect_all_limit_hitting_set_for_3hop' + str(replacement_ratio*100) + 'nell_5_3.txt'

triplets_with_labels = read_triplets_with_labels(hitting_triples_file)
rings = read_rings(rings_file)
large_triplets_with_labels = read_triplets_with_labels(graph_file)

start = time.time()
selected_triplets = set()
for triplet_key, triplet_label in triplets_with_labels.items():
    found_rings = find_rings_for_triplet(triplet_key, rings, num_rings=3)
    if check_rings_for_label_zero(found_rings, large_triplets_with_labels):
        selected_triplets.add(triplet_key + (triplet_label,))
end = time.time()


write_selected_triplets_to_file(selected_triplets, detect_file_path)

print("# hitting set: ", len(triplets_with_labels))
print("# pass detection: ", len(selected_triplets))
print("time: ", end-start)

cooccurrence_path = base_path + 'results/after_detect_all_limit_hitting_set_for_shortest_'+ str(replacement_ratio*100) + 'nell_5_3.txt'
ring_path = base_path + 'circles/error_ring_3hop_'+ str(replacement_ratio*100) + 'nell_5_3.txt'

triplets = read_triplets(detect_file_path)
rings = read_rings(ring_path)
cooccurrence_count = count_cooccurrences(triplets, rings)
marked_triplets = mark_triplets(triplets, cooccurrence_count)
write_marked_triplets(cooccurrence_path, marked_triplets)