import os
from common import *

os.chdir(pim_tree_source_folder)
cmd = "./build/pim_tree_host -l 500000000 100000000 --generate_all_test_cases"
print(cmd)
os.system(cmd)