#! python3.5+
# from math import nan
# import os
from dataclasses import field
import json
import inspect
import numpy as np
import csv
from common import json_print

it = "idx_type"
ot = "op_type"
sk = "skew"
tgt = "target"
bs = "batch_size"
es = "evaluation_set_size"
ts = "threshold"

# global default values
idxs = ("pim_tree", "range_partitioning")
ops = ("micro_predecessor", "micro_insert")
skews = [f'{i:.1f}' for i in (0.0, 1.0)]
target = ("throughput",)
batch_size = (1000000,)
evaluation_set_size = (100000000,)

# nan = 0
from math import nan

columns = []

def test_target_setup(tests, target):

    target_requirement=dict(test_throughput="throughput" in target, test_communication="comm" in target, test_component_time="component_time" in target, test_energy="energy" in target)

    val = "nan" if target_requirement["test_throughput"] else ""
    throughput_stats = dict(throughput=val)

    val = "nan" if target_requirement["test_communication"] else ""
    comm_stats = dict(comm_dram=val, comm_pim=val)

    val = "nan" if target_requirement["test_component_time"] else ""
    component_time_stats = dict(time_cpu=val, time_comm=val, time_load=val, time_pim=val)

    val = "nan" if target_requirement["test_energy"] else ""
    energy_stats = dict(energy_cpu=val, energy_comm=val, energy_pim=val)

    global columns
    assert(len(tests) > 0)
    columns = ["idx_type", "op_type", "skew", "batch_size", "evaluation_set_size", "threshold"] + list(target_requirement.keys()) + list(throughput_stats.keys()) + list(comm_stats.keys()) + list(component_time_stats.keys()) + list(energy_stats.keys())

    ret = [{**test, **target_requirement, **throughput_stats, **comm_stats, **component_time_stats, **energy_stats} for test in tests]

    return ret

class TestGenerator(object):
    def throughput_over_bias_between_pim_and_range(self):
        skews = [f'{i:.1f}' for i in np.arange(0, 1.4, 0.2)]
        ops = ("micro_get", "micro_predecessor", "micro_insert", "micro_delete", "micro_scan")
        tests = [{it:i, ot:j, sk:k, bs:q, es:p} for i in idxs for j in ops for k in skews for q in batch_size for p in evaluation_set_size]
        return test_target_setup(tests, target)

    def effect_of_optimizations(self):
        idxs = ("jump_push", "push_pull", "push_pull_chunk", "push_pull_chunk_shadow", "pim_tree")
        tests = [{it:i, ot:j, sk:k, bs:q, es:p} for i in idxs for j in ops for k in skews for q in batch_size for p in evaluation_set_size]
        # json_print(tests)
        return test_target_setup(tests, target)

    def component_time(self):
        idxs = ("pim_tree", "range_partitioning")
        target = ("component_time",)
        skews = ("0.0", "0.6")
        tests = [{it:i, ot:j, sk:k, bs:q, es:p} for i in idxs for j in ops for k in skews for q in batch_size for p in evaluation_set_size]
        return test_target_setup(tests, target)

    def ycsb(self):
        ops = ("ycsb_" + s for s in map(chr, range(ord("a"), ord("e") + 1)))
        tests = [{it:i, ot:j, sk:k, bs:q, es:p} for i in idxs for j in ops for k in skews for q in batch_size for p in evaluation_set_size]
        # json_print(tests)
        return test_target_setup(tests, target)

    def communication(self):
        idxs = ("pim_tree", "range_partitioning", "ab-tree", "bst")
        target = ("comm",)
        tests = [{it:i, ot:j, sk:k, bs:q, es:p} for i in idxs for j in ops for k in skews for q in batch_size for p in evaluation_set_size]
        # json_print(tests)
        return test_target_setup(tests, target)

    def energy(self):
        skews = [f'{i:.1f}' for i in (0.0, 0.6, 1.0)]
        target = ("energy",)
        ops = ("micro_predecessor", "micro_insert", "micro_scan")
        tests = [{it:i, ot:j, sk:k, bs:q, es:p} for i in idxs for j in ops for k in skews for q in batch_size for p in evaluation_set_size]
        return test_target_setup(tests, target)

    def wikipedia(self):
        evaluation_set_size = (200000000,)
        idxs = ("pim_tree", "ab-tree", "bst")
        ops = ("wiki_predecessor", "wiki_insert")
        target = ("throughput", "comm")
        skews = (1.0,)
        tests = [{it:i, ot:j, sk:k, bs:q, es:p} for i in idxs for j in ops for k in skews for q in batch_size for p in evaluation_set_size]
        # json_print(tests)
        return test_target_setup(tests, target)
        
    def communication_over_different_batch_size(self):
        idxs = ("pim_tree",)
        ops = ("micro_predecessor",)
        skews = [f'{i:.1f}' for i in (0.0,)]
        target = ("comm",)
        batch_size = (1000000, 500000, 200000, 100000, 50000, 20000)
        tests = [{it:i, ot:j, sk:k, bs:q, es:p} for i in idxs for j in ops for k in skews for q in batch_size for p in evaluation_set_size]
        return test_target_setup(tests, target)

    def throughput_with_traditional_indexes(self):
        idxs = ("pim_tree", "ab-tree", "bst")
        tests = [{it:i, ot:j, sk:k, bs:q, es:p} for i in idxs for j in ops for k in skews for q in batch_size for p in evaluation_set_size]
        return test_target_setup(tests, target)
    
    def different_threshold(self):
        idxs = ("pim_tree",)
        ops = ("micro_predecessor",)
        skews = (1.0,)
        batch_size = (1000000,)
        threshold = (8, 16, 24, 32)
        target = ("throughput", "comm")
        tests = [{it:i, ot:j, sk:k, bs:q, es:p, ts:t} for i in idxs for j in ops for k in skews for q in batch_size for p in evaluation_set_size for t in threshold]
        return test_target_setup(tests, target)


tg = TestGenerator()
attrs = (getattr(tg, name) for name in dir(tg))
methods = filter(inspect.ismethod, attrs)
all_tests = []
for method in methods:
    delta_tests = method()
    for test in delta_tests:
        if test not in all_tests:
            all_tests.append(test)
        else:
            json_print(test)
    # json_print(delta_tests)

with open('experiments.csv', 'w', newline='') as csvfile:
    fieldnames = columns
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(all_tests)

# a = list(set(throughput_with_traditional))
# print(a)