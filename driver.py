
import datetime
import os
import json
from time import sleep
from common import json_print
from tqdm import tqdm
import numpy as np

# a = os.system('/bin/bash -c "python3 test.py"')
# print(a)

a = np.arange(0, 1.2, 0.2)
a = [f'{i:.1f}' for i in a]
print(a)