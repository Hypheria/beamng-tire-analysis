# Tire Analyser

## Setup
- Make sure the path to the Beamng installation is correct, adjust BEAMNG_INSTALLATION_PATH if not

## How it works
- Add commands in *Testing Area* towards the bottom of main.py
- Or add commands if *READ_IN_COMMANDS=True* after parsing is complete in terminal

## Commands
Commands are just single line python function calls, the return of the function call is printed

**Some important terminonlogy / variables:**  
  
__tire_data__: dictionary of tire data (key : tire_object)  
  
__tire_key__: tire parts name (e.g. tire_R_225_75_16_standard)  
  
__ingame_name__: ingame name (e.g. Standard Rear Tires)  
  
__tire__: refers to tire object  
  
__prop__: properties in tire objects, intersting ones are:  
tireWidth, radius, frictionCoef, noLoadCoef, slidingFrictionCoef, loadSensitivitySlope, fullLoadCoef, stribeckExponent, stribeckVelMult 
  
__groups__: specify allowed tire groups in array (e.g. ["sport", "race"]); if _excluding_ is set, all groups but the specified ones will be included  
Some (but not all) tire groups: all, standard, rally, offroad, crawler, eco, drift, sport, sport_plus, tarmac, race, drag
  
Some information on the properties: https://documentation.beamng.com/modding/vehicle/sections/nodes/
  
**Useful Functions:**
```py
# print summary from ingame name
def summary(ingame_name : str)
# prints summary of tire given key with most important data
def get_summary(tire_key : str)
# get tire key based off ingame name
def get_tire_key(ingame_name : str)
# sorts tires by property and displays the first #num results. set property to "pi" to sort by estimated perf index
def sort_summary(prop, num=10, descending=True, groups=None, excluding=False)
# get the highest value of a certain property, returns (tire_name, value)
def highest_value(prop, groups=None, excluding=True)
# get the lowest value of a certain property. returns (tire_name, value)
def lowest_value(prop, groups=None, excluding=True)
# get dict of tire selected group(s)
def tire_groups_dict(allowed_groups, excluding=True)
# retrieves a value in the "pressureWheels" section of the json document which contains most tire parameters
def find_value(tire, prop)

# Some example command calls:
summary("265/35R19 Sport Plus 2R Rear Tires")
sort_summary("pi", groups=["race", "sport"])
sort_summary("pi", descending=False)
lowest_value("frictionCoef")
find_value(tire_data[get_tire_key("265/35R19 Sport Plus 2R Rear Tires")], "tireWidth")
```