import json
import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import uvicorn

from .core import VNode, render_to_string, fire_event, resolve_vdom

# Import the Dispatcher class and our new context variable
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
                document.getElementById("root").innerHTML = event.data;
            };
            
            document.addEventListener("click", function(event) {
                if (event.target.id) {
                    ws.send(JSON.stringify({
                        target_id: event.target.id,
                        event_name: "onClick"
                    }));
                }
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
        
        # 1. Create a brand new, empty state manager for THIS connection
        user_dispatcher = Dispatcher()
        
        # 2. Lock it into the context for this specific WebSocket
        dispatcher_context.set(user_dispatcher)
        
        latest_resolved_vdom = None

        def render_loop():
            nonlocal latest_resolved_vdom
            root_vnode = VNode(tag=root_component)
            latest_resolved_vdom = resolve_vdom(root_vnode)
            html_str = render_to_string(latest_resolved_vdom)
            asyncio.create_task(websocket.send_text(html_str))

        user_dispatcher.trigger_render = render_loop
        render_loop() # Initial render

        try:
            while True:
                data = await websocket.receive_text()
                event_data = json.loads(data)
                
                fire_event(
                    latest_resolved_vdom, 
                    event_data.get("target_id"), 
                    event_data.get("event_name")
                )
        except Exception:
            print("Client disconnected.")

    print(f"Starting Pyponent Web Server on http://localhost:{port}")
    uvicorn.run(app, host=host, port=port)