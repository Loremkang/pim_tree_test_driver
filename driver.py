
from cmath import nan
import csv
import datetime
import os
import json
import sys
from time import sleep
from common import json_print
# from tqdm import tqdm
import numpy as np
import re

numeric_const_pattern = '[-+]? (?: (?: \d* \. \d+ ) | (?: \d+ \.? ) )(?: [Ee] [+-]? \d+ ) ?'
rx = re.compile(numeric_const_pattern, re.VERBOSE)

# a = os.system('/bin/bash -c "python3 test.py"')
# print(a)

# a = np.arange(0, 1.2, 0.2)
# a = [f'{i:.1f}' for i in a]
# print(a)

# def a(x):
#     if x:
#         return (1, "1")
#     else:
#         return ("1", 1, 2.3)
def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False

all_tests = []
with open(sys.argv[1], newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    columns = reader.fieldnames
    for row in reader:
        all_tests.append(row)

for test in all_tests:
    if isfloat(test["comm_dram"]):
        comm_dram = float(test["comm_dram"])
        comm_dram *= 64.0
        test["comm_dram"] = comm_dram

with open(f'results_16communication.csv', 'w+', newline='') as csvfile:
    fieldnames = columns
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(all_tests)


# print(f'{a(True)}  {a(False)}')
# exit()

# with open('test.csv', newline='') as csvfile:
#     reader = csv.DictReader(csvfile)
#     columns = reader.fieldnames
#     for row in reader:
#         all_tests.append(row)

# print(columns)
# print(all_tests)