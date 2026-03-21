import asyncio
import contextvars
import json
from pathlib import Path

import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse, HTMLResponse

from .core import VNode, fire_event, render_to_string, resolve_vdom
from .hooks import Dispatcher, dispatcher_context

# header_tags processor


def _process_header_tags(header_tags, app: FastAPI) -> str:
    """
    Accepts a str or list[str]. Each item is either:
      - A raw HTML tag string  -> used as-is
      - A path ending in .css  -> served as a static file and converted to
                                  <link rel="stylesheet" href="/__pyponent_css__/filename.css">

    Returns a single string ready to be dropped into <head>.
    """  # noqa: E501
    if not header_tags:
        return ""

    items = [header_tags] if isinstance(header_tags, str) else list(header_tags)

    resolved = []
    for item in items:
        item = item.strip()
        if item.endswith(".css") and not item.startswith("<"):
            css_path = Path(item)
            if not css_path.exists():
                raise FileNotFoundError(
                    f"Pyponent CSS: file not found: '{item}'. "
                    "Pass the path relative to where you run the server."
                )
            route_url = f"/__pyponent_css__/{css_path.name}"
            _register_css_route(app, route_url, str(css_path.resolve()))
            resolved.append(f'<link rel="stylesheet" href="{route_url}">')
        else:
            resolved.append(item)

    return "\n        ".join(resolved)


def _register_css_route(app: FastAPI, route_url: str, file_path: str):
    """Adds a GET route that serves the given CSS file, if not already registered."""
    if any(r.path == route_url for r in app.routes):
        return

    @app.get(route_url)
    async def serve_css(fp=file_path):
        return FileResponse(fp, media_type="text/css")


# HTML shell

HTML_SHELL_TEMPLATE = """\
<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        {header_tags}
    </head>
    <body>
        <div id="root">{initial_html}</div>
        <script>
            const ws = new WebSocket("ws://" + window.location.host + "/ws");

            ws.onmessage = function(event) {
                const payload = JSON.parse(event.data);

                if (payload.type === "full") {
                    document.getElementById("root").innerHTML = payload.html;
                }
                else if (payload.type === "patch") {
                    payload.patches.forEach(patch => {
                        const el = document.getElementById(patch.id);
                        if (!el) return;

                        if (patch.type === "replace") {
                            el.outerHTML = patch.html;
                        } else if (patch.type === "inner_html") {
                            el.innerHTML = patch.html;
                        } else if (patch.type === "props") {
                            for (const [key, value] of Object.entries(patch.props)) {
                                if (key === "class_name") el.className = value;
                                else if (key === "value") el.value = value;
                                else if (key !== "onClick" && key !== "onInput") el.setAttribute(key, value);
                            }
                        }
                    });
                }
                
                // --- THE MAGIC URL SYNC ---
                // After the DOM is fully updated, check if the server rendered a new URL
                const routerWrapper = document.getElementById("pyponent-router-wrapper");
                if (routerWrapper) {
                    // Note: We look for the hyphenated HTML attribute here!
                    const serverUrl = routerWrapper.getAttribute("data-pyponent-url");
                    if (serverUrl && window.location.pathname !== serverUrl) {
                        window.history.pushState({}, "", serverUrl);
                    }
                }
            };

            ws.onclose = function() {
                console.log("Server disconnected. Waiting for hot reload...");
                const interval = setInterval(function() {
                    fetch("/").then(response => {
                        if (response.ok) { clearInterval(interval); window.location.reload(); }
                    }).catch(e => {});
                }, 1000);
            };

            const trackedEvents = ["click", "input", "change", "keydown", "submit"];
            trackedEvents.forEach(eventType => {
                document.addEventListener(eventType, function(event) {

                    if (eventType === "click") {
                        const link = event.target.closest('a[data-pyponent-link="true"]');
                        if (link) {
                            event.preventDefault();
                            const newPath = link.getAttribute("href");
                            window.history.pushState({}, "", newPath);
                            ws.send(JSON.stringify({
                                target_id: "system-router", // We route the click directly to the system router
                                event_name: "onPopState",
                                value: newPath
                            }));
                            return;
                        }
                    }

                    if (event.target.id) {
                        if (eventType === "submit") event.preventDefault();
                        const eventName = "on" + eventType.charAt(0).toUpperCase() + eventType.slice(1);
                        ws.send(JSON.stringify({
                            target_id: event.target.id,
                            event_name: eventName,
                            value: event.target.value || "",
                            key: event.key || ""
                        }));
                    }
                });
            });

            window.addEventListener("popstate", function(event) {
                ws.send(JSON.stringify({
                    target_id: "system-router",
                    event_name: "onPopState",
                    value: window.location.pathname
                }));
            });
        </script>
    </body>
</html>
"""  # noqa: E501


# setup_pyponent


def setup_pyponent(
    app: FastAPI,
    root_component,
    title: str = "Pyponent App",
    header_tags=None,
    use_tailwind: bool = False,
):
    """
    Attaches Pyponent's HTML and WebSocket routes to an existing FastAPI app.

    Parameters
    ----------
    app            : FastAPI instance.
    root_component : Root Pyponent component function.
    title          : Browser tab title.
    header_tags    : str or list[str] injected into <head>.
                     Raw HTML tag strings are used as-is.
                     Bare .css file paths are auto-served and converted to
                     <link rel="stylesheet"> tags automatically.

                     Examples::

                         header_tags=[
                             '<meta name="description" content="My app">',
                             '<meta property="og:title" content="My app">',
                             '<link rel="icon" href="/favicon.ico">',
                             "styles/main.css",
                         ]

    use_tailwind   : Inject the Tailwind CSS CDN script into <head>.
                     Use class_name="..." on any element to apply Tailwind classes.
    """
    resolved_header = _process_header_tags(header_tags, app)

    if use_tailwind:
        tw_tag = '<script src="https://cdn.tailwindcss.com"></script>'
        resolved_header = (
            (resolved_header + "\n        " + tw_tag).strip()
            if resolved_header
            else tw_tag
        )

    def _render_shell(initial_html: str) -> str:
        html = HTML_SHELL_TEMPLATE
        html = html.replace("{initial_html}", initial_html)
        html = html.replace("{title}", title)
        html = html.replace("{header_tags}", resolved_header)
        return html

    @app.get("/{full_path:path}")
    async def get(full_path: str):
        temp_dispatcher = Dispatcher()
        dispatcher_context.set(temp_dispatcher)

        initial_path = "/" + full_path
        root_vnode = VNode(tag=root_component, props={"initial_path": initial_path})
        resolved_vdom = resolve_vdom(root_vnode)
        initial_html = render_to_string(resolved_vdom)

        return HTMLResponse(_render_shell(initial_html))

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()
        user_dispatcher = Dispatcher()
        dispatcher_context.set(user_dispatcher)
        latest_resolved_vdom = None

        loop = asyncio.get_running_loop()
        ctx = contextvars.copy_context()

        def sync_render():
            nonlocal latest_resolved_vdom

            root_vnode = VNode(tag=root_component)
            new_vdom = resolve_vdom(root_vnode)

            if latest_resolved_vdom is None:
                html_str = render_to_string(new_vdom)
                asyncio.create_task(
                    websocket.send_json({"type": "full", "html": html_str})
                )
            else:
                from .diff import diff_vdom

                patches = diff_vdom(latest_resolved_vdom, new_vdom)
                if patches:
                    asyncio.create_task(
                        websocket.send_json({"type": "patch", "patches": patches})
                    )

            latest_resolved_vdom = new_vdom

            current_dispatcher = dispatcher_context.get()
            for effect_callback in current_dispatcher.pending_effects:
                effect_callback()
            current_dispatcher.pending_effects.clear()

        def render_loop():
            loop.call_soon_threadsafe(ctx.run, sync_render)

        user_dispatcher.trigger_render = render_loop
        ctx.run(sync_render)

        try:
            while True:
                data = await websocket.receive_text()
                event_data = json.loads(data)

                target_id = event_data.get("target_id")
                event_name = event_data.get("event_name")

                if target_id == "system-router" and event_name == "onPopState":

                    def handle_popstate():
                        current_dispatcher = dispatcher_context.get()
                        if hasattr(current_dispatcher, "navigate"):
                            current_dispatcher.navigate(event_data.get("value", "/"))

                    ctx.run(handle_popstate)
                    continue

                ctx.run(
                    fire_event,
                    latest_resolved_vdom,
                    target_id,
                    event_name,
                    event_data,
                )
        except Exception:
            pass


# run


def run(
    target,
    title: str = "Pyponent App",
    header_tags=None,
    use_tailwind: bool = False,
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = False,
):
    """
    Runs the Pyponent server.

    Parameters
    ----------
    target       : FastAPI instance, import string, or root component function.
    title        : Browser tab title.
    header_tags  : str or list[str] injected into <head>.
                   Bare .css paths -> auto-served + converted to <link> tags.
                   Raw HTML strings -> used as-is (SEO meta, OG tags, fonts...).
    use_tailwind : Inject the Tailwind CSS CDN into <head>.
    host / port  : Bind address.
    reload       : Uvicorn hot-reload (requires target as an import string).
    """
    print(f"\n🚀 Starting Pyponent Web Server on http://localhost:{port}")
    if reload:
        print("🔄 Hot Reload is ENABLED. Watching for file changes...")
    if use_tailwind:
        print("🎨 Tailwind CSS: CDN")
    if isinstance(target, FastAPI) or (isinstance(target, str) and "app" in target):
        print("🔗 Hybrid Mode: Custom API routes are active.")
    print("-" * 50 + "\n")

    if reload:
        if not isinstance(target, str):
            raise ValueError(
                "To use reload=True, pass an import string (e.g. 'main:app') "
                "so the reloader can locate your application."
            )
        uvicorn.run(target, host=host, port=port, reload=True)
        return

    if isinstance(target, FastAPI):
        app = target
    else:
        app = FastAPI()
        setup_pyponent(
            app,
            root_component=target,
            title=title,
            header_tags=header_tags,
            use_tailwind=use_tailwind,
        )

    uvicorn.run(app, host=host, port=port)
