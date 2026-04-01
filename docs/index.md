# Pyponent

**A Pythonic, Server-Driven UI Framework over WebSockets.**

[![PyPI version](https://img.shields.io/pypi/v/pyponent.svg)](https://pypi.org/project/pyponent/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## What is Pyponent?

Pyponent allows you to build highly interactive, real-time web applications **without writing a single line of JavaScript**. 

Instead of building a separate React frontend and a FastAPI backend, Pyponent keeps your application state in Python's RAM. It uses a blazing-fast Virtual DOM and an always-open WebSocket connection to push micro-updates directly to the browser.

You get the seamless, single-page-application (SPA) feel of React, with the simplicity and power of pure Python.

[Get Started Now](getting-started/quickstart.md){ .md-button .md-button--primary }

[View on GitHub](https://github.com/dalestack/pyponent){ .md-button }

---

## The Magic in Action

Building a fully interactive, stateful component is as simple as writing a Python function. Notice how we use `use_state` to manage variables and standard Python logic for event handlers!

```python
from pyponent.html import div, h1, p, button
from pyponent.hooks import use_state

def Counter(**props):
    # 1. State lives on the server!
    count, set_count = use_state(0)

    # 2. Standard Python event handlers
    def increment():
        set_count(count + 1)

    # 3. Pure Pythonic UI construction
    return div(
        h1(f"Current Count: {count}"),
        p("Clicking the button updates the DOM in milliseconds via WebSockets."),
        button("Increment", on_click=increment, class_name="btn-blue")
    )
```

## Why Choose Pyponent?

* **Pure Python:** Write your frontend and backend in a single language. Say goodbye to context-switching between JavaScript, HTML, and Python.
* **Zero API Boilerplate:** Stop writing throwaway REST endpoints just to update a UI element. Bind browser events directly to your server-side Python functions.
* **Native Real-Time:** Built on WebSockets from the ground up. Live dashboards, multiplayer interactions, and instant state synchronization are practically free.
* **Styling Unbound:** Support for Tailwind CSS. Pass utility classes directly into your components and build beautiful interfaces without fighting the framework.
* **Inherently Secure:** Your application state, database queries, and business logic never leave the server. The browser only receives the exact HTML it needs to render.