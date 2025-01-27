#!/pkg/python/3.7.4/bin/python3
import sys
import random
import pickle
from graph_helpers import *
from ortholog_helpers import *

def get_same_graph_name2num(el_path):
    nodes = list(read_in_nodes(el_path))
    random.shuffle(nodes)
    return {name : num for num, name in enumerate(nodes)}

def get_cross_graph_num2num(el1_name2num, el2_name2num, s1_to_s2_orthologs):
    assert s1_to_s2_orthologs != None

    if type(s1_to_s2_orthologs) is SelfOrthos:
        return get_cross_graph_num2num_self_orthos(el1_name2num, el2_name2num)
    else:
        return get_cross_graph_num2num_orthos(el1_name2num, el2_name2num, s1_to_s2_orthologs)

def get_cross_graph_num2num_self_orthos(el1_name2num, el2_name2num):
    el1_names = set(el1_name2num.keys())
    el2_names = set(el2_name2num.keys())
    all_names = el1_names.union(el2_names)
    max_len = max(len(el1_names), len(el2_names))
    num2num = dict()

    for name in all_names:
        if name in el1_name2num and name in el2_name2num:
            num2num[el1_name2num[name]] = el2_name2num[name]

    for i in range(max_len):
        if i not in num2num:
            num2num[i] = max_len

    return num2num

def get_cross_graph_num2num_orthos(el1_name2num, el2_name2num, s1_to_s2_orthologs):
    el1_names = el1_name2num.keys()
    el2_names = el2_name2num.keys()
    max_len = max(len(el1_names), len(el2_names))
    num2num = dict()

    for el1_name in s1_to_s2_orthologs:
        el2_name = s1_to_s2_orthologs[el1_name]

        if el1_name in el1_name2num and el2_name in el2_name2num:
            num2num[el1_name2num[el1_name]] = el2_name2num[el2_name]

    for i in range(max_len):
        if i not in num2num:
            num2num[i] = max_len

    return num2num

def get_name2globnum(el1_name2num, el2_name2num):
    num_el1_keys = len(el1_name2num.keys())
    el1_name2globnum = el1_name2num
    el2_name2globnum = dict()

    for name, num in el2_name2num.items():
        el2_name2globnum[name] = num + num_el1_keys

    return el1_name2globnum, el2_name2globnum

def get_num_el(el, el_name2num):
    num_el = []

    for node1, node2 in el:
        num_el.append((el_name2num[node1], el_name2num[node2]))

    return num_el

def get_regal_el(num_el):
    edge_set = set()

    for num1, num2 in num_el:
        assert type(num1) is int and type(num2) is int

        if num1 != num2:
            edge_set.add((min(num1, num2), max(num1, num2)))

    return sorted(list(edge_set))

def get_all_outputs(el1_path, el2_path, s1_to_s2_orthologs):
    # get mapping
    el1_name2num = get_same_graph_name2num(el1_path)
    el2_name2num = get_same_graph_name2num(el2_path)
    cross_num2num = get_cross_graph_num2num(el1_name2num, el2_name2num, s1_to_s2_orthologs)

    # get combined edges
    el1_name2globnum, el2_name2globnum = get_name2globnum(el1_name2num, el2_name2num)
    el1 = read_in_el(el1_path)
    el2 = read_in_el(el2_path)
    num_el1 = get_num_el(el1, el1_name2globnum)
    num_el2 = get_num_el(el2, el2_name2globnum)
    regal_el1 = get_regal_el(num_el1)
    regal_el2 = get_regal_el(num_el2)
    combined_el = regal_el1 + regal_el2
    return cross_num2num, combined_el

def output_mapping(mapping, fname):
    outf = open(fname, 'wb')
    pickle.dump(mapping, outf)

def output_combined_edges(combined_edges, fname):
    outf = open(fname, 'w')
    outf.write('\n'.join([f'{num1} {num2} {{\'weight\': 1.0}}' for num1, num2 in combined_edges]))

if __name__ == '__main__':
    MODE = 'iid'
    
    if MODE == 'snap':
        snap1 = sys.argv[1]
        snap2 = sys.argv[2]
        base_out = sys.argv[3]
        s1_to_s2_orthologs = SelfOrthos()
        el1_path = get_snap_graph_path(snap1)
        el2_path = get_snap_graph_path(snap2)
    elif MODE == 'iid':
        species1 = sys.argv[1]
        species2 = sys.argv[2]
        base_out = sys.argv[3]
        s1_to_s2_orthologs = get_s1_to_s2_orthologs(species1, species2)
        el1_path = get_graph_path(species1)
        el2_path = get_graph_path(species2)

    mapping, combined_edges = get_all_outputs(el1_path, el2_path, s1_to_s2_orthologs)
    mapping_path = f'/home/wangph1/plant/data/regal/{base_out}_edges-mapping-permutation.txt'
    output_mapping(mapping, mapping_path)
    combined_edges_path = f'/home/wangph1/plant/data/regal/{base_out}_combined_edges.txt'
    output_combined_edges(combined_edges, combined_edges_path)

    for openlab_path in [mapping_path, combined_edges_path]:
        print(f'scp wangph1@openlab.ics.uci.edu:{openlab_path} /Users/patrickwang/Downloads/REGAL-master/data;')

    el1_nodes = read_in_nodes(el1_path)
    print(f'python3 regal.py --input data/{base_out}_combined_edges.txt --split {len(el1_nodes)}')
