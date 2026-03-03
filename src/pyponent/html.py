from .core import VNode
import uuid

def component(component_func, *children, **kwargs):
    """Helper to instantiate a custom Python function as a Pyponent component."""
    props = kwargs
    return VNode(tag=component_func, props=props, children=list(children))

def _make_tag(tag_name):
    def tag_helper(*children, **kwargs):
        props = {}
        has_event = False # Track if this element has an action
        
        for key, value in kwargs.items():
            if key == "class_name":
                props["class"] = value
            elif key == "html_for":
                props["for"] = value
            elif key.startswith("data_") or key.startswith("aria_"):
                props[key.replace("_", "-")] = value
            else:
                props[key] = value
                
            # Check if the user attached an event!
            if key.startswith("on"):
                has_event = True
                
        # --- THE MAGIC FIX ---
        # If there is an event but no ID, generate a secure random one!
        if has_event and "id" not in props:
            props["id"] = f"pyponent-{uuid.uuid4().hex[:8]}"
            
        flat_children = []
        for child in children:
            if isinstance(child, list):
                flat_children.extend(child)
            else:
                flat_children.append(child)

        return VNode(tag=tag_name, props=props, children=flat_children)
    
    return tag_helper


# Style Tag
style_tag = _make_tag("style")

# Generate standard HTML elements
div = _make_tag("div")
span = _make_tag("span")
p = _make_tag("p")
h1 = _make_tag("h1")
h2 = _make_tag("h2")
button = _make_tag("button")
form = _make_tag("form")
label = _make_tag("label")
ul = _make_tag("ul")
li = _make_tag("li")
a = _make_tag("a")
textarea = _make_tag("textarea")

# Python has a built-in `input()` function, so we must name this one `input_`
input_ = _make_tag("input") 

# You can easily add more tags here as you need them!