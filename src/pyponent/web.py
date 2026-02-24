import json
import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import uvicorn

from .core import VNode, render_to_string, fire_event, resolve_vdom
from .hooks import Dispatcher, dispatcher_context 

HTML_SHELL = """
<!DOCTYPE html>
<html>
    <head><title>Pyponent App</title></head>
    <body>
        <div id="root">Connecting to Pyponent...</div>
        <script>
            const ws = new WebSocket("ws://" + window.location.host + "/ws");
            
            ws.onmessage = function(event) {
                // Save where the cursor is before we overwrite the HTML
                const activeId = document.activeElement ? document.activeElement.id : null;
                
                document.getElementById("root").innerHTML = event.data;
                
                // Put the cursor back so the user can keep typing!
                if (activeId) {
                    const el = document.getElementById(activeId);
                    if (el) {
                        el.focus();
                        if (el.value) el.setSelectionRange(el.value.length, el.value.length);
                    }
                }
            };
            
            // Listen for clicks AND typing
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

def run(root_component, host="0.0.0.0", port=8000):
    app = FastAPI()

    @app.get("/")
    async def get():
        return HTMLResponse(HTML_SHELL)

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()
        user_dispatcher = Dispatcher()
        dispatcher_context.set(user_dispatcher)
        latest_resolved_vdom = None

        def render_loop():
            nonlocal latest_resolved_vdom
            root_vnode = VNode(tag=root_component)
            latest_resolved_vdom = resolve_vdom(root_vnode)
            html_str = render_to_string(latest_resolved_vdom)
            asyncio.create_task(websocket.send_text(html_str))

        user_dispatcher.trigger_render = render_loop
        render_loop()

        try:
            while True:
                data = await websocket.receive_text()
                event_data = json.loads(data)
                
                # DEBUG PRINT: Watch your terminal to see if the browser is talking to Python!
                print(f"Browser sent: {event_data}")
                
                fire_event(
                    latest_resolved_vdom, 
                    event_data.get("target_id"), 
                    event_data.get("event_name"),
                    event_data # Pass the typing data into the engine
                )
        except Exception:
            print("Client disconnected.")

    print(f"Starting Pyponent Web Server on http://localhost:{port}")
    uvicorn.run(app, host=host, port=port)