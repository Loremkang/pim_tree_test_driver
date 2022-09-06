import os
import json
from time import sleep
from common import json_print
from tqdm import tqdm

x = [i for i in range(70)]

for i in tqdm(x):
    sleep(0.1)
    print(i)