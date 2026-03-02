# 🚀 Pyponent: The Interactive Tutorial

Welcome to Pyponent! This guide will walk you through building real-time, Server-Driven UIs in pure Python. No JavaScript, no React, no API endpoints required. 

Just write Python functions, and Pyponent handles the WebSockets, state management, and Virtual DOM diffing behind the scenes.

---

## 1. The Basics: Components & Props
In Pyponent, everything is a function that returns HTML elements. We use `**props` to pass data (like text, styles, or user info) into our components.

```python
from src.pyponent.html import div, h1, p

# A reusable component! Always use **props.
def WelcomeCard(**props):
    # Extract data passed from the parent, or use a default
    name = props.get("name", "Guest")
    
    return div(
        h1(f"Hello, {name}!"),
        p("Welcome to your first Pyponent app."),
        style="padding: 20px; border: 1px solid #ccc; border-radius: 8px;"
    )

def App(**props):
    return div(
        WelcomeCard(name="Casey"),
        WelcomeCard() # Will default to "Guest"
    )
```

## 2. Interactivity: State & Events
Need a button to do something? Use the `use_state` hook. When you call the setter function, Pyponent automatically calculates the exact HTML changes and pushes them to the browser instantly over WebSockets.

```python
from src.pyponent.hooks import use_state
from src.pyponent.html import div, h2, button

def Counter(**props):
    # Define a state variable and its updater function
    count, set_count = use_state(0)
    
    return div(
        h2(f"Current Count: {count}"),
        # Pass a lambda function to onClick
        button("Add 1", onClick=lambda e: set_count(count + 1)),
        button("Subtract 1", onClick=lambda e: set_count(count - 1))
    )
```

## 3. Real-Time Forms: The Input Mirror
Because Pyponent uses Granular DOM Diffing, typing into an input box won't destroy the page or make you lose your cursor focus.

⚠️ Golden Rule: Always give your text inputs a hardcoded `id`!

```python
from src.pyponent.hooks import use_state
from src.pyponent.html import div, input_, p

def LiveText(**props):
    text, set_text = use_state("")
    
    return div(
        input_(
            id="my-unique-input", # REQUIRED for text inputs!
            type="text",
            value=text,
            placeholder="Type here...",
            onInput=lambda e: set_text(e.get("value", "")) # Update state on every keystroke
        ),
        p("You are typing: ", text, style="color: blue;")
    )
```

## 4. Background Tasks: Async Effects
If you need to fetch data from a database or run a heavy calculation, you don't want to freeze the UI. Use `use_async_effect` to run Python code in a background thread.

```python
import time
from src.pyponent.hooks import use_state, use_async_effect
from src.pyponent.html import div, ul, li

def TodoList(**props):
    tasks, set_tasks = use_state([])
    is_loading, set_is_loading = use_state(True)
    
    def fetch_from_db():
        time.sleep(1.5) # Simulate a slow database query
        set_tasks(["Learn Python", "Build a Framework", "Celebrate"])
        set_is_loading(False)
        
    # The empty list [] means this only runs ONCE when the component loads
    use_async_effect(fetch_from_db, [])
    
    if is_loading:
        return div("Loading tasks in the background...")
        
    return ul(*[li(task) for task in tasks])
```

## 5. Multi-Page Apps: The Router
Pyponent comes with a built-in Client-Side Router. You can build a Single Page Application (SPA) with zero page reloads.

⚠️ Golden Rule: Use `Link` for navigating inside your app, and `a` for external websites.

```python
from src.pyponent.html import div, h1
from src.pyponent.router import Router, Link

def HomePage(**props):
    return div(h1("Home"), "This is the main page.")

def AboutPage(**props):
    return div(h1("About"), "This is the about page.")

def App(**props):
    return div(
        # Navigation Bar
        div(
            Link(to="/", children=["Home"], style="margin-right: 10px;"),
            Link(to="/about", children=["About"])
        ),
        
        # The Page Content
        Router(
            initial_path=props.get("initial_path", "/"),
            routes={
                "/": HomePage,
                "/about": AboutPage
            }
        )
    )
```

## Running Your App
To serve your Pyponent application, just attach it to a standard FastAPI app:
```python
from fastapi import FastAPI
from src.pyponent.web import setup_pyponent, run
from my_components import App # Import your root component

app = FastAPI()

# Attach Pyponent to FastAPI
setup_pyponent(app, App, title="My Pyponent App")

if __name__ == "__main__":
    # Run with hot-reloading enabled!
    run("main:app", port=8000, reload=True)
```