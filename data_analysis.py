import json

BASE_DIR = "path to the directory containing al DB and video folders" 

def main():
    sirt_time, cgls_time, bp_time, sums = sum_all_execution_times()
    print(f"Total execution times:")
    print(f"SIRT3D_CUDA: {seconds_to_hours(sirt_time):.2f} hours ({sirt_time:.2f} seconds)") if sirt_time>0 else print('Error in sirt')
    print(f"CGLS3D_CUDA: {seconds_to_hours(cgls_time):.2f} hours ({cgls_time:.2f} seconds)") if cgls_time>0 else print('Error in cgls')
    print(f"BP3D_CUDA: {seconds_to_hours(bp_time):.2f} hours ({bp_time:.2f} seconds)") if bp_time>0 else print('Error in bp')
    print(f"Total time: {seconds_to_hours(sums):.2f} hours") if sirt_time>0 else print('Error in sums')

    value = "execution_time_seconds" # Example value
    title_value = value.replace('_', ' ').title()
    sirt_min, sirt_config, cgls_min, cgls_config, bp_min, bp_config =analyze_all_minimums(value)
    print(f"\nMinimum {title_value}:") 
    print(f"SIRT3D_CUDA: {sirt_min:.6f} ({sirt_config})") if sirt_min!=float('inf') else None
    print(f"CGLS3D_CUDA: {cgls_min:.6f} ({cgls_config})") if cgls_min!=float('inf') else None
    print(f"BP3D_CUDA: {bp_min:.6f} ({bp_config})") if bp_min!=float('inf') else None

    # Find overall minimum
    min_value = min(sirt_min, cgls_min, bp_min) if min(sirt_min, cgls_min, bp_min)!=float('inf') else None
    if min_value == sirt_min:
        print(f"Best algorithm: SIRT3D_CUDA for {title_value}")
    elif min_value == cgls_min:
        print(f"Best algorithm: CGLS3D_CUDA for {title_value}")
    elif min_value == cgls_min:
        print(f"Best algorithm: BP3D_CUDA for {title_value}")
    else:
        print(f"Error, no minimum {title_value}")
       
def seconds_to_hours(seconds):
        return seconds / 3600

def sum_execution_times(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)
        
    total_time = 0
    
    def recursive_sum(d):
        time_sum = 0
        for k, v in d.items():
            if isinstance(v, dict):
                time_sum += recursive_sum(v)
            elif k == 'execution_time_seconds':
                time_sum += v
        return time_sum
    
    total_time = recursive_sum(data)
    return total_time

def sum_all_execution_times(path_to_json_sirt=None, path_to_json_cgls=None, path_to_json_bp=None):
    # Load and sum times from each algorithm's results
    sirt_file = path_to_json_sirt
    cgls_file = path_to_json_cgls
    bp_file = path_to_json_bp

    try:
        sirt_time = sum_execution_times(sirt_file)
    except:
        sirt_time = 0
    try:
        cgls_time = sum_execution_times(cgls_file)
    except:
        cgls_time = 0
    try:
        bp_time = sum_execution_times(bp_file)
    except:
        bp_time = 0


    return [sirt_time, cgls_time, bp_time, sirt_time + cgls_time + bp_time]
    

def get_minimum_value(json_file, value):
    with open(json_file, 'r') as f:
        data = json.load(f)
        
    def recursive_find_min(d):
        min_value = float('inf')  # Initialize with infinity
        min_config = None
        
        for k, v in d.items():
            if isinstance(v, dict):
                sub_min_value, sub_min_config = recursive_find_min(v)
                if sub_min_value < min_value:
                    min_value = sub_min_value
                    min_config = sub_min_config
            elif k == value:
                # Store the parent configuration if this is the minimum so far
                if v < min_value:
                    min_value = v
                    min_config = d['info']  # Store the entire configuration dictionary
                    
        return min_value, min_config
    
    min_value, min_config = recursive_find_min(data)
    return min_value, min_config

    
   
# Example usage
def analyze_all_minimums(value, path_to_json_sirt=None, path_to_json_cgls=None, path_to_json_bp=None):
    sirt_file = path_to_json_sirt
    cgls_file = path_to_json_cgls
    bp_file = path_to_json_bp

    # Get minimum for each algorithm
    try:
        sirt_min, sirt_config = get_minimum_value(sirt_file, value)
    except:
        sirt_min = float('inf')
        sirt_config = None
    try:
        cgls_min, cgls_config = get_minimum_value(cgls_file, value)
    except:
        cgls_min = float('inf')
        cgls_config = None
    try:
        bp_min, bp_config = get_minimum_value(bp_file, value)
    except:
        bp_min = float('inf')
        bp_config = None

    return sirt_min, sirt_config, cgls_min, cgls_config, bp_min, bp_config
    

def get_all_values(json_file, key_to_find):
    """
    Get all values for a specific key from a JSON file
    
    Args:
        json_file (str): Path to the JSON file
        key_to_find (str): Key to search for (e.g., 'euclidean_distance', 'execution_time_seconds')
    
    Returns:
        list: All values found for that key
    """
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    values = []
    
    def find_values(d):
        if isinstance(d, dict):
            for k, v in d.items():
                if k == key_to_find:
                    values.append(v)
                elif isinstance(v, (dict, list)):
                    find_values(v)
        elif isinstance(d, list):
            for item in d:
                find_values(item)
    
    find_values(data)
    return values

def get_all_values_and_iterations(json_file, key_to_find):
    """
    Get all values grouped by iterations (10, 100, 1000, 2000) from the JSON file
    """
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    values_10 = []
    values_100 = []
    values_1000 = []
    values_2000 = []
    
    def extract_values(d):
        if isinstance(d, dict):
            # If we find a leaf node with our key and info
            if 'info' in d.keys():
                value = d[key_to_find]
                if 'iter1000' in d['info']:
                    values_1000.append(value)
                elif 'iter100' in d['info']:
                    values_100.append(value)
                elif  'iter10' in d['info']:
                    values_10.append(value)
                elif 'iter2000' in d['info']:
                    values_2000.append(value)
               
            # Continue searching through all dictionary values
            for v in d.values():
                if isinstance(v, dict):
                    extract_values(v)
    
    extract_values(data)
    return values_10, values_100, values_1000, values_2000

def get_ordered_values(json_file, key_to_find):
    """
    Get all values for a specific key from a JSON file and return them ordered
    
    Args:
        json_file (str): Path to the JSON file
        key_to_find (str): Key to search for (e.g., 'euclidean_distance', 'execution_time_seconds')
    
    Returns:
        tuple: (list of values ordered, list of corresponding info strings)
    """
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    values = []
    infos = []
    
    def find_values(d):
        if isinstance(d, dict):
            if key_to_find in d and 'info' in d:
                values.append(d[key_to_find])
                infos.append(d['info'])
            for v in d.values():
                if isinstance(v, dict):
                    find_values(v)
    
    find_values(data)
    
    # Sort both lists based on values while keeping the correspondence
    pairs = sorted(zip(values, infos))
    sorted_values, sorted_infos = zip(*pairs) if pairs else ([], [])
    
    return list(sorted_values), list(sorted_infos)


if __name__ == "__main__":
    main()