import math
import zipfile
import json5

LOG_VERBOSE = False         # Extra logging
TESTING = False             # Only parse 3 files for testing purposes
READ_IN_COMMANDS = True    # Allow execution of python via terminal

# COMMON_ZIP_PATH + TIRES_FOLDER should be the path to tire information (in beam installation)
COMMON_ZIP_PATH = "C:/Program Files (x86)/Steam/steamapps/common/BeamNG.drive/content/vehicles/common.zip/"
TIRES_FOLDER = 'vehicles/common/tires/'


# collect files
all_files = []
with zipfile.ZipFile(COMMON_ZIP_PATH, 'r') as zip_ref:
    all_files = [f for f in zip_ref.namelist() if f.startswith(TIRES_FOLDER) and f.endswith('.jbeam')]
    print(f"Found {all_files.__len__()} jbeam tire files.\n")


files = all_files[:3] if TESTING else all_files

combined_tire_data = []

# parse files
print("Parsing... This may take some time...")
for f in files:
   with zipfile.ZipFile(COMMON_ZIP_PATH, 'r') as zip_ref:
       with zip_ref.open(f) as file:
            content = file.read().decode('utf-8')
            if LOG_VERBOSE: print(f"Parsing {f}")
            try:
                tire = json5.loads(content)
                combined_tire_data.append(tire)
            except:
                print(f"\033[31mFailed parsing file {f}\033[0m")

print(f"\nSuccessfully parsed {combined_tire_data.__len__()} tire data files.\n")


# splitting up tire data since one file can contain serveral tires
tire_data = dict()
for t in combined_tire_data:
    for key in t.keys():
        tire_data[key] = t[key]

print(f"Found {len(tire_data)} tires in total.\n")

tire_names = list(tire_data.keys())

first_tire = tire_data[next(iter(tire_names))] # for experimental purposes

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
def get_extreme_value(prop, _max, groups):
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
def get_highest_value(prop, groups=None):
    if groups is None:
        groups = ["all"]
    return get_extreme_value(prop, True, groups)

# get the lowest value of a certain property
# returns (tire_name, value)
def get_lowest_value(prop, groups=None):
    if groups is None:
        groups = ["all"]
    return get_extreme_value(prop, False, groups)

# sorts tires by property.  set property to "pi" to sort by estimated perf index
# returns the first #num keys
def sort_by_property(prop, num=10, descending=True, groups=None):
    if groups is None:
        groups = ["all"]
    selected_tire_data = tire_groups_dict(groups)
    keys_sorted_by_values = []
    if prop == "pi":
        keys_sorted_by_values = sorted(selected_tire_data, key=lambda x: get_estimated_grip_index(selected_tire_data[x]), reverse=descending)
    else:
        keys_sorted_by_values = sorted(selected_tire_data, key=lambda x: find_value(selected_tire_data[x], prop), reverse=descending)
    return keys_sorted_by_values[:num]

# sorts tires by property and displays the first #num results
def print_sorted_by_property(prop, num=10, descending=True, groups=None):
    if groups is None:
        groups = ["all"]
    keys = sort_by_property(prop, num=num, descending=descending, groups=groups)
    print(f"Tires sorted by {prop}:")
    for i in range(keys.__len__()):
        print(f"{i+1}.", keys[i], find_value(tire_data[keys[i]], prop))
    print("\n")

# get tire key based off ingame name, apparently this doesn't work for all tires (not in these files?)
# returns None if not found
def get_tire(ingame_name):
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
def get_tire_summary(tire_key):
    tire = tire_data[tire_key]
    # this method is inefficient since it uses find_value a lot, no issue if just called once though
    width = find_value(tire, 'tireWidth') or 0
    radius = find_value(tire, 'radius') or 0
    print(f"""
Tire Summary: {tire_key} ({tire["information"]["name"]})

Width: {width * 1000} mm
Radius: {radius * 1000} mm

Material: {find_value(tire, 'nodeMaterial')}

Friction Coefficient: {find_value(tire, 'frictionCoef')}
No Load Coefficient: {find_value(tire, 'noLoadCoef')}
Load Sensitivity Slope: {find_value(tire, 'loadSensitivitySlope')}

Estimated Grip Index: {get_estimated_grip_index(tire)}
""")

# print summary from ingame name
def summary(ingame_name):
    tire = get_tire(ingame_name)
    if tire is None:
        print("Tire not found.")
        return
    get_tire_summary(get_tire(ingame_name))


###############################################
# Testing Area:
###############################################

# possible tire groups: all, standard, rally, offroad, biasply, eco, drift, sport, sport_plus, race, drag

# print_sorted_by_property("noLoadCoef")
# print(get_lowest_value("tireWidth", groups=["sport", "race"]))

###############################################

while READ_IN_COMMANDS:
    command = input("Enter command: (exit to end)\n")
    try:
        exec(command)
    except Exception as e:
        print(f"\033[31mExecution failed: {e}\033[0m")

    if command == "exit": break;