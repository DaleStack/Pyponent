from .hooks import dispatcher_context, use_state
from .html import a, div


def Router(**props):
    routes = props.get("routes", {})
    initial_path = props.get("initial_path", "/")

    # The Router's state is literally just the current URL
    current_path, set_current_path = use_state(initial_path)

    # We store the 'navigate' function globally in the dispatcher
    # so that ANY <Link> component on the page can trigger a route change.
    dispatcher = dispatcher_context.get()
    dispatcher.navigate = set_current_path

    # Find the matching component for the current URL
    RouteComponent = routes.get(current_path)

    if not RouteComponent:
        return div(
            f"404 - Page {current_path} Not Found", 
            style="color: red; padding: 20px;"
        )

    return div(
        RouteComponent(),
        id="pyponent-router-wrapper",
        data_pyponent_url=current_path
    )


def Link(*children, **props):
    to = props.get("to", "/")

    def on_click(e):
        dispatcher = dispatcher_context.get()
        if hasattr(dispatcher, "navigate"):
            dispatcher.navigate(to)

    return a(
        *children,   
        href=to,
        onClick=on_click,
        data_pyponent_link="true",
        # Removed "children" from the exclusion list since it's no longer in props
        **{k: v for k, v in props.items() if k not in ["to", "onClick"]},
    )