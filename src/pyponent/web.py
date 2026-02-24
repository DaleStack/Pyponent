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
            // ... (Keep all your existing JavaScript exactly the same!) ...
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
            
            const trackedEvents = ["click", "input", "change", "keydown", "submit"];
            trackedEvents.forEach(eventType => {
                document.addEventListener(eventType, function(event) {
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
        </script>
    </body>
</html>
"""

def setup_pyponent(app: FastAPI, root_component, title="Pyponent App", meta_tags=""):
    """Attaches Pyponent's HTML and WebSocket routes to an existing FastAPI app."""
    
    @app.get("/")
    async def get():
        temp_dispatcher = Dispatcher()
        dispatcher_context.set(temp_dispatcher)
        
        root_vnode = VNode(tag=root_component)
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
                
                # Run events safely inside the user's context
                ctx.run(
                    fire_event,
                    latest_resolved_vdom, 
                    event_data.get("target_id"), 
                    event_data.get("event_name"),
                    event_data
                )
        except Exception:
            pass

def run(target, title="Pyponent App", meta_tags="", host="0.0.0.0", port=8000):
    """
    Runs the Pyponent server. 
    'target' can be a Pyponent Component, OR a pre-configured FastAPI app.
    """
    # 1. Did the user pass a custom FastAPI app, or just a UI component?
    if isinstance(target, FastAPI):
        app = target
    else:
        app = FastAPI()
        setup_pyponent(app, root_component=target, title=title, meta_tags=meta_tags)

    # 2. The Framework handles the Developer Experience (DX)!
    print(f"\n🚀 Starting Pyponent Web Server on http://localhost:{port}")
    if isinstance(target, FastAPI):
        print("🔗 Hybrid Mode: Custom API routes are active.")
    print("-" * 50 + "\n")
    
    # 3. Start the server
    uvicorn.run(app, host=host, port=port)