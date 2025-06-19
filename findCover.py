import time
import sys
sys.setrecursionlimit(10000)

class Triplet:
    def __init__(self, triplet, D, cover_set):
        self.triplet = triplet
        self.D = D
        self.cover_set = cover_set

class TripletSet:
    def __init__(self, tripletSet, D, num):
        self.triplet = tripletSet
        self.D = D
        self.num = num

class TripletsPropertyDict:
    def __init__(self):
        self.triplets2property = {}
        self.cover = {}
        self.mode = {"error":0, "all":1}
        self.rings = 0

    def add(self, triplets): 
        if triplets not in self.triplets2property:
            property_list = [0]*2
            self.triplets2property[triplets] = property_list
            self.cover[triplets] = []
        return triplets

    def add_ring(self):
        self.rings += 1
    
    def exist(self, triplet):
        return False if self.triplets2property.get(triplet) is None else True
    
    def add_cover(self, triplet, mode, cover_ring=None):
        self.triplets2property[triplet][self.mode[mode]] +=1
        if mode == "error":
            self.cover[triplet].append(cover_ring)

    def compute_D(self):
        value_list = []
        for triplet, properties in self.triplets2property.items():
            SC = properties[self.mode["all"]]/self.rings
            CC = 0 if properties[self.mode["all"]]==0 else properties[self.mode["error"]]/properties[self.mode["all"]]
            print(properties[self.mode["all"]], CC, triplet)
            D = SC-CC
            value_list.append(Triplet(triplet, D, self.cover[triplet]))
        sorted_value_list = sorted(value_list, key=lambda x: x.D)
        print("Number of rings: ", len(sorted_value_list))
        return sorted_value_list
        
def extract_error_triplets(triplets, error_path, error_path_write):
    error_list = []
    num_R = 0
    with open(error_path, 'r') as file:
        for line in file:
            line = line.strip().split('\t')
            line.append(line[0])
            triplets_set = set()
            for i in range(len(line)-1):
                triplets_set.add(triplets.add((int(line[i]), int(line[i+1]))))
            for triplet in triplets_set:
                triplets.add_cover(triplet, "error", num_R)
            error_list.append(triplets_set)
            num_R += 1
    with open(error_path_write, "w") as file:
        for triplets_set in error_list:
            int_set_str = '\t'.join(map(str, triplets_set))
            file.write(int_set_str + "\n")
    return error_list, num_R

def extract_all_triplets(triplets, path):
    with open(path, 'r') as file:
        for line in file:
            triplets.add_ring()
            line = line.strip().split('\t')
            line.append(line[0])
            triplets_set = set()
            for i in range(len(line)-1):
                if triplets.exist((int(line[i]), int(line[i+1]))):
                    triplets_set.add((int(line[i]), int(line[i+1])))
            for triplet in triplets_set:
                triplets.add_cover(triplet, "all")
 
def extract_triplets(error_path, all_path, error_path_write):
    triplets = TripletsPropertyDict()
    error_list, num_R = extract_error_triplets(triplets, error_path, error_path_write)
    extract_all_triplets(triplets, all_path)
    print("Number of error rings: ", num_R)
    return triplets.compute_D(), error_list, num_R


class solution:
    def __init__(self, sorted_value_list, num_R, error_list, max_t, output_path):
        self.num_R = num_R
        self.sorted_value_list = sorted_value_list
        self.error_list = error_list
        self.max_t = max_t
        self.output_path_all = output_path + "AllCoveredSets.txt"
        self.output_info = output_path + "Coveredinfo.txt"
        self.output_path_best = output_path + "BestCoveredSets.txt"
        self.set_be_considered = 0
        self.solutionList = []
        self.min_length_D = 1
        self.min_length = max_t

    # solution
    def solution(self):
        for i in range(len(self.sorted_value_list)):
            self.expand_triplets(set(), i, set(), 0)
        self.Find_Best()
        print("Number of set that considered: ", self.set_be_considered)

    # 寻找最优
    def Find_Best(self):
        sortedSolutionList = sorted(self.solutionList, key=lambda x: x.num)
        markedSet = set()
        non_redundant_List = []
        for i in range(len(sortedSolutionList)):
            if i in markedSet:
                continue
            non_redundant_List.append(sortedSolutionList[i])
            for j in range(i, len(sortedSolutionList)):
                if j in markedSet:
                    continue
                if sortedSolutionList[i].triplet.issubset(sortedSolutionList[j].triplet):
                    markedSet.add(j)
        non_redundant_List = sorted(non_redundant_List, key = lambda x:x.D)
        self.save_best_triplets(non_redundant_List)

    def find_a_cover(self, covered_set, average):
        if len(covered_set) <= self.min_length:
            self.min_length = len(covered_set)
            self.min_length_D = average
        self.save_triplets(covered_set, average, self.output_path_all)
        self.save_info(covered_set, average, self.output_info)
        self.solutionList.append(TripletSet(covered_set, average, len(covered_set)))

    def expand_triplets(self, current_set, current_index, current_cover, current_Sum_D):
        if len(current_set) >= self.max_t:
            return

        expanded_Sum_D = current_Sum_D + self.sorted_value_list[current_index].D
        average = expanded_Sum_D/(len(current_set)+1)

        if len(current_set) + 1 >= self.min_length and average > self.min_length_D:
            return
               
        expanded_set = set(current_set)
        expanded_set.add(self.sorted_value_list[current_index].triplet)
        expanded_cover = set(current_cover)
        expanded_cover = expanded_cover.union(set(self.sorted_value_list[current_index].cover_set))

        if len(expanded_cover)==self.num_R:
            self.find_a_cover(expanded_set, average)
            return
        for i in range(current_index+1, len(self.sorted_value_list)):
            self.expand_triplets(expanded_set, i, expanded_cover, expanded_Sum_D)

    def save_triplets(self, covered_set, score, path):
        with open(path, "a")as f:
            f.write("#"+str(score)+'\n')
            f.write('\n'.join(map(str, covered_set))+'\n')
        self.set_be_considered += 1
    def save_info(self, covered_set, score, path):
        with open(path, "a")as f:
            f.write("# Score: " + str(score) + ". Triplets len: " + str(len(covered_set)) + ". Set_be_considered: " + str(self.set_be_considered) + "\n")
    def save_best_triplets(self, tripleSets):
        length = tripleSets[0].num
        min_D = tripleSets[0].D
        for tripletSet in tripleSets:
            if tripletSet.D != min_D:
                break
            self.save_triplets(tripletSet.triplet, tripletSet.D, self.output_path_best)
        print("Number of t in the best: ", length)
        print("Best D: ", tripleSets[0].D)

replacement_ratio = 0.1
number = 23
base_path = "./data/"
error_path = base_path  + str(number) + 'error_ring.txt'
all_path = base_path  + str(number) + 'all_ring.txt'


result_base_path = "D:\Projects\conflict2\\result3\\"
error_path_write = result_base_path  + str(number) + "error_rings" + ".txt"
output_path = result_base_path  + str(number) + "covered_rings" 

start_time = time.time()
sorted_value_list, error_list, num_R = extract_triplets(error_path, all_path, error_path_write)
max_t = min(num_R, len(sorted_value_list))
print(max_t)
middle_time = time.time()
s = solution(sorted_value_list, num_R, error_list, max_t, output_path)

s.solution()
end_time = time.time()

print("Time to compute D(s): ", middle_time-start_time)
print("Time to find best set(s): ", end_time-middle_time)
print("Total Time: ", end_time-start_time)