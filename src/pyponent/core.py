from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Union
from src.pyponent.hooks import dispatcher

@dataclass
class VNode:
    # Now tag can be a string ("div") OR a component function (Counter)
    tag: Union[str, Callable] 
    props: Dict[str, Any] = field(default_factory=dict)
    children: List[Union['VNode', str]] = field(default_factory=list)

def render_to_string(node: Union[VNode, str]) -> str:
    """Recursively converts a VNode tree into an HTML string."""
    if isinstance(node, str):
        return node
    
    # Extract standard HTML attributes (ignore events like onClick for the string)
    html_attrs = []
    for key, value in node.props.items():
        if not key.startswith("on"):
            html_attrs.append(f'{key}="{value}"')
            
    attr_str = " " + " ".join(html_attrs) if html_attrs else ""
    children_str = "".join(render_to_string(child) for child in node.children)
    
    return f"<{node.tag}{attr_str}>{children_str}</{node.tag}>"

def fire_event(node: Union['VNode', str], target_id: str, event_name: str) -> bool:
    """Recursively searches the VNode tree for an ID and fires its event."""
    # Strings don't have properties or events
    if isinstance(node, str):
        return False

    # 1. Check if the current node is the target
    if node.props.get("id") == target_id:
        handler = node.props.get(event_name)
        if handler:
            handler() # Execute the lambda function!
            return True
        return False

    # 2. If not found, recursively search the children
    for child in node.children:
        if fire_event(child, target_id, event_name):
            return True # Stop searching once we found and fired it

    return False

def resolve_vdom(node: Union[VNode, str], path: str = "root") -> Union[VNode, str]:
    """Recursively resolves component functions into pure HTML VNodes."""
    if isinstance(node, str):
        return node

    # 1. Is this a Function Component?
    if callable(node.tag):
        # Create a unique ID based on its name and path in the tree
        node_id = f"{node.tag.__name__}_{path}"
        
        # Tell the dispatcher to attach state to THIS specific ID
        dispatcher.prepare_render(node_id)
        
        # Execute the function to get the inner VNode
        # (Pass props if the function expects them, otherwise call empty)
        try:
            resolved_component = node.tag(node.props)
        except TypeError:
            resolved_component = node.tag() # Fallback for components without props
            
        # The component might return another component! Resolve it recursively.
        return resolve_vdom(resolved_component, path)

    # 2. It's a standard HTML tag ("div", "h1", etc.)
    # We must resolve all of its children, appending to the path so each child is unique
    resolved_children = []
    for index, child in enumerate(node.children):
        child_path = f"{path}.{index}"
        resolved_children.append(resolve_vdom(child, child_path))

    # Return a clean HTML VNode
    return VNode(tag=node.tag, props=node.props, children=resolved_children)