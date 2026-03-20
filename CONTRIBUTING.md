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

2. **Install the project** in editable mode with development dependencies:
```bash
uv pip install -e ".[dev]"
```