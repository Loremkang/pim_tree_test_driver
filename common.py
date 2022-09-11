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
# pim_tree_exec = os.path.join(pim_tree_source_folder, "build/pim_tree_host")

range_partitioning_folder = "/home/upmem0037/kanghongbo/code/pim_skip_list_partitioned"
# range_partitioning_exec = os.path.join(range_partitioning_folder, "build/fast_skip_list_host")

before_chunking_folder = "/home/upmem0037/kanghongbo/code/before_chunking"

benchmark_folder = "/scratch/pim_workloads"
microbenchmark_init_file = os.path.join(benchmark_folder, "init.in")
microbenchmark_init_file_sorted = os.path.join(benchmark_folder, "init.insorted")
microbenchmark_folder = os.path.join(benchmark_folder, "micro")
ycsb_folder = os.path.join(benchmark_folder, "ycsb")

wiki_folder = os.path.join(benchmark_folder, "wiki")
wiki_init_file = os.path.join(wiki_folder, "wiki_1000M_init.binary")
wiki_predecessor_file = os.path.join(wiki_folder, "wiki_200M_predecessor.binary")
wiki_insert_file = os.path.join(wiki_folder, "wiki_200M_insert.binary")

ycsb_folder = "/scratch/ycsb_data/"