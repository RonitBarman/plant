#!/bin/python3
import sys
import random
import pickle
from graph_helpers import *

def get_same_graph_name2num(el_path):
    nodes = list(read_in_nodes(el_path))
    random.shuffle(nodes)
    return {name : num for num, name in enumerate(nodes, 1)}

def get_cross_graph_num2num(el1_name2num, el2_name2num):
    el1_keys = set(el1_name2num.keys())
    el2_keys = set(el1_name2num.keys())
    assert all([k in el2_keys for k in el1_keys])
    assert all([k in el1_keys for k in el2_keys])

    return {el1_name2num[name] : el2_name2num[name] for name in el1_name2num}

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

def get_all_outputs(el1_path, el2_path):
    # get mapping
    el1_name2num = get_same_graph_name2num(el1_path)
    el2_name2num = get_same_graph_name2num(el2_path)
    cross_num2num = get_cross_graph_num2num(el1_name2num, el2_name2num)

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
    el1_path = sys.argv[1]
    el2_path = sys.argv[2]
    mapping, combined_edges = get_all_outputs(el1_path, el2_path)
    output_mapping(mapping, 'mapping.txt')
    output_combined_edges(combined_edges, 'combined_edges.txt')