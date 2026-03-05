# Pyponent

**Pyponent** is a blazing-fast, Server-Driven UI (SDUI) framework for Python. It allows you to build highly interactive, real-time Single Page Applications (SPAs) entirely in Python—without writing a single line of JavaScript, HTML, or CSS (unless you want to).

Powered by **FastAPI** and **WebSockets**, Pyponent manages state on the server, calculates Virtual DOM diffs in pure Python, and surgically updates the browser using granular JSON patches. 

---

## Why was Pyponent made?
Modern web development often requires massive context switching. To build a dynamic web app, developers usually have to write Python for the backend, design APIs, configure Webpack/Vite, and write JavaScript/React for the frontend. 

**Pyponent was built to eliminate the frontend build step.** It is designed for Python developers who want to build complex, interactive dashboards and tools at the speed of thought, keeping their data, state, and UI logic perfectly synced in one unified codebase.



---

## Pros and Cons

### Pros
* **Zero JavaScript:** Build modals, interactive forms, and real-time dashboards using pure Python.
* **Granular DOM Diffing:** Unlike older frameworks that reload the whole page, Pyponent sends tiny JSON patches over WebSockets, preserving cursor focus and scrolling.
* **Built-in SPA Routing:** Includes a client-side router (`Router` and `Link`) for instant, zero-refresh page navigation.
* **Native Tailwind Support:** Turn on Tailwind CSS with a single boolean flag.
* **Secure by Default:** Because state lives on the server, sensitive business logic and API keys are never exposed to the browser.

### Cons
* **Requires Always-On Connection:** Pyponent relies entirely on WebSockets. It does not work offline.
* **Network Latency:** Every button click travels to the server and back. It is incredibly fast, but not suited for high-frequency client-side animations (like 60fps drag-and-drop or WebGL games).
* **State Management Scale:** Because the server holds the state for every connected user, massive applications with millions of concurrent users will require careful load balancing.

---

## How it Works



1. **Initial Load:** You define components in Python. Pyponent renders them to a static HTML string and sends it to the browser.
2. **WebSocket Connection:** The browser connects back to the FastAPI server via WebSockets.
3. **Interactivity:** When a user clicks a button or types in an input, the browser sends a tiny JSON event `{"event_name": "onClick", "target_id": "btn-1"}` to the server.
4. **Reconciliation:** Python updates the state, rebuilds the Virtual DOM in memory, and calculates the exact differences.
5. **Patching:** Python sends a surgical JSON patch back to the browser, updating only the elements that changed.

---

## Installation & Quick Start

*(Note: Pyponent is designed to run alongside Uvicorn and FastAPI).*

```bash
pip install pyponent fastapi uvicorn