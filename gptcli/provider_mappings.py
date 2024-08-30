# import json
# import re
#
# provider_mappings = {
{
    "example_provider": {
        "key_mappings": {
            "personal_info.name": "full_name",
            "personal_info.age": "years_old",
            "contact": re.compile(r"^contact_(.+)$"),
            "to_be_deleted": ""  # This key will be deleted
        },
        "value_mappings": {
            "personal_info.full_name": lambda x: x.upper(),
            "personal_info.years_old": lambda x: x * 2,
            "addresses": lambda x: [addr.capitalize() for addr in x],
            "new_key": lambda: "This is a new value",  # This key will be added if it doesn't exist
            "": lambda x: {**x, "top_level_key": "Added by top-level transformation"}  # Top-level transformation
        }
    },
    "openai": {
        "key_mappings": {},
        "value_mappings": {
            "parameters.additionalProperties": lambda: False,
            "": lambda struct: f'''{{"type": "function", "function": {json.dumps(struct)}}}'''
        }
    },
    "anthropic": {
        "key_mappings": {
            "parameters": "input_schema"
        },
        "value_mappings": {
        }
    }
}
