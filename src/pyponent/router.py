# src/pyponent/router.py
from .hooks import use_state, dispatcher_context
from .html import a, div

def Router(**props):  # <-- FIX: Added ** here
    routes = props.get("routes", {})
    initial_path = props.get("initial_path", "/")
    
    # The Router's state is literally just the current URL!
    current_path, set_current_path = use_state(initial_path)
    
    # We store the 'navigate' function globally in the dispatcher 
    # so that ANY <Link> component on the page can trigger a route change.
    dispatcher = dispatcher_context.get()
    dispatcher.navigate = set_current_path
    
    # Find the matching component for the current URL
    RouteComponent = routes.get(current_path)
    
    if not RouteComponent:
        return div(f"404 - Page {current_path} Not Found", style="color: red; padding: 20px;")
        
    return RouteComponent()

def Link(**props): # <-- FIX: Added ** here
    to = props.get("to", "/")
    
    def on_click(e):
        dispatcher = dispatcher_context.get()
        if hasattr(dispatcher, 'navigate'):
            # Trigger the Router state update!
            dispatcher.navigate(to)
            
    # We add a special data attribute so our JS shell knows to intercept this click
    return a(
        *props.get("children", []),
        href=to,
        onClick=on_click,
        data_pyponent_link="true", 
        **{k: v for k, v in props.items() if k not in ["to", "children", "onClick"]}
    )