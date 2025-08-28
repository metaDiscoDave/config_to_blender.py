
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

1. **Prepare your .blend file**: Copy the script to your Scripting Workspace in Blender or Open the config_to_blender.py in the Blender text Editor
2. **Select an object**: Choose the object you want to apply the parametric system to
3. **Run the script**: Execute the script in Blender's Text Editor by presseing the Play button

### Configuration Methods

#### Method 1: Auto-detection
Place your config file (ending with `_Config.json` or `_config.json`) in the same directory as your .blend file. The script will automatically find and load it.





