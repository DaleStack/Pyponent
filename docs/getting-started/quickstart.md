# Quickstart

Let's build your first Pyponent application. Pyponent mounts directly onto [FastAPI](https://fastapi.tiangolo.com/), meaning you can build real-time UIs and standard REST APIs in the exact same codebase.

## 1. Create your Application

Create a single file named `main.py`. This file will initialize your FastAPI app, define your Pyponent UI, and mount them together.

```python
from fastapi import FastAPI
from pyponent.web import setup_pyponent, run
from pyponent.html import div, h1, p, button
from pyponent.hooks import use_state

# 1. Initialize your standard FastAPI application
app = FastAPI()

# 2. Define your interactive Pyponent components
def Counter(**props):
    count, set_count = use_state(0)

    def increment(): set_count(count + 1)
    def decrement(): set_count(count - 1)

    return div(
        button("-", on_click=decrement, class_name="p-2 bg-red-500 text-white rounded"),
        p(f"Current Count: {count}", class_name="text-xl font-bold my-4"),
        button("+", on_click=increment, class_name="p-2 bg-blue-500 text-white rounded")
    )

def App(**props):
    return div(
        h1("Hello World!", class_name="text-3xl font-bold"),
        p("This is a simple Pyponent app mounted on FastAPI."),
        Counter()
    )

# 3. Mount Pyponent's WebSocket and HTML routes onto the FastAPI app
setup_pyponent(
    app, 
    root_component=App, 
    title="Simple Pyponent App",
    use_tailwind=True
)

if __name__ == "__main__":
    # 4. Start the server with hot-reload enabled!
    run("main:app", port=8000, reload=True)
```

## 2. Run the Server

Start the application directly from your terminal:

```bash
uv run main.py
```

You will see Pyponent boot up in your terminal:
```bash
🚀 Starting Pyponent Web Server on http://localhost:8000
🔄 Hot Reload is ENABLED. Watching for file changes...
🔗 Hybrid Mode: Custom API routes are active.
🎨 Tailwind CSS: CDN
--------------------------------------------------
```

Open `http://localhost:8000` in your browser. Click the buttons and watch the state update instantly over WebSockets!