# Core Elements

Pyponent provides a set of pure Python functions that map directly to standard HTML DOM elements. Instead of writing raw HTML strings or JSX, you compose your user interfaces using these functions.

## Importing Elements

All standard HTML elements are available in the `pyponent.html` module. 

```python
from pyponent.html import div, h1, p, span, button, input_, ul, li
```

*(Note: Because `input` is a reserved keyword in Python, the HTML input element is named `input_`).*

## Basic Usage

Every element function accepts child elements as positional arguments and HTML attributes as keyword arguments (`kwargs`).

```python
div(
    h1("Welcome to my App"),
    p("This is a paragraph inside a div.", id="subtitle")
)
```

---

## The "Pythonic" Syntax Sugar

Writing raw HTML in Python can sometimes clash with Python's naming conventions. Pyponent automatically translates standard Python conventions into valid HTML and JavaScript under the hood.

### 1. CSS Classes
Because `class` is a reserved keyword in Python, Pyponent allows you to use `class_name`. This maps perfectly to the HTML `class` attribute (which is incredibly useful for Tailwind CSS).

```python
# Python
button("Submit", class_name="bg-blue-500 text-white font-bold p-2")

# What the browser sees
# <button class="bg-blue-500 text-white font-bold p-2">Submit</button>
```

## Inline Styles

You can pass standard CSS strings directly to any element using the `style` keyword argument. Pyponent will attach it exactly as it would appear in raw HTML.

```python
from pyponent.html import div, p

def AlertBox():
    return div(
        p("Access Denied", style="color: red; font-weight: bold;"),
        style="border: 1px solid red; padding: 10px; background-color: #ffe6e6;"
    )
```

### 2. Event Listeners (`snake_case` to `camelCase`)
JavaScript uses `camelCase` for events (like `onClick` or `onKeyDown`). Python strictly prefers `snake_case`. Pyponent bridges this gap automatically. 

Any keyword argument starting with `on_` is automatically translated and wired up to the WebSocket engine.

```python
def handle_click():
    print("Button was clicked!")

# Use standard Python snake_case
button("Click Me", on_click=handle_click)
```

**Common Events:**
* `on_click` -> `onClick`
* `on_input` -> `onInput`
* `on_change` -> `onChange`
* `on_key_down` -> `onKeyDown`

### 3. Data and Aria Attributes
HTML custom data attributes use hyphens (`data-test-id`), which are invalid in Python kwargs. Pyponent automatically converts underscores to hyphens for any `data_` or `aria_` props.

```python
# Python
div("Content", data_test_id="hero-banner", aria_label="Hero")

# What the browser sees
# <div data-test-id="hero-banner" aria-label="Hero">Content</div>
```

---

## Form Inputs and Event Data

When binding events to inputs (like a user typing in a text box), you often need to read the value they typed. Pyponent automatically passes an `event` dictionary to your handler if your function asks for it!

```python
from pyponent.html import input_, p
from pyponent.hooks import use_state

def NameTag(**props):
    name, set_name = use_state("")

    # Pyponent automatically passes the event payload!
    def update_name(event):
        set_name(event.get("value", ""))

    return div(
        input_(
            type="text", 
            placeholder="Enter your name", 
            value=name, 
            on_input=update_name
        ),
        p(f"Hello, {name}!")
    )
```