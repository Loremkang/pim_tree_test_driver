from cmath import nan
import inspect
import os
import csv
from time import sleep
from tqdm import tqdm
import datetime

from common import *

result_folder = ""

def test_traditional(test):
    if (test["idx_type"] in ("ab-tree", "bst")):
        return True
    return False

def command_executor(cmd):
    print(cmd)

def core_command_gen(idx_type, batch_size, skew, op_type):
    if idx_type != "pim_tree" and batch_size != 1000000:
        raise Exception("Invalid batch size")


    init_file = ""
    test_file = ""

    if "ycsb" in op_type:
        raise NotImplemented("Automatic YCSB Test Not Implemented Yet!")
    elif "micro" in op_type:
        init_file = microbenchmark_init_file
        typeid = 0
        if "get" in op_type:
            typeid = 1
        elif "predecessor" in op_type:
            typeid = 3
        elif "scan" in op_type:
            typeid = 4
        elif "insert" in op_type:
            typeid = 5
        elif "delete" in op_type:
            typeid = 6
        else:
            raise Exception("micro invalid type")
        test_file = os.path.join(microbenchmark_folder, f'test_100000000_{skew}_{typeid}.in')
    elif "wiki" in op_type:
        if "predecessor" in op_type:
            test_file = wiki_predecessor_file
        elif "insert" in op_type:
            test_file = wiki_insert_file
        else:
            raise Exception("wiki invalid type")
    

    if idx_type == "pim_tree":
        return f'./build/fast_skip_list_host -c -t -d --top_level_threads 2 -f {init_file} {test_file} --test_batch_size {batch_size}'
    elif idx_type == "range_partitioning":
        pass
    elif idx_type == "jump_push":
        pass
    elif idx_type == "push_pull":
        pass
    elif idx_type == "push_pull_chunk":
        pass
    elif idx_type == "push_pull_chunk_shadow":
        return f'./build/fast_skip_list_host -c -t -d --top_level_threads 1 -f {init_file} {test_file}'

class Test_Runner(object):
    def test_communication(self, tidx, test):
        if (test["test_communication"] == "False"):
            return
        if (test["comm_dram"], test["comm_pim"]) != (nan, nan):
            return
        run_test_cmd = "numactl --cpunodebind=0 --membind=0 " + core_command_gen(test["idx_type"], )
        result_file = os.path.join(result_folder, str(tidx) + "communication.txt")

        command_executor("/bin/bash -c " + run_test_cmd + " > " + result_file)
        (test["comm_dram"], test["comm_pim"]) = (0, 0)

    def test_component_time(self, test):
        if (test["test_component_time"] == "False"):
            return
        if (test["time_cpu"], test["time_comm"], test["time_pim"]) != (nan, nan, nan):
            return
        run_test_cmd = "numactl --interleave=all "
        result_file = os.path.join(result_folder, str(tidx) + "component_time.txt")
        command_executor("/bin/bash -c " + run_test_cmd + "> " + result_file)
        (test["time_cpu"], test["time_comm"], test["time_pim"]) = (0, 0, 0)

    def test_throughput(self, test):
        if (test["test_throughput"] == "False"):
            return
        if test["throughput"] != nan:
            return
        run_test_cmd = "numactl --interleave=all "
        result_file = os.path.join(result_folder, str(tidx) + "throughput.txt")
        command_executor("/bin/bash -c " + run_test_cmd + "> " + result_file)
        test["throughput"] = 0

    def test_energy(self, test):
        raise NotImplementedError("Automatic Energy Test Not Implemented Yet!")

def run_test(tidx, test):
    tr = Test_Runner()
    attrs = (getattr(tr, name) for name in dir(tr))
    methods = filter(inspect.ismethod, attrs)
    all_tests = []
    for method in methods:
        try:
            if (test_traditional(test)):
                raise NotImplementedError("Automatic Traditional Indexes Evaluation Not Implemented Yet!")
            method(tidx, test)
        except NotImplementedError as error:
            pass
    return


# load test cases
all_tests = []
columns = []
with open('experiments.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    columns = reader.fieldnames
    for row in reader:
        all_tests.append(row)


# init output folder
now = datetime.datetime.now()
nowStr = now.strftime("%b_%d_%Y_%H:%M:%S")
dirName = "test_results_" + nowStr
if os.path.exists(dirName):
    raise IOError("Test Dir Already Exist. Do not run this script multiple times in one second.")
os.mkdir(dirName)
result_folder = os.path.abspath(dirName)

# run tests
for tidx, test in enumerate(tqdm(all_tests)):
    # sleep(0.1)
    # pass
    run_test(tidx, test)

# print results
with open('results.csv', 'w', newline='') as csvfile:
    fieldnames = columns
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(all_tests)

# print(json_print(all_tests))
