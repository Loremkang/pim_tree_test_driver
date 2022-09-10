# from cmath import nan
import inspect
from math import nan
import os
import csv
import re
import sys
from time import sleep
from tqdm import tqdm
import datetime

from common import *

result_folder = ""
cur_folder = os.path.dirname(os.path.abspath(__file__))
numeric_const_pattern = '[-+]? (?: (?: \d* \. \d+ ) | (?: \d+ \.? ) )(?: [Ee] [+-]? \d+ ) ?'
rx = re.compile(numeric_const_pattern, re.VERBOSE)

all_tests = []
columns = []

def test_traditional(test):
    if (test["idx_type"] in ("ab-tree", "bst")):
        return True
    return False

def working_dir_switch(path):
    os.chdir(path)

def command_executor(cmd):
    print(cmd)
    os.system(cmd)

def save_results(name):
    working_dir_switch(result_folder)
    # print results
    with open(f'results_{name}.csv', 'w+', newline='') as csvfile:
        fieldnames = columns
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_tests)

def core_command_gen(test, pipeline):
    idx_type = test["idx_type"]
    batch_size = test["batch_size"]
    op_type = test["op_type"]
    skew = test["skew"]

    if idx_type != "pim_tree" and batch_size != "1000000":
        raise Exception("Invalid batch size")

    # input file
    init_file = ""
    test_file = ""
    if "ycsb" in op_type:
        # raise NotImplementedError("Automatic YCSB Test Not Implemented Yet!")
        if "partition" in test["idx_type"]:
            init_file = microbenchmark_init_file
        else:
            init_file = microbenchmark_init_file_sorted
        test_file = os.path.join(ycsb_folder, f'test_100000000_{skew}_{op_type}.binary')
    elif "micro" in op_type:
        if "partition" in test["idx_type"]:
            init_file = microbenchmark_init_file
        else:
            init_file = microbenchmark_init_file_sorted
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
            raise Exception(f'invalid micro op type: {op_type}')
        test_file = os.path.join(microbenchmark_folder, f'test_100000000_{skew}_{typeid}.binary')
    elif "wiki" in op_type:
        if "predecessor" in op_type:
            test_file = wiki_predecessor_file
        elif "insert" in op_type:
            test_file = wiki_insert_file
        else:
            raise Exception(f'invalid wiki op type: {op_type}')
    

    if idx_type == "pim_tree":
        working_dir_switch(pim_tree_source_folder)
        if pipeline:
            return f'./build/pim_tree_host -c -t -d --top_level_threads 2 -f {init_file} {test_file} --test_batch_size {batch_size}'
        else:
            return f'./build/pim_tree_host -c -t -d --top_level_threads 1 -f {init_file} {test_file} --test_batch_size {batch_size}'
    elif idx_type == "range_partitioning":
        working_dir_switch(range_partitioning_folder)
        return f'./build/fast_skip_list_host -c -t -d -f {init_file} {test_file}'
    elif idx_type == "jump_push":
        working_dir_switch(before_chunking_folder)
        return f'./build/jump_push_skip_list_host -c -t -d --init_state -f {init_file} {test_file}'
    elif idx_type == "push_pull":
        working_dir_switch(before_chunking_folder)
        return f'./build/push_pull_skip_list_host -c -t -d --init_state -f {init_file} {test_file}'
    elif idx_type == "push_pull_chunk":
        working_dir_switch(pim_tree_source_folder)
        return f'./build/pim_tree_host_no_shadow_subtree -c -t -d -f {init_file} {test_file}'
    elif idx_type == "push_pull_chunk_shadow":
        working_dir_switch(pim_tree_source_folder)
        return f'./build/pim_tree_host -c -t -d --top_level_threads 1 -f {init_file} {test_file} --test_batch_size {batch_size}'
    else:
        raise Exception(f'invalid idx type: {idx_type}')

class EvaluationFailErorr(Exception):
    pass

def output_analysis(test, type, file):
    if not os.path.exists(file):
        raise EvaluationFailErorr("result file not found")

    f = open(file, "r")
    str = f.read().split('\n')
    f.close()

    if type == "throughput":
        if (test["idx_type"] == "pim_tree"): # with pipelining!
            for idx, s in enumerate(str):
                if "Pipeline Average Time:" in s:
                    print(s)
                    total_time = float(str[idx + 1])
                    return float(test["evaluation_set_size"]) / total_time
            raise EvaluationFailErorr('throughput t1 not found')
        else:
            for idx, s in enumerate(str):
                if "Timer -> global_exec:" in s:
                    print(s)
                    total_time_str = s[idx + 2]
                    vals = rx.findall(total_time_str)
                    if len(vals) != 1:
                        raise RuntimeError("Invalid throughput str")
                    total_time = float(vals[0])
                    return float(test["evaluation_set_size"]) / total_time
            raise EvaluationFailErorr('throughput t2 not found')

    elif type == "communication":
        comm_dram = comm_pim = None
        for idx, s in enumerate(str):
            if "PAPI_L3_TCM" in s:
                print(s)
                if comm_dram != None:
                    raise EvaluationFailErorr("Replicated communication DRAM")
                vals = rx.findall(s)
                if len(vals) != 2 or vals[0] != "3":
                    raise EvaluationFailErorr("Invalid communication str DRAM")
                comm_dram = float(vals[1]) * 64 / float(test["evaluation_set_size"])
            if "total actual communication" in s:
                print(s)
                if comm_pim != None:
                    raise EvaluationFailErorr("Replicated communication PIM")
                vals = rx.findall(s)
                if len(vals) != 1:
                    raise EvaluationFailErorr("Invalid communication str PIM")
                comm_pim = float(vals[0]) / float(test["evaluation_set_size"])
        if comm_dram == None or comm_pim == None:
            raise EvaluationFailErorr("comm not found")
        return comm_dram, comm_pim
    elif type == "component_time":
        time_cpu = time_pim = time_comm = 0.0
        for idx, s in enumerate(str):
            if " -> exec -> dpu:" in s:
                print(s)
                total_time_str = s[idx + 2]                
                vals = rx.findall(total_time_str)
                if len(vals) != 1:
                    raise EvaluationFailErorr("Invalid component time dpu")
                total_time = float(vals[0])
                time_pim += total_time
            if " -> exec:" in s:
                print(s)
                total_time_str = s[idx + 2]                
                vals = rx.findall(total_time_str)
                if len(vals) != 1:
                    raise EvaluationFailErorr("Invalid component time dpu")
                total_time = float(vals[0])
                time_comm += total_time
            if "Timer -> global_exec:" in s:
                print(s)
                total_time_str = s[idx + 2]
                vals = rx.findall(total_time_str)
                if len(vals) != 1:
                    raise EvaluationFailErorr("Invalid throughput str")
                total_time = float(vals[0])
                time_cpu = total_time
        if time_cpu == 0.0 or time_pim == 0.0 or time_comm == 0.0:
            raise EvaluationFailErorr("cpu/pim/comm not found")
        if time_comm <= time_pim:
            raise EvaluationFailErorr("Invalid component time comm < 0") 
        if time_cpu <= time_comm:
            raise EvaluationFailErorr("Invalid component time comm+pim < 0") 
        time_cpu -= time_comm
        time_comm -= time_pim
        return time_cpu, time_comm, time_pim

class Test_Runner(object):
    def test_communication(self, tidx, test):
        if (test["test_communication"] == "False"):
            return
        if (test["comm_dram"], test["comm_pim"]) != ("nan", "nan"):
            return
        # test["pipeline"] = "False"
        # change working dir here
        run_test_cmd = f'numactl --cpunodebind=0 --membind=0 {core_command_gen(test, pipeline=False)}'
        suffix = str(tidx) + "communication"
        result_file = os.path.join(result_folder, f'{suffix}.txt')
        command_executor(f'{run_test_cmd} > {result_file}')
        try:
            (test["comm_dram"], test["comm_pim"]) = output_analysis(test, "communication", result_file)
        except EvaluationFailErorr as error:
            print(error)
            (test["comm_dram"], test["comm_pim"]) = ("nan", "nan")
        save_results(suffix)

    def test_component_time(self, tidx, test):
        if (test["test_component_time"] == "False"):
            return
        if (test["time_cpu"], test["time_comm"], test["time_pim"]) != ("nan", "nan", "nan"):
            return
        run_test_cmd = f'numactl --interleave=all {core_command_gen(test, pipeline=False)}'
        suffix = str(tidx) + "component_time"
        result_file = os.path.join(result_folder, f'{suffix}.txt')
        command_executor(f'{run_test_cmd} > {result_file}')
        try:
            (test["time_cpu"], test["time_comm"], test["time_pim"]) = output_analysis(test, "component_time", result_file)
        except EvaluationFailErorr as error:
            print(error)
            (test["time_cpu"], test["time_comm"], test["time_pim"]) = ("nan", "nan", "nan")
        save_results(suffix)

    def test_throughput(self, tidx, test):
        if (test["test_throughput"] == "False"):
            return
        if test["throughput"] != "nan":
            return
        run_test_cmd = f'numactl --interleave=all {core_command_gen(test, pipeline=True)}'
        suffix = str(tidx) + "throughput"
        result_file = os.path.join(result_folder, f'{suffix}.txt')
        command_executor(f'{run_test_cmd} > {result_file}')
        try:
            test["throughput"] = output_analysis(test, "throughput", result_file)
        except EvaluationFailErorr as error:
            print(error)
            test["throughput"] = "fail"
        save_results(suffix)

    def test_energy(self, tidx, test):
        if (test["test_energy"] == "False"):
            return
        if test["energy_cpu"] != "nan":
            return
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
            print(error)
            pass
    return


assert(len(sys.argv[1:]) > 0)

# load test cases
with open(sys.argv[1], newline='') as csvfile:
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

working_dir_switch(cur_folder)
# print results
with open(f'results.csv', 'w+', newline='') as csvfile:
    fieldnames = columns
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(all_tests)