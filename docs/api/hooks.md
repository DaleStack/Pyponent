# State Management & Effects

In Pyponent, components are not just static HTML generators—they are fully reactive. You can manage memory with `use_state`, and handle side effects (like fetching data or setting timers) using `use_effect` and `use_async_effect`.

---

## `use_state`

The `use_state` function allows you to add stateful memory to your Python components. 

Because Pyponent is a Server-Driven UI framework, **this state lives securely in your server's RAM**, tied directly to the user's specific WebSocket connection via Python `contextvars`. 

### Basic Syntax

```python
from pyponent.hooks import use_state

value, set_value = use_state(initial_value)
```

`use_state` returns a tuple with exactly two items:
1. **The current state:** The value as it exists right now.
2. **The setter function:** A function you call to update the value and trigger a UI re-render.

---

## `use_effect`

Sometimes you need your component to do something *after* it renders, like synchronizing with an external system, setting up a timer, or logging data. 

`use_effect` takes a callback function and an optional list of dependencies (`deps`).

```python
from pyponent.hooks import use_effect, use_state

def LoggerComponent(**props):
    count, set_count = use_state(0)

    def log_to_console():
        print(f"The component rendered, and count is now {count}")

    # This runs every time 'count' changes
    use_effect(log_to_console, deps=[count])
    
    # ... render UI ...
```

### The Dependency Array (`deps`)
* **`deps=None`** (Default): The effect runs after *every single render*.
* **`deps=[]`** (Empty List): The effect runs exactly once when the component first mounts.
* **`deps=[variable]`**: The effect runs only when the variables in the list have changed since the last render.

---

## `use_async_effect` (Background Tasks)

This is one of Pyponent's most powerful features. 

If you need to perform a heavy task—like querying a database, calling an external API, or running a machine learning model—you do not want to freeze the user's UI. 

`use_async_effect` automatically spawns a Python background thread for your callback. Because Pyponent's event loop is thread-safe, you can safely call your `set_state` functions from inside this background thread to update the UI when the task is done!

### Example: Fetching Data without Freezing
Notice how the UI renders a "Loading..." message instantly, and then seamlessly updates once the heavy background task is complete.

```python
import time
from pyponent.html import div, h1, p, button
from pyponent.hooks import use_state, use_async_effect

def DataDashboard(**props):
    # 1. Set up our state
    data, set_data = use_state(None)
    is_loading, set_is_loading = use_state(True)

    # 2. Define a heavy, long-running function
    def fetch_heavy_data():
        set_is_loading(True)
        
        # Simulate a 3-second database query or API call
        time.sleep(3) 
        
        # Safely update the state from the background thread!
        set_data({"users_online": 42, "status": "Healthy"})
        set_is_loading(False)

    # 3. Fire the effect exactly once when the component mounts
    use_async_effect(fetch_heavy_data, deps=[])

    # 4. Render the UI (this happens immediately, without waiting for the sleep!)
    if is_loading:
        return div(
            h1("Dashboard"),
            p("Fetching data from the database...", class_name="animate-pulse text-gray-500")
        )

    return div(
        h1("Dashboard"),
        p(f"System Status: {data['status']}"),
        p(f"Users Online: {data['users_online']}"),
        button("Refresh Data", on_click=fetch_heavy_data, class_name="bg-blue-500 text-white p-2")
    )
```

!!! success "Thread-Safe by Design"
    You never have to worry about `asyncio` loop conflicts or Thread locks. Pyponent's WebSocket engine handles cross-thread DOM diffing automatically.