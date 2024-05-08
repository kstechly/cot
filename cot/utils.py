import json
import os
import time


### json utils

def write_json(domain_name,text_to_write,data_type):
    directory = f"data/{data_type}/{domain_name}"
    os.makedirs(directory, exist_ok=True)
    location = f"{directory}/{data_type}.json"
    with open(f'{location}.tmp',"w") as fp:
        json.dump(text_to_write, fp, indent = 4)
    os.replace(f'{location}.tmp', location)

def read_json(domain_name, overwrite_previous, data_type, verbose=False):
    location = f"data/{data_type}/{domain_name}/{data_type}.json"
    if os.path.exists(location):
        with open(location, 'r') as file:
            previous = json.load(file)
        if overwrite_previous:
            stamp = str(time.time())
            with open(f"data/{data_type}/{domain_name}/{data_type}-{stamp}.json.old","w") as file:
                json.dump(previous, file, indent=4)
        return previous
    else:
        if verbose: print(f"{location} does not exist. Initializing with empty dictionary.")
        return {}

### other utils

def includes_dict_w_ignore(l, b, ignore_keys):
    for a in l:
        ka = set(a).difference(ignore_keys)
        kb = set(b).difference(ignore_keys)
        if ka == kb and all(a[k] == b[k] for k in ka): return True
    return False

def includes_dict(l, b):
    for a in l:
        if all(a[k] == b[k] for k in b.keys()): return True
    return False