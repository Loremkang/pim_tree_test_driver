import json

def list_sum(a, b):
    c = [0] * len(a)
    for i in range(len(a)):
        c[i] = a[i] + b[i]
    return c

def json_print(a):
    print(json.dumps(a, sort_keys=True, indent=2))
    return