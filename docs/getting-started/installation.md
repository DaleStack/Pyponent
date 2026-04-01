# Installation

Getting Pyponent up and running takes less than a minute. Because Pyponent comes pre-packaged with a lightning-fast ASGI server, you only need to install a single package.

---

## Prerequisites

Pyponent requires **Python 3.8** or higher. 

We highly recommend using a virtual environment to keep your project dependencies isolated. 

## The Recommended Way (Using `uv`)

For the best developer experience, we recommend using [uv](https://github.com/astral-sh/uv) by Astral. It is a wildly fast Python package installer and resolver written in Rust.

**1. Create and activate a virtual environment:**
```bash
uv venv
source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
```

**2. Install Pyponent:**
```bash
uv add pyponent
```

!!! tip "Batteries Included"
    When you install `pyponent`, it automatically installs **FastAPI** and **Uvicorn** under the hood. You don't need to manage web server dependencies separately—Pyponent has everything it needs to run out of the box.

---

## The Standard Way (Using `pip`)

If you prefer to stick with the standard Python toolchain, you can use the built-in `venv` and `pip` modules.

**1. Create and activate a virtual environment:**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
```

**2. Install Pyponent:**
```bash
pip install pyponent
```

---

## Verifying the Installation

To verify that Pyponent was installed successfully, you can run a quick check in your terminal:

```bash
python -c "import pyponent; print('Pyponent is ready!')"
```

If it prints `Pyponent is ready!` without any errors, you are completely set up!

!!! success "Next Steps"
    Now that your environment is ready, head over to the [Quickstart](quickstart.md) guide to build your very first Server-Driven UI component.