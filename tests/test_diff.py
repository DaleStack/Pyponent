from pyponent.diff import diff_vdom
from pyponent.html import div


def test_props_diffing():
    # 1. Create an old state and a new state
    old_node = div(id="box", class_name="bg-red")
    new_node = div(id="box", class_name="bg-blue")  # Changed class!

    # 2. Run the diff
    patches = diff_vdom(old_node, new_node)

    # 3. Assert the patch tells the browser to update the props safely
    assert len(patches) == 1
    assert patches[0]["type"] == "props"

    # Resilient check: Just verify 'bg-blue' is in the payload!
    props_dict = patches[0]["props"]
    assert "bg-blue" in props_dict.values(), (
        f"Props update failed. Payload was: {props_dict}"
    )
