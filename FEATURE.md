# Pyponent Features & Architecture

Pyponent is an experimental, Server-Driven UI (SDUI) framework built in pure Python. It combines the declarative component model of React with the WebSocket-driven state management of Phoenix LiveView, all running on top of FastAPI.

## Core Engine
* **Virtual DOM**: A lightweight Python representation of HTML elements (`VNode`) that recursively resolves into raw HTML strings.
* **Context-Aware Dispatcher**: Uses Python's `contextvars` to isolate user sessions and securely map state/events to specific component instances.
* **Auto-Generated DOM IDs**: The framework automatically generates unique `uuid` strings for elements with event listeners, abstracting DOM management away from the developer.

## UI & Reactivity
* **Hyperscript Syntax**: Build semantic HTML purely in Python using composable functions (`div`, `h1`, `ul`, `li`, `input_`, `button`).
* **State Management (`use_state`)**: React-style state hooks. Updating state automatically triggers a re-render of the component and diffs the UI over WebSockets.
* **Real-time Event Handling**: Two-way data binding. Browser events (`onClick`, `onInput`) are captured by a lightweight JS shell, serialized, and beamed to Python lambdas instantly.
* **Focus-Stable Inputs**: Support for hardcoded IDs on text inputs to ensure the user's cursor never drops during a WebSocket re-render.
* **CSS-in-Python**: Full support for `class_name` attribute mapping and dynamic `<style>` tag injection for scoped component styling.
* **Dynamic Array Rendering**: Unpack Python list comprehensions directly into UI nodes (e.g., rendering lists of database items) while preserving state integrity.

## Lifecycle & Side Effects
* **Effect Hook (`use_effect`)**: React-style lifecycle hook with dependency array tracking. Supports running logic on mount, on every render, or when specific state variables change.
* **Asynchronous Effects (`use_async_effect`)**: A custom hook that automatically wraps long-running side effects (like database queries or API calls) in a background `threading.Thread`. This prevents blocking the main server thread, keeping the WebSocket completely responsive during heavy backend operations.

## Architecture & Server
* **Hybrid FastAPI Plugin**: Pyponent doesn't hijack the server. Using `setup_pyponent`, developers can attach the UI engine to an existing FastAPI application alongside standard JSON REST APIs.
* **Server-Side Rendering (SSR)**: The initial HTTP `GET` request fully renders the UI tree to HTML on the server. This guarantees instant First Contentful Paint (FCP) and perfect SEO before the WebSocket hydrates the page.
* **Custom SEO & Metadata**: Inject custom `<title>` and `<meta>` tags into the document `<head>` during the SSR phase.

## Developer Experience (DX)
* **Rust-Powered Hot Reloading**: Integrated with `uvicorn` and `watchfiles`. Saving a `.py` file instantly restarts the backend server.
* **Frontend Auto-Recovery**: The JavaScript shell detects server disconnects during a hot-reload and automatically pings the server to trigger a seamless browser refresh.
* **Clean Terminal Output**: The framework intercepts standard startup logs to provide formatted, clickable local URLs for both the UI and the underlying API.

---
### Roadmap (Coming Soon)
* Multi-page Routing without full browser reloads.
* Granular Virtual DOM Diffing (sending only changed HTML chunks over the WebSocket instead of the full tree).