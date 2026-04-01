# Native Tailwind CSS (No Node.js)

While Pyponent supports the Tailwind CDN for quick prototyping (`use_tailwind=True`), it is highly recommended to use compiled, native Tailwind CSS for production. 

Thanks to **Tailwind v4** and the `pytailwindcss` package, you can compile lightning-fast, production-ready CSS **without ever installing Node.js or npm**. 

Here is how to set up a pure-Python Tailwind pipeline.

## 1. Install the Compiler

`pytailwindcss` is an official Python wrapper that automatically downloads and runs the standalone Tailwind binary for your operating system.

Install it via `uv` or `pip`:
```bash
uv add pytailwindcss
```

!!! info "Initial Download"
    The first time you use it, run `tailwindcss` in your terminal. It will briefly download the official binary for your machine. Once finished, the command is permanently available.

## 2. Create your Input CSS

Tailwind v4 is completely "CSS-first," meaning you don't need a `tailwind.config.js` file. 

Create a file named `input.css` in your project's root directory. This file imports the Tailwind engine and tells it to scan your Python files for class names:

```css
/* input.css */
@import "tailwindcss";

/* Scan all Python files in this directory and subdirectories */
@source "./**/*.py";
```

## 3. Run the Watch Command

Keep this command running in a separate terminal while you develop. It watches your `.py` files and instantly recompiles your CSS whenever you save.

```bash
tailwindcss -i input.css -o styles/output.css --watch
```

!!! tip "Production Builds"
    When you are ready to deploy, swap `--watch` for `--minify`. This will compress your CSS file to be as tiny as possible:
    `tailwindcss -i input.css -o styles/output.css --minify`

## 4. Link it to Pyponent

Pyponent automatically serves any static files you declare in `header_tags`. Point your framework to the newly generated `styles/output.css` file and disable the CDN.

```python
from fastapi import FastAPI
from pyponent.web import setup_pyponent, run
from components.layout import App

app = FastAPI()

setup_pyponent(
    app, 
    root_component=App, 
    # 1. Mount the compiled CSS
    header_tags=["styles/output.css"], 
    # 2. Disable the CDN
    use_tailwind=False                 
)

if __name__ == "__main__":
    run("main:app", port=8000, reload=True)
```

You are now running a hyper-optimized SPA with native Tailwind CSS, all from a single Python environment!