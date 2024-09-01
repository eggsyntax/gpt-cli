"""
This module provides functionality to process and modify a list of nested data structures
based on provider-specific mappings. It allows for key renaming, value modifications,
key deletion, key addition, and top-level transformations using a dot-notation path.
"""

import json
import re
from typing import Any, Dict, Union, List, Callable

def modify_key(data: Any, key_path: str, new_key: Union[str, re.Pattern]) -> Any:
    """
    Modify or delete a key in a nested data structure.

    Args:
        data (Any): The data structure to modify.
        key_path (str): Dot-notation path to the key to be modified or deleted.
        new_key (Union[str, re.Pattern]): New key name, regex pattern for replacement,
                                          or empty string for deletion.

    Returns:
        Any: The modified data structure.
    """
    def _modify(d: Any, keys: list, new_k: Union[str, re.Pattern]) -> Any:
        if not keys:
            return d
        if isinstance(d, dict):
            key = keys[0]
            if len(keys) == 1:
                if isinstance(new_k, str):
                    if new_k == "":  # Delete the key
                        d.pop(key, None)
                    else:  # Rename the key
                        d[new_k] = d.pop(key)
                else:  # regex
                    for k in list(d.keys()):
                        if re.match(new_k, k):
                            new_key_name = re.sub(new_k, new_k.pattern, k)
                            if new_key_name == "":  # Delete the key
                                d.pop(k, None)
                            else:  # Rename the key
                                d[new_key_name] = d.pop(k)
            else:
                if key in d:
                    d[key] = _modify(d[key], keys[1:], new_k)
        return d

    keys = key_path.split('.')
    return _modify(data, keys, new_key)

def modify_value(data: Any, key_path: str, modifier: Callable[[], Any]) -> Any:
    """
    Modify a value or add a new key/value pair in a nested data structure. If
    the key exists, calls the `modifier` function on the old value to transform
    it. If the key doesn't exist, calls the `modifier` function with no
    arguments to generate a value to insert.

    Args:
        data (Any): The data structure to modify.
        key_path (str): Dot-notation path to the value to be modified or added.
        modifier (Callable[[], Any]): Function to apply to the value or generate a new value.

    Returns:
        Any: The modified data structure.
    """
    def _modify(d: Any, keys: list, mod: Callable[[], Any]) -> Any:
        if not keys:
            return d
        if isinstance(d, dict):
            key = keys[0]
            if len(keys) == 1:
                if key in d:
                    d[key] = mod(d[key])
                else:
                    d[key] = mod()  # Add new key/value pair
            else:
                if key not in d:
                    d[key] = {}  # Create nested dict if it doesn't exist
                d[key] = _modify(d[key], keys[1:], mod)
        return d

    keys = key_path.split('.')
    return _modify(data, keys, modifier)

def process_single_map(data: Dict[str, Any], mappings: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Process a single map using the provided mappings.

    Args:
        data (Dict[str, Any]): The map to process.
        mappings (Dict[str, Dict[str, Any]]): The mappings to apply.

    Returns:
        Dict[str, Any]: The processed map.
    """
    # Apply key modifications (including deletions)
    for key_path, new_key in mappings['key_mappings'].items():
        data = modify_key(data, key_path, new_key)

    # Apply value modifications (including additions)
    for key_path, modifier in mappings['value_mappings'].items():
        if key_path == "":
            # Apply top-level transformation
            data = modifier(data)
        else:
            data = modify_value(data, key_path, modifier)

    return data

def load_functions(filename: str, provider_name: str) -> str:
    """
    Process data from a JSON file containing a list of maps using provider-specific mappings.

    This function reads a JSON file containing a list of maps, applies key and value modifications
    (including key deletions, additions, and top-level transformations) to each map based on the
    specified provider's mappings, and returns the modified data as a JSON string.

    Args:
        filename (str): Path to the JSON file to process.
        provider_name (str): Name of the provider whose mappings to use.

    Returns:
        str: JSON string of the modified data (a list of processed maps).

    Raises:
        ValueError: If the specified provider is not found in the mappings or if the input is not a list.
        json.JSONDecodeError: If the input file is not valid JSON.
        FileNotFoundError: If the specified file does not exist.
    """
    # Read the file
    with open(filename, 'r') as file:
        data_list = json.load(file)

    # Ensure data_list is a list
    if not isinstance(data_list, list):
        raise ValueError("Input JSON must contain a list of maps")

    with open('./gptcli/provider_mappings.py') as f:
        mappings_string = f.read()
        provider_mappings = eval(mappings_string) # you're sure it's safe, right?
    mappings = provider_mappings.get(provider_name)
    if not mappings:
        raise ValueError(f"Unknown provider: {provider_name}")

    # Process each map in the list
    processed_data = [process_single_map(item, mappings) for item in data_list]
    return processed_data

# Example usage
if __name__ == "__main__":
    result = load_functions("sample_data.json", "example_provider")
    print(result)
