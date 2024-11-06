import math
import zipfile
from audioop import reverse
from unittest import result

import json5
import multiprocessing as mp

LOG_VERBOSE = False         # Extra logging
TESTING = False             # Only parse 3 files for testing purposes
READ_IN_COMMANDS = True    # Allow execution of python via terminal

BEAMNG_INSTALLATION_PATH = "C:/Program Files (x86)/Steam/steamapps/common/BeamNG.drive/" # installation path, might have to change this

# BEAMNG_INSTALLATION_PATH + COMMON_ZIP_PATH + TIRES_FOLDER should be the path to tire information
COMMON_ZIP_PATH = BEAMNG_INSTALLATION_PATH + "content/vehicles/common.zip/"
TIRES_FOLDER = 'vehicles/common/tires/'

# thread function for parsing json files
def parse_files(files, queue):
    parsed_files = []
    for f in files:
        with zipfile.ZipFile(COMMON_ZIP_PATH, 'r') as zip_ref:
            with zip_ref.open(f) as file:
                content = file.read().decode('utf-8')
                if LOG_VERBOSE: print(f"Parsing {f}")
                try:
                    tire = json5.loads(content)
                    parsed_files.append(tire)
                except:
                    print(f"\033[31mFailed parsing file {f}\033[0m")
    queue.put(parsed_files)
    return

def main():
    # collect files
    all_files = []
    with zipfile.ZipFile(COMMON_ZIP_PATH, 'r') as zip_ref:
        all_files = [f for f in zip_ref.namelist() if f.startswith(TIRES_FOLDER) and f.endswith('.jbeam')]
        print(f"Found {all_files.__len__()} jbeam tire files.\n")


    files = all_files[:3] if TESTING else all_files

    combined_tire_data = []

    # parse files
    print("Parsing... This may take some time...")

    # set up multiprocessing
    num_threads = mp.cpu_count()
    processes = []
    chunk_size = math.ceil(files.__len__() / num_threads)
    result_queue = mp.Queue()

    if LOG_VERBOSE: print(f"Starting multiprocessing with {num_threads} threads.\n")

    # start threads
    for i in range(num_threads):
        start_idx = i * chunk_size
        end_idx = min(start_idx + chunk_size, files.__len__())
        sub_files_list = files[start_idx:end_idx]
        process = mp.Process(target=parse_files, args=(sub_files_list, result_queue))
        processes.append(process)
        process.start()
        if LOG_VERBOSE: print(f"Starting thread {i+1}.")

    # pulling results from queue, joining threads not needed
    for i in range(num_threads):
        tire_data = result_queue.get()
        combined_tire_data = combined_tire_data + tire_data


    print(f"\nSuccessfully parsed {combined_tire_data.__len__()} tire data files.\n")


    # splitting up tire data since one file can contain serveral tires
    tire_data = dict()
    for t in combined_tire_data:
        for key in t.keys():
            tire_data[key] = t[key]

    print(f"Found {len(tire_data)} tires in total.\n")

    tire_names = list(tire_data.keys())

    # define functions to make sense of tire data

    # retrieves a value in the "pressureWheels" section of the json document which contains most tire parameters
    # returns None if not found
    def find_value(tire, prop):
        props = tire["pressureWheels"]
        for _prop in props:
            if isinstance(_prop, dict):
                if prop in list(_prop.keys()):
                    return _prop[prop]
        return None

    # get list of keys of selected tire group(s)
    # possible groups: all, standard, drift, sport, sport_plus, race, drag
    def tire_groups(allowed_groups):
        allowed_names = []
        if "all" in allowed_groups:
            return tire_names
        for n in tire_names:
            for group in allowed_groups:
                if group in n:
                    allowed_names.append(n)
        return allowed_names

    # get dict of tire selected group(s)
    # possible tire groups: all, standard, rally, offroad, biasply, eco, drift, sport, sport_plus, race, drag
    def tire_groups_dict(allowed_groups):
        _dict = {}
        keys = tire_groups(allowed_groups)
        for key in keys:
            _dict[key] = tire_data[key]
        return _dict

    # helper function
    def extreme_value(prop, _max, groups):
        selected_tire_names = tire_groups(groups)
        extr_val = float('-inf' if _max else 'inf')
        extr_val_name = ""
        for tire_name in selected_tire_names:
            tire = tire_data[tire_name]
            val = find_value(tire, prop)
            if val is None: continue
            if not isinstance(val, float) and not isinstance(val, int):
                print(f"\033[31mValue is not a number.\033[0m")
                break
            if (_max and val > extr_val) or (not _max and val < extr_val):
                extr_val = val
                extr_val_name = tire_name
        return extr_val_name, extr_val

    # get the highest value of a certain property
    # returns (tire_name, value)
    def highest_value(prop, groups=None):
        if groups is None:
            groups = ["all"]
        return extreme_value(prop, True, groups)

    # get the lowest value of a certain property
    # returns (tire_name, value)
    def lowest_value(prop, groups=None):
        if groups is None:
            groups = ["all"]
        return extreme_value(prop, False, groups)

    # sorts tires by property.  set property to "pi" to sort by estimated perf index
    # returns the first #num keys
    def sort(prop, num=10, descending=True, groups=None):
        if groups is None:
            groups = ["all"]
        selected_tire_data = tire_groups_dict(groups)
        if prop == "pi":
            keys_sorted_by_values = sorted(selected_tire_data, key=lambda x: get_estimated_grip_index(selected_tire_data[x]), reverse=descending)
        else:
            keys_sorted_by_values = sorted(selected_tire_data, key=lambda x: find_value(selected_tire_data[x], prop), reverse=descending)
        return keys_sorted_by_values[:num]

    # sorts tires by property and displays the first #num results
    def sort_summary(prop, num=10, descending=True, groups=None):
        if groups is None:
            groups = ["all"]
        keys = sort(prop, num=num, descending=descending, groups=groups)
        summary = f"Tires sorted by {prop}:\n"
        for i in range(keys.__len__()):
            summary = summary + f"{i+1}. {keys[i]} {get_estimated_grip_index(tire_data[keys[i]]) if prop == "pi" else find_value(tire_data[keys[i]], prop)}\n"
        summary = summary + "\n"
        return summary

    # get tire key based off ingame name, apparently this doesn't work for all tires (not in these files?)
    # returns None if not found
    def get_tire_key(ingame_name):
        for n in tire_names:
            tire = tire_data[n]
            if ingame_name in tire["information"]["name"]:
                return n
        return None

    # function to estimate how much grip a tire produces
    # returns integer (0 if a value is not found)
    def get_estimated_grip_index(tire):
        width = find_value(tire, 'tireWidth') or 0
        fcoeff = find_value(tire, 'frictionCoef') or 0
        noloadcoeff = find_value(tire, 'noLoadCoef') or 0
        return math.floor(100 * width * fcoeff * noloadcoeff)

    # prints summary of tire given key with most important data
    def get_summary(tire_key):
        tire = tire_data[tire_key]
        # this method is inefficient since it uses find_value a lot, no issue if just called once though
        width = find_value(tire, 'tireWidth') or 0
        radius = find_value(tire, 'radius') or 0
        return f"""
Tire Summary: {tire_key} ({tire["information"]["name"]})

Width: {width * 1000} mm
Radius: {radius * 1000} mm

Material: {find_value(tire, 'nodeMaterial')}

Friction Coefficient: {find_value(tire, 'frictionCoef')}
No Load Coefficient: {find_value(tire, 'noLoadCoef')}
Load Sensitivity Slope: {find_value(tire, 'loadSensitivitySlope')}

Estimated Grip Index: {get_estimated_grip_index(tire)}
"""

    # print summary from ingame name
    def summary(ingame_name):
        tire = get_tire_key(ingame_name)
        if tire is None:
            print("Tire not found.")
            return
        return get_summary(tire)


    ###############################################
    # Testing Area:
    ###############################################

    # possible tire groups: all, standard, rally, offroad, biasply, eco, drift, sport, sport_plus, race, drag

    # first_tire = tire_data[next(iter(tire_names))]

    # print(lowest_value("tireWidth", groups=["sport", "race"]))

    ###############################################

    while READ_IN_COMMANDS:
        command = input("Enter command: (exit to end)\n")
        if command == "exit": break;

        try:
            exec(f"print({command})")
        except Exception as e:
            print(f"\033[31mExecution failed: {e}\033[0m")



if __name__ == '__main__':
    main()