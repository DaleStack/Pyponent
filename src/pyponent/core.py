from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Union

# 1. Import the context variable instead of the old singleton
from src.pyponent.hooks import dispatcher_context

@dataclass
class VNode:
    tag: Union[str, Callable] 
    props: Dict[str, Any] = field(default_factory=dict)
    children: List[Union['VNode', str]] = field(default_factory=list)

def render_to_string(node: Union[VNode, str]) -> str:
    """Recursively converts a VNode tree into an HTML string."""
    if isinstance(node, str):
        return node
    
    html_attrs = []
    for key, value in node.props.items():
        if not key.startswith("on"):
            html_attrs.append(f'{key}="{value}"')
            
    attr_str = " " + " ".join(html_attrs) if html_attrs else ""
    children_str = "".join(render_to_string(child) for child in node.children)
    
    return f"<{node.tag}{attr_str}>{children_str}</{node.tag}>"

def fire_event(node: Union['VNode', str], target_id: str, event_name: str) -> bool:
    """Recursively searches the VNode tree for an ID and fires its event."""
    if isinstance(node, str):
        return False

    if node.props.get("id") == target_id:
        handler = node.props.get(event_name)
        if handler:
            handler() 
            return True
        return False

    for child in node.children:
        if fire_event(child, target_id, event_name):
            return True

    return False

def resolve_vdom(node: Union[VNode, str], path: str = "root") -> Union[VNode, str]:
    """Recursively resolves component functions into pure HTML VNodes."""
    if isinstance(node, str):
        return node

    if callable(node.tag):
        node_id = f"{node.tag.__name__}_{path}"
        
        # 2. Fetch the specific dispatcher for THIS web request/tab
        current_dispatcher = dispatcher_context.get()
        current_dispatcher.prepare_render(node_id)
        
        try:
            resolved_component = node.tag(node.props)
        except TypeError:
            resolved_component = node.tag() 
            
        return resolve_vdom(resolved_component, path)

    resolved_children = []
    for index, child in enumerate(node.children):
        child_path = f"{path}.{index}"
        resolved_children.append(resolve_vdom(child, child_path))

    return VNode(tag=node.tag, props=node.props, children=resolved_children)