from src.pyponent.core import VNode
from src.pyponent.hooks import use_state
from src.pyponent.web import run

def NameCard(props):
    # State to hold what the user types
    name, set_name = use_state("")
    
    return VNode(
        tag="div",
        props={"style": "padding: 20px; border: 2px solid blue; border-radius: 8px; width: 300px;"},
        children=[
            VNode(tag="h2", children=[f"Hello, {name}!" if name else "Who are you?"]),
            VNode(
                tag="input",
                props={
                    "id": "name-input",
                    "type": "text",
                    "placeholder": "Type your name...",
                    # We receive the event dictionary 'e' and extract 'value'!
                    "onInput": lambda e: set_name(e.get("value", "")),
                    # We can also dynamically bind the value back to the input
                    "value": name 
                }
            )
        ]
    )

def App():
    return VNode(
        tag="div",
        props={"style": "font-family: sans-serif; padding: 2rem;"},
        children=[
            VNode(tag="h1", children=["Two-Way Data Binding"]),
            VNode(tag=NameCard)
        ]
    )

if __name__ == "__main__":
    run(App, port=8000)