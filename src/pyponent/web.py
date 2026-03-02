import json
import asyncio
import contextvars
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import uvicorn

from .core import VNode, render_to_string, fire_event, resolve_vdom
from .hooks import Dispatcher, dispatcher_context 

HTML_SHELL_TEMPLATE = """
<!DOCTYPE html>
<html>
    <head>
        <title>{title}</title>
        {meta_tags}
    </head>
    <body>
        <div id="root">{initial_html}</div>
        <script>
            const ws = new WebSocket("ws://" + window.location.host + "/ws");
            
            ws.onmessage = function(event) {
                const activeId = document.activeElement ? document.activeElement.id : null;
                document.getElementById("root").innerHTML = event.data;
                if (activeId) {
                    const el = document.getElementById(activeId);
                    if (el) {
                        el.focus();
                        if (el.value) el.setSelectionRange(el.value.length, el.value.length);
                    }
                }
            };

            ws.onclose = function() {
                console.log("Server disconnected. Waiting for hot reload...");
                const interval = setInterval(function() {
                    fetch("/").then(response => {
                        if (response.ok) {
                            clearInterval(interval);
                            window.location.reload(); 
                        }
                    }).catch(e => { /* still waiting... */ });
                }, 1000);
            };
            
            const trackedEvents = ["click", "input", "change", "keydown", "submit"];
            trackedEvents.forEach(eventType => {
                document.addEventListener(eventType, function(event) {
                    
                    // --- NEW: Intercept Pyponent Router Links ---
                    if (eventType === "click") {
                        const link = event.target.closest('a[data-pyponent-link="true"]');
                        if (link) {
                            event.preventDefault(); // Stop the browser from hard-reloading
                            const newPath = link.getAttribute("href");
                            window.history.pushState({}, "", newPath); // Update the URL bar silently
                            
                            // Send the click event directly to the Link's Python lambda
                            ws.send(JSON.stringify({
                                target_id: link.id,
                                event_name: "onClick",
                                value: newPath
                            }));
                            return; // Exit early so we don't trigger the generic click handler below
                        }
                    }

                    // --- Standard Event Handling ---
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

            // --- NEW: Handle Browser Back/Forward Buttons ---
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
"""

def setup_pyponent(app: FastAPI, root_component, title="Pyponent App", meta_tags=""):
    """Attaches Pyponent's HTML and WebSocket routes to an existing FastAPI app."""
    
    @app.get("/{full_path:path}")
    async def get(full_path: str):
        temp_dispatcher = Dispatcher()
        dispatcher_context.set(temp_dispatcher)
        
        initial_path = "/" + full_path
        root_vnode = VNode(tag=root_component, props={"initial_path": initial_path})
        resolved_vdom = resolve_vdom(root_vnode)
        initial_html = render_to_string(resolved_vdom)
        
        html_content = HTML_SHELL_TEMPLATE.replace("{initial_html}", initial_html)
        html_content = html_content.replace("{title}", title)
        html_content = html_content.replace("{meta_tags}", meta_tags)
        
        return HTMLResponse(html_content)
    
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()
        user_dispatcher = Dispatcher()
        dispatcher_context.set(user_dispatcher)
        latest_resolved_vdom = None

        # 1. Grab the server's main event loop and the user's specific context
        loop = asyncio.get_running_loop()
        ctx = contextvars.copy_context()

        # 2. This is the actual rendering logic
        def sync_render():
            nonlocal latest_resolved_vdom
            root_vnode = VNode(tag=root_component)
            latest_resolved_vdom = resolve_vdom(root_vnode)
            html_str = render_to_string(latest_resolved_vdom)
            
            asyncio.create_task(websocket.send_text(html_str))
            
            current_dispatcher = dispatcher_context.get()
            for effect_callback in current_dispatcher.pending_effects:
                effect_callback()
            current_dispatcher.pending_effects.clear()

        # 3. This is the thread-safe trigger
        def render_loop():
            # No matter what thread calls this, push the render back to the main loop safely!
            loop.call_soon_threadsafe(ctx.run, sync_render)

        user_dispatcher.trigger_render = render_loop
        
        # Initial render 
        ctx.run(sync_render)

        try:
            while True:
                data = await websocket.receive_text()
                event_data = json.loads(data)
                
                target_id = event_data.get("target_id")
                event_name = event_data.get("event_name")
                
                # --- NEW: Intercept Router History (Back/Forward) ---
                if target_id == "system-router" and event_name == "onPopState":
                    def handle_popstate():
                        current_dispatcher = dispatcher_context.get()
                        # If the Router is active, it will have registered 'navigate'
                        if hasattr(current_dispatcher, 'navigate'):
                            current_dispatcher.navigate(event_data.get("value", "/"))
                    
                    # Run the navigation in context so it safely triggers your render_loop!
                    ctx.run(handle_popstate)
                    continue

                # Run normal events safely inside the user's context
                ctx.run(
                    fire_event,
                    latest_resolved_vdom, 
                    target_id, 
                    event_name,
                    event_data
                )
        except Exception:
            pass

def run(target, title="Pyponent App", meta_tags="", host="0.0.0.0", port=8000, reload=False):
    """
    Runs the Pyponent server. 
    """
    print(f"\n🚀 Starting Pyponent Web Server on http://localhost:{port}")
    if reload:
        print("🔄 Hot Reload is ENABLED. Watching for file changes...")
    
    # If target is a string (e.g., 'main:app'), we assume custom API routes are present
    if isinstance(target, FastAPI) or (isinstance(target, str) and "app" in target):
        print("🔗 Hybrid Mode: Custom API routes are active.")
    print("-" * 50 + "\n")

    # --- NEW: Hot Reload Execution ---
    if reload:
        if not isinstance(target, str):
            raise ValueError(
                "⚠️ To use reload=True, you must pass an import string (e.g., 'main:app') "
                "so the reloader can locate your application."
            )
        uvicorn.run(target, host=host, port=port, reload=True)
        return

    # --- Standard Execution ---
    if isinstance(target, FastAPI):
        app = target
    else:
        app = FastAPI()
        setup_pyponent(app, root_component=target, title=title, meta_tags=meta_tags)

    uvicorn.run(app, host=host, port=port)