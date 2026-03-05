# Pyponent

**Pyponent** is a blazing-fast, Server-Driven UI (SDUI) framework for Python. It allows you to build highly interactive, real-time Single Page Applications (SPAs) entirely in Python—without writing a single line of JavaScript, HTML, or CSS (unless you want to).

Powered by **FastAPI** and **WebSockets**, Pyponent manages state on the server, calculates Virtual DOM diffs in pure Python, and surgically updates the browser using granular JSON patches. 

---

## Why was Pyponent made?
Modern web development often requires massive context switching. To build a dynamic web app, developers usually have to write Python for the backend, design APIs, configure Webpack/Vite, and write JavaScript/React for the frontend. 

**Pyponent was built to eliminate the frontend build step.** It is designed for Python developers who want to build complex, interactive dashboards and tools at the speed of thought, keeping their data, state, and UI logic perfectly synced in one unified codebase.



---

## Pros and Cons

### Pros
* **Zero JavaScript:** Build modals, interactive forms, and real-time dashboards using pure Python.
* **Granular DOM Diffing:** Unlike older frameworks that reload the whole page, Pyponent sends tiny JSON patches over WebSockets, preserving cursor focus and scrolling.
* **Built-in SPA Routing:** Includes a client-side router (`Router` and `Link`) for instant, zero-refresh page navigation.
* **Native Tailwind Support:** Turn on Tailwind CSS with a single boolean flag.
* **Secure by Default:** Because state lives on the server, sensitive business logic and API keys are never exposed to the browser.

### Cons
* **Requires Always-On Connection:** Pyponent relies entirely on WebSockets. It does not work offline.
* **Network Latency:** Every button click travels to the server and back. It is incredibly fast, but not suited for high-frequency client-side animations (like 60fps drag-and-drop or WebGL games).
* **State Management Scale:** Because the server holds the state for every connected user, massive applications with millions of concurrent users will require careful load balancing.

---

## How it Works



1. **Initial Load:** You define components in Python. Pyponent renders them to a static HTML string and sends it to the browser.
2. **WebSocket Connection:** The browser connects back to the FastAPI server via WebSockets.
3. **Interactivity:** When a user clicks a button or types in an input, the browser sends a tiny JSON event `{"event_name": "onClick", "target_id": "btn-1"}` to the server.
4. **Reconciliation:** Python updates the state, rebuilds the Virtual DOM in memory, and calculates the exact differences.
5. **Patching:** Python sends a surgical JSON patch back to the browser, updating only the elements that changed.

---

## Installation & Quick Start

*(Note: Pyponent is designed to run alongside Uvicorn and FastAPI).*

```bash
pip install pyponent fastapi uvicorn
```

## The "Hello World" App

Create a file named `main.py`
```python
from fastapi import FastAPI
from pyponent.web import setup_pyponent, run
from pyponent.html import div, h1, p

def App(**props):
    return div(
        h1("Hello, Pyponent!"),
        p("This is a pure Python UI.")
    )

app = FastAPI()

# Attach Pyponent to your FastAPI app
setup_pyponent(app, App, title="My First App")

if __name__ == "__main__":
    run("main:app", port=8000, reload=True)
```
Run it via terminal: `python main.py` or `uv run main.py`


## Core Features

### 1. State & Interactivity (`use_state`)
Add interactivity without JavaScript. Just bind state to your HTML elements.
```python
from pyponent.hooks import use_state
from pyponent.html import div, h2, button

def Counter(**props):
    count, set_count = use_state(0)
    
    return div(
        h2(f"Clicks: {count}"),
        button("Increment", onClick=lambda e: set_count(count + 1))
    )
```

### 2. Live Inputs (No Cursor Loss!)
Because of Pyponent's surgical diffing engine, you can type into inputs without the DOM reloading.

⚠️ Golden Rule: Always provide a hardcoded id for text inputs!
```python
from pyponent.hooks import use_state
from pyponent.html import div, input_, p

def LiveMirror(**props):
    text, set_text = use_state("")
    
    return div(
        input_(
            id="mirror-input", # Required!
            type="text",
            value=text,
            onInput=lambda e: set_text(e.get("value", ""))
        ),
        p("You typed: ", text)
    )
```

### 3. Tailwind & Custom Head Tags
Pyponent makes styling effortless. You can inject multiple `meta`, `link`, or `script` tags safely using a list, and opt into Tailwind CSS with a single flag.
```python
from pyponent.hooks import use_state
from pyponent.html import div, input_, p
from pyponent.web import setup_pyponent

my_seo_tags = [
    '<meta name="description" content="A blazing fast Pyponent App.">',
    'styles/sample.css', # Use styles/ directory, it has automatic injection
    '<script src="[https://js.stripe.com/v3/](https://js.stripe.com/v3/)"></script>'
]

setup_pyponent(
    app, 
    App, 
    title="My E-Commerce Dashboard", 
    use_tailwind=True,  # Instantly activates Tailwind CDN!
    meta_tags=my_seo_tags
)
```

### 4. Zero Refresh Routing
Build Multi-Page Applications without page reloads using the built-in router.
```python
from pyponent.router import Router, Link

def Navigation(**props):
    return div(
        # Use Link for internal SPA navigation and a tag for external
        Link(to="/", children=["Home"]),
        Link(to="/dashboard", children=["Dashboard"])
    )

def App(**props):
    return div(
        Navigation(),
        Router(
            initial_path=props.get("initial_path", "/"),
            routes={
                "/": HomePage,
                "/dashboard": DashboardPage
            }
        )
    )
```