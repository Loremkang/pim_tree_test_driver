import inspect
import os
import csv
from time import sleep
from tqdm import tqdm

from common import *

class Test_Runner(object):
    def test_communication(self, test):
        if (test["test_communication"] == False):
            return
        (test["comm_dram"], test["comm_cpu"]) = (0, 0)

    def test_component_time(self, test):
        if (test["test_component_time"] == False):
            return
        (test["time_cpu"], test["time_comm"], test["time_pim"]) = (0, 0, 0)

    def test_throughput(self, test):
        if (test["test_throughput"] == False):
            return
        test["throughput"] = 0
    
    def test_energy(self, test):
        print("Automatic Energy Test Not Implemented Yet!")
        pass


def run_test(test):
    tr = Test_Runner()
    attrs = (getattr(tr, name) for name in dir(tr))
    methods = filter(inspect.ismethod, attrs)
    all_tests = []
    for method in methods:
        method(test)
    return

all_tests = []

with open('experiments.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        all_tests.append(row)

for test in tqdm(all_tests):
    # sleep(0.1)
    # pass
    run_test(test)

# print(json_print(all_tests))