
# Config to Blender Script

A Python script for Blender 4.5+ that automatically converts JSON configuration files into parametric geometry node groups. This tool streamlines the creation of procedural 3D objects by parsing configuration data and generating corresponding Blender node setups with interactive parameters.

## Features

- **Automatic Parameter Generation**: Creates float, integer, and menu input sockets based on JSON config ranges and options
- **Menu Switch Integration**: Generates geometry menu switch nodes for categorical parameters with proper string-to-geometry mapping
- **Material System**: Automatically creates and assigns materials for each object part defined in the config
- **Smart Detection**: Auto-detects config files in the current .blend file directory or accepts manual file paths
- **Geometry Nodes Integration**: Seamlessly applies generated node groups to selected objects as geometry node modifiers

## Requirements

- Blender 4.5 or higher
- Python 3.x (included with Blender)

## Installation

1. Download the `config_to_blender.py` script
2. Place it in your Blender scripts directory or project folder
3. Ensure your JSON config files are properly formatted

## Usage

### Basic Usage

1. **Prepare your .blend file**: Save your Blender file in the same directory as your config file
2. **Select an object**: Choose the object you want to apply the parametric system to
3. **Run the script**: Execute the script in Blender's Text Editor or via command line

### Configuration Methods

#### Method 1: Auto-detection
Place your config file (ending with `_Config.json` or `_config.json`) in the same directory as your .blend file. The script will automatically find and load it.

#### Method 2: Manual path
Set the `CONFIG_PATH` variable at the top of the script:
```python
CONFIG_PATH = r"C:\Path\To\Your\Config.json"


#### Method 3: Command line

Run Blender with the script and config path as arguments:

`blender your_file.blend --python config_to_blender.py -- "path/to/config.json"`

JSON Configuration Format
-------------------------

### Basic Structure

`{     "category": "ObjectType",     "config": {         "ParameterName": {             "range": [min_value, max_value]         },         "MenuParameter": [             "option1",             "option2",             "option3"         ]     },     "parts": {         "PartName1": {},         "PartName2": {},         "PartName3": {}     },     "joints": {         "joint_name": {             "parent": "PartName1",             "child": "PartName2",             "type": "revolute",             "axis": [0, 0, 1],             "limit": [0, 120]         }     } }`

### Parameter Types

#### Numeric Parameters

`"Width": {     "range": [0.6, 0.8] }, "Height": {     "range": [0.85, 1.1] }`

*   Creates float or integer input sockets
*   Automatically detects data type based on values
*   Sets min/max constraints and default values

#### Menu Parameters

`"LoadingType": [     "front_loading",     "top_loading" ], "ControlType": [     "knob",     "digital",     "buttons" ]`

*   Creates menu switch nodes for string-based options
*   Generates geometry-type menu switches
*   Automatically connects input sockets to menu nodes

#### Boolean Parameters

`"HasLid": [     true,     false ]`

*   Creates integer sockets for boolean choices
*   Maps to 0/1 values for first/second option

### Parts and Materials

`"parts": {     "Body": {},     "Door": {},     "Handle": {},     "ControlPanel": {} }`

*   Automatically creates materials for each part
*   Materials are assigned to the active object
*   Can be manually applied to specific faces in Edit mode

Example Configuration
---------------------

Here's a complete example for a washing machine:

`{     "category": "Washer",     "config": {         "Width": {             "range": [0.6, 0.8]         },         "Height": {             "range": [0.85, 1.1]         },         "Capacity": {             "range": [3.5, 6.0]         },         "LoadingType": [             "front_loading",             "top_loading"         ],         "DoorSwing": [             "left_hinge",             "right_hinge"         ],         "HasLid": [             true,             false         ]     },     "parts": {         "Body": {},         "Door": {},         "Drum": {},         "Handle": {},         "ControlPanel": {}     },     "joints": {         "door_hinge": {             "parent": "Body",             "child": "Door",             "type": "revolute",             "axis": [0, 0, 1],             "limit": [0, 120]         }     } }`

Output
------

The script generates:

1.  **Geometry Node Group**: Named after your object with all parameters as input sockets
2.  **Menu Switch Nodes**: For categorical parameters with geometry outputs
3.  **Materials**: One material per part defined in the config
4.  **Geometry Nodes Modifier**: Applied to the selected object

Debugging
---------

Enable debug output by setting `DEBUG = True` in the script. This provides detailed logging of:

*   File loading progress
*   Parameter processing
*   Node creation steps
*   Material assignment
*   Error messages with stack traces

Troubleshooting
---------------

### Common Issues

**"No config files found"**

*   Ensure your config file ends with `_Config.json` or `_config.json`
*   Save your .blend file before running the script
*   Check that the config file is in the same directory as your .blend file

**"No active object selected"**

*   Select an object in the 3D viewport before running the script
*   The script will still create the node group but won't apply it automatically

**"Invalid JSON"**

*   Validate your JSON syntax using a JSON validator
*   Check for missing commas, brackets, or quotes
*   Ensure boolean values use lowercase (`true`/`false`)

**"sequence item 0: expected str instance, bool found"**

*   This error was fixed in recent versions
*   Update to the latest version of the script

File Structure
--------------

`your_project/ ├── your_file.blend ├── config_to_blender.py ├── YourObject_Config.json └── README.md`

Contributing
------------

This script is designed to work with articulated object systems and procedural generation pipelines. Feel free to extend it for your specific use cases.

License
-------

Open source - feel free to modify and distribute.
