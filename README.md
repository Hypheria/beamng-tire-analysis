# Tire Analyser

## Setup
- Make sure path to tire data is correct, the path is split up at common.zip

## How it works
- Add commands in *Testing Area* towards the bottom of main.py
- Or add commands if *READ_IN_COMMANDS=True* after parsing is complete in terminal

## Commands
Commands are just single line python function calls

**Some important terminonlogy / variables:**  
__tire_data__: dictionary of tire data (key : tire_object)  
__tire_key__: tire parts name (e.g. tire_R_225_75_16_standard)  
__ingame_name__: ingame name (e.g. Standard Rear Tires)  
__tire__: refers to tire object  
__prop__: properties in tier objects, intersting ones are:  
tireWidth, radius, frictionCoef, noLoadCoef, slidingFrictionCoef, loadSensitivitySlope, fullLoadCoef  
__groups__: specify allowed tire groups in array (e.g. ["sport", "race"]), possible tire groups:  
all, standard, rally, offroad, biasply, eco, drift, sport, sport_plus, race, drag

**Useful Functions:**
```py
# print summary from ingame name
def summary(ingame_name : str)
# prints summary of tire given key with most important data
def get_tire_summary(tire_key : str)
# get tire key based off ingame name
def get_tire(ingame_name : str)
# sorts tires by property and displays the first #num results. set property to "pi" to sort by estimated perf index
def print_sorted_by_property(prop, num=10, descending=True, groups=None)
# get the highest value of a certain property, returns (tire_name, value)
def get_highest_value(prop, groups=None)
# get the lowest value of a certain property. returns (tire_name, value)
def get_lowest_value(prop, groups=None)
# get dict of tire selected group(s)
def tire_groups_dict(allowed_groups)
# retrieves a value in the "pressureWheels" section of the json document which contains most tire parameters
def find_value(tire, prop)
```