from src.pyponent.hooks import use_state
from src.pyponent.web import run
from src.pyponent.html import div, h1, input_, button, component

def NameCard(props):
    # State to hold what the user types
    name, set_name = use_state("")
    
    return div(
        h1(f"Hello {name}!" if name else "What's your name?"),
        input_(id="name-input",
               type="text", 
               placeholder="Enter your name", 
               value=name, onInput=lambda e: set_name(e.get("value", ""))
        ),
        button("Clear",
               id="clear-btn",
               onClick=lambda: set_name(""),
               style="margin-left: 10px;"
        ),

        style="padding: 20px; border: 2px solid blue; border-radius: 8px; margin-top: 10px;"
    )


def App():
    return div(
        h1("Pyponent is GOOODDDD!!"),
        component(NameCard),
        style="font-family: sans-serif; padding: 2rem;"
    )

if __name__ == "__main__":
    run(App, port=8000)