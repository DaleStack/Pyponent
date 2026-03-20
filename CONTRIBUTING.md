# Contributing to Pyponent

First off, thank you for considering contributing to Pyponent! It's people like you that make Pyponent a great tool for the Python community. 

This document outlines the process for contributing to the project to ensure a smooth experience for everyone.

## 🏗️ Local Development Setup

To get your local environment set up for hacking on Pyponent, we use **[uv](https://github.com/astral-sh/uv)** for lightning-fast virtual environments and dependency resolution.

1. **Fork the repository** on GitHub and clone your fork locally:
```bash
git clone [https://github.com/](https://github.com/)<your-username>/pyponent.git
cd pyponent
```

2. **Create a virtual environment** using `uv` and activate it:
```bash
uv venv
source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
```

3. **Install the project** in editable mode with development dependencies:
```bash
uv pip install -e ".[dev]"
```

## 🗺️ Project Architecture
If you are looking to fix a bug or add a feature, here is a quick map of the codebase:

- `core.py`: The heart of the Virtual DOM (`VNode`) and component resolution.

- `diff.py`: The diffing engine that compares old and new VNodes.

- `html.py`: The element generator. (Note: We translate Pythonic `snake_case` props like `on_click` to JavaScript `camelCase` here!)

- `hooks.py`: Client-side state management (`use_state`, etc.).

## ✅ The Workflow (Before you open a PR)
Before submitting a Pull Request, please ensure your code passes our quality checks. GitHub Actions will run these automatically, but checking locally saves time!

1. **Run the Linters & Formatters (Ruff)**:
We use Ruff for blazing-fast formatting and linting.
```bash
ruff format .
ruff check . --fix
```

2. **Run the Test Suite**:
Make sure you haven't broken the diffing engine or existing components.
```bash
pytest .
```

## 🚀 Opening a Pull Request
1. Create a new branch for your feature or bugfix: `git checkout -b feature/my-awesome-feature`

2. Commit your changes with a descriptive message.

3. Push your branch to your fork: `git push origin feature/my-awesome-feature`

4. Open a Pull Request against the `main` branch of the original Pyponent repository.

5. Fill out the PR template provided.

### **Thank you for helping make Pyponent better!** 🐍✌️
