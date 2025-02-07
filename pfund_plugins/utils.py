import re
import inspect
from typing import Callable

from pfund_plugins.llm.type import SchemaType


def generate_schema_from_docstring(func: Callable) -> SchemaType:
    """
    Automatically generate a JSON schema from a function's signature and docstring.
    """
    # Get function signature
    sig = inspect.signature(func)
    
    # Extract docstring
    docstring = func.__doc__ or ""
    
    # Parse parameter descriptions from docstring
    param_descriptions = {}
    param_pattern = re.compile(r"\s*([\w_]+):\s*(.*?)\n")  # Matches "param_name: description"
    matches = param_pattern.findall(docstring)
    
    for param_name, desc in matches:
        param_descriptions[param_name.strip()] = desc.strip()
    
    # Build schema
    schema = {
        "type": "object",
        "properties": {},
        "required": []
    }

    for param_name, param in sig.parameters.items():
        param_type = param.annotation
        param_info = {"type": "string"}  # Default type
        
        # Handle common Python types
        if param_type == int:
            param_info["type"] = "integer"
        elif param_type == float:
            param_info["type"] = "number"
        elif param_type == bool:
            param_info["type"] = "boolean"

        # Add description if found
        if param_name in param_descriptions:
            param_info["description"] = param_descriptions[param_name]

        # Add property
        schema["properties"][param_name] = param_info

        # Mark as required if no default
        if param.default == inspect.Parameter.empty:
            schema["required"].append(param_name)

    return schema
