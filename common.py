import json
import os

def list_sum(a, b):
    c = [0] * len(a)
    for i in range(len(a)):
        c[i] = a[i] + b[i]
    return c

def json_print(a):
    print(json.dumps(a, sort_keys=True, indent=2))
    return

pim_tree_source_folder = "/home/upmem0037/kanghongbo/code/fast_skip_list"
range_partitioning_folder = "/home/upmem0037/kanghongbo/code/pim_skip_list_partitioned"

jump_push_folder = ""

microbenchmark_folder = "/scratch/pim_tree_data"
microbenchmark_init_file = os.path.join(microbenchmark_folder, "init.insorted")

wiki_folder = "/scratch/wiki_data/"
wiki_init_file = os.path.join(wiki_folder, "wiki_1000M_init.binary")
wiki_predecessor_file = os.path.join(wiki_folder, "wiki_200M_predecessor.binary")
wiki_insert_file = os.path.join(wiki_folder, "wiki_200M_insert.binary")

ycsb_folder = "/scratch/ycsb_data/"