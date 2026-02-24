from .core import VNode


def component(component_func, *children, **kwargs):
    """Helper to instantiate a custom Python function as a Pyponent component."""
    props = kwargs
    return VNode(tag=component_func, props=props, children=list(children))

def _make_tag(tag_name):
    """Factory function to generate HTML tag helpers."""
    def tag_helper(*children, **kwargs):
        props = {}
        for key, value in kwargs.items():
            # Handle Python reserved keywords! 
            # We can't use `class=` in Python, so we use `class_name=` instead.
            if key == "class_name":
                props["class"] = value
            elif key == "html_for":
                props["for"] = value
            # Convert underscores to hyphens (e.g., data_id -> data-id)
            elif key.startswith("data_") or key.startswith("aria_"):
                props[key.replace("_", "-")] = value
            else:
                props[key] = value
                
        # Automatically unpack lists if a user passes a list of children
        flat_children = []
        for child in children:
            if isinstance(child, list):
                flat_children.extend(child)
            else:
                flat_children.append(child)

        return VNode(tag=tag_name, props=props, children=flat_children)
    
    return tag_helper



# Generate standard HTML elements
div = _make_tag("div")
span = _make_tag("span")
p = _make_tag("p")
h1 = _make_tag("h1")
h2 = _make_tag("h2")
button = _make_tag("button")
form = _make_tag("form")
label = _make_tag("label")

# Python has a built-in `input()` function, so we must name this one `input_`
input_ = _make_tag("input") 

# You can easily add more tags here as you need them!