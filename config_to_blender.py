import bpy
import json
import os
import sys
import traceback

# Enable detailed debugging
DEBUG = True

def debug_print(message):
    """Print debug messages"""
    if DEBUG:
        print(f"DEBUG: {message}")

# ===== USER CONFIGURATION =====
# Set this to the path of your config file to use a specific file
# Example: r"C:\Path\To\Your\Config.json" or r"/path/to/your/config.json"
# Leave as None to auto-detect or use command-line arguments
CONFIG_PATH = None
# =============================

def load_config_file(filepath):
    """Load a config file and create nodes and materials"""
    debug_print(f"Attempting to load config file: {filepath}")

    # Check if file exists
    if not os.path.exists(filepath):
        print(f"ERROR: File does not exist: {filepath}")
        return None

    try:
        debug_print("Opening file...")
        with open(filepath, 'r') as f:
            try:
                debug_print("Parsing JSON...")
                config_data = json.load(f)
                debug_print(f"JSON loaded successfully. Keys: {list(config_data.keys())}")
            except json.JSONDecodeError as e:
                print(f"ERROR: Invalid JSON in config file: {e}")
                return None

        # Get the object name from the file path
        filename = os.path.basename(filepath)
        object_name = os.path.splitext(filename)[0].replace("_Config", "").replace("_config", "")
        debug_print(f"Object name: {object_name}")

        # Check if config section exists
        if "config" not in config_data:
            print("ERROR: No 'config' section found in the JSON file")
            return None

        # Create node group for parameters
        debug_print("Creating parameter node group...")
        node_group = create_parameter_node_group(config_data, object_name)

        if not node_group:
            print("ERROR: Failed to create node group")
            return None

        debug_print(f"Node group created successfully: {node_group.name}")

        # Create simple materials for parts
        if "parts" in config_data:
            debug_print(f"Creating materials for {len(config_data['parts'])} parts...")
            materials = create_simple_materials(config_data["parts"], object_name)

            # Assign materials to the active object if one exists
            if materials and bpy.context.active_object:
                assign_materials_to_object(materials, bpy.context.active_object)

            debug_print("Materials created successfully")
        else:
            debug_print("No 'parts' section found in config")

        # Print summary
        print(f"\n{object_name} Configuration Loaded:")
        print(f"- Created node group: {node_group.name}")
        print(f"- Parameters created for {len(config_data['config'])} values")
        if "parts" in config_data:
            print(f"- Materials created: {len(config_data['parts'])}")

        return node_group

    except Exception as e:
        print(f"ERROR loading config file: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return None

def create_parameter_node_group(config_data, object_name):
    """Create a node group for the parameters in the config"""
    try:
        # Create a name for the node group - just the object name as requested
        node_group_name = object_name
        debug_print(f"Creating node group: {node_group_name}")

        # Check if the node group already exists
        if node_group_name in bpy.data.node_groups:
            debug_print(f"Node group {node_group_name} already exists, removing it")
            bpy.data.node_groups.remove(bpy.data.node_groups[node_group_name])

        # Create a new node group
        debug_print("Creating new node group")
        node_group = bpy.data.node_groups.new(type="GeometryNodeTree", name=node_group_name)

        # Create group input and output nodes
        debug_print("Setting up input and output nodes")
        input_node = node_group.nodes.new("NodeGroupInput")
        input_node.location = (-200, 0)

        output_node = node_group.nodes.new("NodeGroupOutput")
        output_node.location = (400, 0)

        # Add a geometry output socket to the output node
        debug_print("Adding geometry output socket")
        # In Blender 4.5, we need to use interface sockets differently
        # First, create the interface socket
        geometry_socket = node_group.interface.new_socket(
            name="Geometry",
            in_out='OUTPUT',
            socket_type='NodeSocketGeometry'
        )

        # Process parameters from the config file
        if "config" in config_data:
            debug_print(f"Processing {len(config_data['config'])} parameters")
            y_offset = 0

            for param_name, param_data in config_data["config"].items():
                debug_print(f"Processing parameter: {param_name}, data: {param_data}")

                if isinstance(param_data, dict):
                    if "range" in param_data:
                        # This is a numeric parameter with a range
                        # Check if the values are integers or floats
                        min_val = param_data["range"][0]
                        max_val = param_data["range"][1]

                        # Check if both values are integers
                        are_integers = (isinstance(min_val, int) and isinstance(max_val, int)) or \
                                      (min_val == int(min_val) and max_val == int(max_val))

                        if are_integers:
                            # Use integer socket
                            min_val = int(min_val)
                            max_val = int(max_val)
                            default_val = min_val  # Default to minimum value for integers

                            debug_print(f"Adding int socket: {param_name}, range: [{min_val}, {max_val}], default: {default_val}")

                            socket = node_group.interface.new_socket(
                                name=param_name,
                                in_out='INPUT',
                                socket_type='NodeSocketInt'
                            )
                        else:
                            # Use float socket
                            min_val = float(min_val)
                            max_val = float(max_val)
                            default_val = (min_val + max_val) / 2  # Set default to middle of range for floats

                            debug_print(f"Adding float socket: {param_name}, range: [{min_val}, {max_val}], default: {default_val}")

                            socket = node_group.interface.new_socket(
                                name=param_name,
                                in_out='INPUT',
                                socket_type='NodeSocketFloat'
                            )

                        # Set the min, max, and default values
                        socket.min_value = min_val
                        socket.max_value = max_val
                        socket.default_value = default_val

                    elif "count" in param_data:
                        # This is a count parameter (like Button Count)
                        min_val = int(param_data["count"][0])
                        max_val = int(param_data["count"][1])
                        default_val = min_val  # Default to minimum value

                        debug_print(f"Adding int socket for count: {param_name}, range: [{min_val}, {max_val}], default: {default_val}")

                        # Create the interface socket for this parameter
                        socket = node_group.interface.new_socket(
                            name=param_name,
                            in_out='INPUT',
                            socket_type='NodeSocketInt'
                        )

                        # Set the min, max, and default values
                        socket.min_value = min_val
                        socket.max_value = max_val
                        socket.default_value = default_val

                # Replace the existing elif isinstance(param_data, list): section with this:

                elif isinstance(param_data, list):
                    # This is a categorical parameter (enum)
                    debug_print(f"Processing list parameter: {param_name}, options: {param_data}")

                    # Check if this list contains strings (not booleans)
                    has_strings = any(isinstance(item, str) for item in param_data)

                    if has_strings:
                        # Create menu switch node for string-based options
                        debug_print(f"Creating menu switch node for: {param_name}")

                        # Create a menu socket
                        socket = node_group.interface.new_socket(
                            name=param_name,
                            in_out='INPUT',
                            socket_type='NodeSocketMenu'
                        )

                        # Create a menu switch node
                        menu_switch_node = node_group.nodes.new("GeometryNodeMenuSwitch")
                        menu_switch_node.name = f"MenuSwitch_{param_name}"
                        menu_switch_node.label = param_name
                        menu_switch_node.location = (0, y_offset)

                        # Set the data type to String for string options
                        menu_switch_node.data_type = 'GEOMETRY'

                        # Clear existing enum items and add our options
                        menu_switch_node.enum_definition.enum_items.clear()
                        for i, option in enumerate(param_data):
                            if isinstance(option, str):
                                item = menu_switch_node.enum_definition.enum_items.new(str(option))
                                item.name = str(option)
                                item.description = f"{param_name} option: {option}"

                        # Connect the input socket to the menu switch node
                        node_group.links.new(
                            input_node.outputs[param_name],
                            menu_switch_node.inputs['Menu']
                        )

                        # Store the options as a custom property for reference
                        node_group["menu_options_" + param_name] = ",".join(str(item) for item in param_data)
                        debug_print(f"Created menu switch node for {param_name} with {len(param_data)} string options")

                    else:
                        # Check if this is a boolean list
                        has_booleans = all(isinstance(item, bool) for item in param_data)

                        if has_booleans:
                            # For boolean lists, use boolean socket
                            socket = node_group.interface.new_socket(
                                name=param_name,
                                in_out='INPUT',
                                socket_type='NodeSocketBool'
                            )

                            # Set default to first boolean value
                            socket.default_value = param_data[0]

                            # Store the boolean options as a custom property
                            node_group["bool_options_" + param_name] = ",".join(str(item) for item in param_data)
                            debug_print(f"Created boolean socket for {param_name} with options: {param_data}")
                        else:
                            # For other non-string lists, use integer socket
                            socket = node_group.interface.new_socket(
                                name=param_name,
                                in_out='INPUT',
                                socket_type='NodeSocketInt'
                            )

                            # Set the min, max, and default values
                            socket.min_value = 0
                            socket.max_value = len(param_data) - 1
                            socket.default_value = 0  # Default to first option

                            # Store the enum options as a custom property on the node group
                            node_group["enum_options_" + param_name] = ",".join(str(item) for item in param_data)
                            debug_print(f"Created int socket for {param_name} with {len(param_data)} options")


                y_offset -= 50

        debug_print(f"Node group created with {len(node_group.interface.items_tree)} interface items")
        return node_group

    except Exception as e:
        print(f"ERROR creating parameter node group: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return None

def create_simple_materials(parts_data, object_name):
    """Create simple materials for each part in the config"""
    try:
        print(f"Creating materials for {len(parts_data)} parts: {list(parts_data.keys())}")

        # List existing materials before creating new ones
        existing_materials = list(bpy.data.materials.keys())
        print(f"Existing materials before creation: {existing_materials}")

        materials_created = []

        for part_name in parts_data.keys():
            # Create a material name based on the part name
            material_name = part_name
            print(f"Attempting to create material: {material_name}")

            # Check if the material already exists
            if material_name in bpy.data.materials:
                print(f"Material {material_name} already exists, skipping")
                continue
            else:
                try:
                    # Create a new material with default settings
                    mat = bpy.data.materials.new(name=material_name)
                    mat.use_nodes = True
                    materials_created.append(material_name)
                    print(f"Successfully created material: {material_name}")
                except Exception as e:
                    print(f"Error creating material {material_name}: {e}")

        # List materials after creation to verify
        new_materials = list(bpy.data.materials.keys())
        print(f"Materials after creation: {new_materials}")
        print(f"Materials created in this run: {materials_created}")

        return materials_created

    except Exception as e:
        print(f"ERROR creating materials: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return []

def assign_materials_to_object(material_names, obj):
    """Assign materials to the active object, regardless of its shape"""
    try:
        print(f"Assigning {len(material_names)} materials to object: {obj.name}")

        # Make sure the object can have materials
        if not hasattr(obj, 'data') or not hasattr(obj.data, 'materials'):
            print(f"Object {obj.name} cannot have materials assigned")
            return False

        # Clear existing materials
        obj.data.materials.clear()
        print(f"Cleared existing materials")

        # Add each material to the object
        for mat_name in material_names:
            if mat_name in bpy.data.materials:
                # Get the material
                mat = bpy.data.materials[mat_name]

                # Append the material to the object's materials
                obj.data.materials.append(mat)
                print(f"Assigned material {mat_name} to slot {len(obj.data.materials)-1}")
            else:
                print(f"Material {mat_name} not found in bpy.data.materials")

        # Make sure the object uses material slots
        if hasattr(obj, 'material_slots') and len(obj.material_slots) > 0:
            print(f"Object has {len(obj.material_slots)} material slots")
        else:
            print(f"Object doesn't have material slots after assignment")

        print(f"Successfully assigned {len(material_names)} materials to {obj.name}")
        print(f"You can find these materials in the Materials tab in the Properties panel")
        print(f"To use them in Edit mode, select faces and assign them to specific material slots")

        return True

    except Exception as e:
        print(f"ERROR assigning materials: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

def main():
    try:
        print("\n=== STARTING CONFIG TO BLENDER SCRIPT ===")

        # Check if Blender is running in background mode
        if bpy.app.background:
            print("WARNING: Blender is running in background mode, no UI updates will be visible")

        # Check if an object is selected
        if not bpy.context.active_object:
            print("ERROR: No active object selected. Please select an object before running the script.")
            print("The script will still create the node group and materials, but won't apply them to any object.")
        else:
            debug_print(f"Active object: {bpy.context.active_object.name}")

        # Check if a config path was specified at the top of the script
        if CONFIG_PATH:
            print(f"Using config path from script variable: {CONFIG_PATH}")
            config_path = CONFIG_PATH
        else:
            # Get the command line arguments
            argv = sys.argv
            argv = argv[argv.index("--") + 1:] if "--" in argv else []

            if len(argv) > 0:
                # Use the provided file path from command line
                print(f"Using config path from command line: {argv[0]}")
                config_path = argv[0]
            else:
                # Try to get the directory of the current .blend file
                try:
                    # Get the directory of the current .blend file
                    blend_dir = bpy.path.abspath("//")
                    if not blend_dir:
                        print("ERROR: Could not determine the directory of the current .blend file.")
                        print("Please save your .blend file before running this script.")
                        return

                    print(f"Looking for config files in Blender file directory: {blend_dir}")

                    # Look for config files in the .blend file directory
                    if os.path.exists(blend_dir):
                        config_files = [f for f in os.listdir(blend_dir) if f.endswith("_Config.json") or f.endswith("_config.json")]

                        if not config_files:
                            print("ERROR: No config files found in the Blender file directory.")
                            print("Please place a config file in the same directory as your .blend file.")
                            return
                        elif len(config_files) > 1:
                            print("ERROR: Multiple config files found in the Blender file directory:")
                            for cf in config_files:
                                print(f"  - {cf}")
                            print("Please specify a single config file using CONFIG_PATH at the top of the script.")
                            return
                        else:
                            config_path = os.path.join(blend_dir, config_files[0])
                            print(f"Found config file: {config_path}")
                    else:
                        print(f"Blender file directory not accessible: {blend_dir}")
                        return
                except Exception as e:
                    print(f"Error finding config file: {e}")
                    print(f"Traceback: {traceback.format_exc()}")
                    print("Please specify a config file path at the top of the script.")
                    return

        # Load the config file
        node_group = load_config_file(config_path)

        # Add the node group to the active object if one exists
        if node_group and bpy.context.active_object:
            debug_print(f"Adding node group to active object: {bpy.context.active_object.name}")

            # Check if the object already has a geometry nodes modifier
            modifier = None
            for mod in bpy.context.active_object.modifiers:
                if mod.type == 'NODES':
                    modifier = mod
                    debug_print(f"Found existing geometry nodes modifier: {mod.name}")
                    break

            # If no modifier exists, create one
            if not modifier:
                debug_print("Creating new geometry nodes modifier")
                modifier = bpy.context.active_object.modifiers.new(name=node_group.name, type='NODES')

            # Set the node group
            debug_print(f"Setting node group: {node_group.name}")
            modifier.node_group = node_group

            print(f"Successfully applied node group '{node_group.name}' to object '{bpy.context.active_object.name}'")
            print("You can find the parameters in the modifier panel of the active object")
        else:
            if not node_group:
                print("Failed to create node group.")
            if not bpy.context.active_object:
                print("No active object selected. The node group was created but not applied to any object.")
                print("To use the node group, select an object and add a Geometry Nodes modifier, then select the node group.")

        print("=== SCRIPT COMPLETED ===")

    except Exception as e:
        print(f"ERROR in main function: {e}")
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    main()
