import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Union
from .hooks import dispatcher_context

@dataclass
class VNode:
    tag: Union[str, Callable] 
    props: Dict[str, Any] = field(default_factory=dict)
    children: List[Union['VNode', str]] = field(default_factory=list)
    id: str = field(init=False) # Tell dataclass we will set this ourselves

    def __post_init__(self):
        # Guarantee an ID for every element for the Diffing Engine 
        if "id" not in self.props:
            self.props["id"] = f"pyp-{uuid.uuid4().hex[:8]}"
        self.id = self.props["id"]

def render_to_string(node: Union[VNode, str]) -> str:
    if isinstance(node, str):
        return node
    
    html_attrs = []
    for key, value in node.props.items():
        if not key.startswith("on"):
            html_attrs.append(f'{key}="{value}"')
            
    attr_str = " " + " ".join(html_attrs) if html_attrs else ""
    children_str = "".join(render_to_string(child) for child in node.children)
    return f"<{node.tag}{attr_str}>{children_str}</{node.tag}>"

def fire_event(node: Union['VNode', str], target_id: str, event_name: str, event_data: dict = None) -> bool:
    if isinstance(node, str):
        return False

    if node.props.get("id") == target_id:
        handler = node.props.get(event_name)
        if handler:
            try:
                # Pass the typing payload to the user's function
                handler(event_data or {})
            except TypeError:
                # If they didn't ask for the payload (like a simple button click), run it empty
                handler() 
            return True
        return False

    for child in node.children:
        if fire_event(child, target_id, event_name, event_data):
            return True

    return False

def resolve_vdom(node: Union[VNode, str], path: str = "root") -> Union[VNode, str]:
    if isinstance(node, str):
        return node

    if callable(node.tag):
        node_id = f"{node.tag.__name__}_{path}"
        current_dispatcher = dispatcher_context.get()
        current_dispatcher.prepare_render(node_id)
        
        try:
            # Use ** to unpack the dictionary into keyword arguments
            resolved_component = node.tag(**node.props)
        except TypeError:
            resolved_component = node.tag() 
            
        return resolve_vdom(resolved_component, path)

    resolved_children = []
    for index, child in enumerate(node.children):
        if child is None:
            continue
        child_path = f"{path}.{index}"
        resolved_children.append(resolve_vdom(child, child_path))

    return VNode(tag=node.tag, props=node.props, children=resolved_children)