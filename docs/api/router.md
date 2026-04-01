# Client-Side Routing

Pyponent is a true Single Page Application (SPA) framework. When users navigate between pages, the browser does not perform a full page reload. Instead, Pyponent intercepts the navigation, updates the browser's URL using the HTML5 History API, and swaps out the Virtual DOM over the WebSocket.

This results in instant, flicker-free page transitions while preserving the state of your application.

---

## The `Router` Component

To define the pages of your application, use the `Router` component. It takes a dictionary mapping URL paths to your Python component functions.

```python
from pyponent.html import div, h1
from pyponent.router import Router, Link

def Home(**props):
    return div(
        h1("Welcome Home")
    )

def About(**props):
    return div(
        h1("About Us")
    )

def App(**props):
    # The Router listens to the browser's URL and renders the matching component
    return Router(
        routes={
            "/": Home,
            "/about": About
        }
    )
```

*(Note: The `Router` automatically handles 404s. If a user navigates to an unregistered route, it gracefully falls back or renders an empty node depending on your configuration).*

---

## The `Link` Component

Never use a standard HTML `<a href="...">` tag for internal application navigation! A standard `<a>` tag will force the browser to disconnect the WebSocket and reload the entire page.

Instead, use Pyponent's built-in `Link` component. 

```python
from pyponent.router import Link
from pyponent.html import nav, span

def Navbar(**props):
    return nav(
        # Pass the children as positional arguments, and the destination as 'to='
        Link("Home", to="/", class_name="font-bold text-blue-500 mr-4"),
        Link(span("ℹ️ About"), to="/about", class_name="text-gray-700")
    )
```

!!! tip "How it works under the hood"
    When you use `Link(to="/about")`, Pyponent renders a special anchor tag (`<a data-pyponent-link="true" href="/about">`). When a user clicks it, Pyponent's client-side JavaScript prevents the default reload, updates the URL bar to `/about`, and sends a tiny WebSocket message telling the Python engine to render the `About` component.

---

## Programmatic Navigation

Sometimes you need to change the page automatically without the user clicking a `<Link>`—for example, redirecting them to a dashboard after they successfully log in. 

Because Pyponent's `Dispatcher` is attached to the current user's context, you can trigger a navigation event directly from any Python function using the `use_navigate` hook.

```python
from pyponent.html import div, h1, button
from pyponent.hooks import use_navigate

def LoginScreen(**props):
    # Grab the navigation function for this specific user
    navigate = use_navigate()

    def handle_login():
        # ... verify password ...
        
        # Instantly push the user to the dashboard route!
        navigate("/dashboard")

    return div(
        h1("Login"),
        button("Log In", on_click=handle_login, class_name="bg-green-500 p-2")
    )
```