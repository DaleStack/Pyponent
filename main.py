from src.pyponent.core import VNode
from src.pyponent.hooks import use_state
from src.pyponent.web import run

def Counter(props):
    count, set_count = use_state(0)
    btn_id = props.get("id", "btn") 
    
    return VNode(
        tag="div",
        props={"style": "margin: 10px; padding: 10px; border: 1px solid #ccc;"},
        children=[
            VNode(tag="span", children=[f"Count: {count}  "]),
            VNode(
                tag="button",
                props={"id": btn_id, "onClick": lambda: set_count(count + 1)},
                children=["Add +1"]
            )
        ]
    )

def App():
    return VNode(
        tag="div",
        props={"style": "font-family: sans-serif; padding: 2rem;"},
        children=[
            VNode(tag="h1", children=["Pyponent Framework"]),
            VNode(tag=Counter, props={"id": "btn-1"}),
            VNode(tag=Counter, props={"id": "btn-2"}) 
        ]
    )

if __name__ == "__main__":
    # The magic single-line entry point!
    run(App, port=8000)