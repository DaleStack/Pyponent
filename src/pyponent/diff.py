from .core import VNode, render_to_string

def diff_vdom(old, new):
    patches = []

    if old.tag != new.tag:
        return [{"type": "replace", "id": old.id, "html": render_to_string(new)}]

    new.id = old.id
    new.props["id"] = old.id

    # Filter out functions before diffing and sending
    safe_old_props = {k: v for k, v in old.props.items() if not callable(v) and not k.startswith("on")}
    safe_new_props = {k: v for k, v in new.props.items() if not callable(v) and not k.startswith("on")}

    if safe_old_props != safe_new_props:
        patches.append({"type": "props", "id": new.id, "props": safe_new_props})

    if len(old.children) != len(new.children):
        inner_html = "".join(render_to_string(c) for c in new.children)
        patches.append({"type": "inner_html", "id": new.id, "html": inner_html})
    else:
        for o_child, n_child in zip(old.children, new.children):
            if isinstance(o_child, VNode) and isinstance(n_child, VNode):
                patches.extend(diff_vdom(o_child, n_child))
            elif o_child != n_child:
                inner_html = "".join(render_to_string(c) for c in new.children)
                patches.append({"type": "inner_html", "id": new.id, "html": inner_html})
                break

    return patches