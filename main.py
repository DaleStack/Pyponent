from fastapi import FastAPI
from src.pyponent.web import setup_pyponent, run
from src.pyponent.html import div, h1, p, style_tag
from src.pyponent.router import Router, Link

# --- Page Components ---
def HomePage(**props):
    return div(
        h1("Welcome Home"),
        p("This is the main dashboard."),
        Link(to="/about", children=["Go to About Page"], style="color: blue;")
    )

def AboutPage(**props):
    return div(
        h1("About Us"),
        p("We are building the future of Python UIs."),
        Link(to="/", children=["Back to Home"], style="color: blue;")
    )

# --- The Root App ---
def App(**props):
    return div(
        style_tag("body { font-family: sans-serif; padding: 20px; }"),
        
        # A persistent navigation bar that never re-renders!
        div(
            Link(to="/", children=["Home"], style="margin-right: 15px; font-weight: bold;"),
            Link(to="/about", children=["About"], style="font-weight: bold;"),
            style="padding-bottom: 20px; border-bottom: 2px solid #ccc; margin-bottom: 20px;"
        ),
        
        # The Router handles swapping the page content below
        Router(
            initial_path=props.get("initial_path", "/"),
            routes={
                "/": HomePage,
                "/about": AboutPage
            }
        )
    )

app = FastAPI()
setup_pyponent(app, App, title="Pyponent Router App")

if __name__ == "__main__":
    run("main:app", port=8000, reload=True)