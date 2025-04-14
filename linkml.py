import json
import yaml
from typing import Dict, Any, Optional, List, Union, Set

def linkml_file(json_data: Dict[str, Any],
                schema_name: str = "GeneratedSchema",
                root: str = "MainClass") -> str:
   
    schema = {
        "id": f"http://example.com/{schema_name}",  
        "name": schema_name,                       
        "classes": {                               
            root: {"attributes": {}}             
        }
    }
    
    process_node(json_data, schema["classes"][root]["attributes"], schema)

    return yaml.dump(schema, sort_keys=False, width=200, allow_unicode=True)


def process_node(data: Any,
                 attributes: Dict[str, Any],
                 schema: Dict[str, Any],
                 parent_path: Optional[str] = None) -> None:
    
    if isinstance(data, dict):
    
        for key, value in data.items():
            
            current_path = f"{parent_path}_{key}" if parent_path else key

            if isinstance(value, dict):
                attr_def = {"range": current_path,          
                            "description": f"computing nested object: {current_path}"
                            }

                attributes[key] = attr_def  
                
            
                if current_path not in schema["classes"]:
                    schema["classes"][current_path] = {"attributes": {}}
                    
                    process_node(value, schema["classes"][current_path]["attributes"], schema, current_path)

            elif isinstance(value, list) and value:
                element_types = _get_list_element_types(value)
                
                if len(element_types) == 1 and isinstance(next(iter(element_types)), dict):
                    item_class = f"{current_path}_Item"

                    attr_def = {"range": item_class,
                                "multivalued": True,       
                                "description": f"对象数组: {current_path}"
                                }
                    
                    attributes[key] = attr_def
                    
                    if item_class not in schema["classes"]:
                        schema["classes"][item_class] = {"attributes": {}}
                        process_node(value[0], schema["classes"][item_class]["attributes"], schema, item_class)

                else:
                    attr_def = {
                        "range": resolve_mixed_types(element_types, current_path, schema),
                        "multivalued": True,       
                        "description": f"Mixed Type Arrays: {current_path}"
                    }
                    attributes[key] = attr_def

            else:
                attributes[key] = attribute_definition(value, key)



def _get_list_element_types(lst: List[Any]) -> Set[type]:
    return {type(x) for x in lst}


def resolve_mixed_types(types: Set[type],
                        current_path: str,
                        schema: Dict[str, Any]) -> str:
    
    type_mapping = {
        str: "string",
        int: "integer",
        float: "float",
        bool: "boolean",
        dict: f"{current_path}_Item" 
    }

    resolved_types = []
    for t in types:
        if t in type_mapping:
            resolved_types.append(type_mapping[t])
        else:
            resolved_types.append("string")

    if len(resolved_types) == 1:
        return resolved_types[0]
    else:
        return f"anyOf: [{', '.join(resolved_types)}]"

def attribute_definition(value: Any, key: str) -> Dict[str, Any]:
    type_mapping = {
        str: {"range": "string"},
        int: {"range": "integer"},
        float: {"range": "float"},
        bool: {"range": "boolean"},
        list: {"range": "string", "multivalued": True}  
    }
    return type_mapping.get(type(value), {"range": "string"})


if __name__ == "__main__":
    with open("P04637.json") as f:
        data = json.load(f)

    yaml_schema = linkml_file(data, "P04637_Schema")

    with open("testlinkml.yaml", "w", encoding='UTF-8') as f:
        f.write(yaml_schema)