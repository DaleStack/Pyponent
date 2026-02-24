import json
import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import uvicorn

# Import your core engine (assuming these are in src/pyponent/)
from src.pyponent.core import VNode, render_to_string, fire_event, resolve_vdom
from src.pyponent.hooks import use_state, dispatcher

# --- 1. Your Components (Unchanged!) ---
def Counter(props):
    count, set_count = use_state(0)
    btn_id = props.get("id", "btn") 
    
    return VNode(
        tag="div",
        props={"style": "margin: 10px; padding: 10px; border: 1px solid #ccc;"},
        children=[
            VNode(tag="span", children=[f"Count: {count}  "]),
            VNode(
                tag="button",
                props={"id": btn_id, "onClick": lambda: set_count(count + 1)},
                children=["Add +1"]
            )
        ]
    )

def App():
    return VNode(
        tag="div",
        props={"style": "font-family: sans-serif; padding: 2rem;"},
        children=[
            VNode(tag="h1", children=["Pyponent Web Framework"]),
            VNode(tag=Counter, props={"id": "btn-1"}),
            VNode(tag=Counter, props={"id": "btn-2"}) 
        ]
    )

# --- 2. The FastAPI Server ---
app = FastAPI()

# This is the "Shell" that loads in the browser once.
# It contains a tiny JS script to forward clicks to Python.
HTML_SHELL = """
<!DOCTYPE html>
<html>
    <head><title>Pyponent App</title></head>
    <body>
        <div id="root">Connecting to Pyponent...</div>
        <script>
            const ws = new WebSocket("ws://localhost:8000/ws");
            
            // When Python sends new HTML, update the screen
            ws.onmessage = function(event) {
                document.getElementById("root").innerHTML = event.data;
            };
            
            // When the user clicks anything, send the ID to Python
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

@app.get("/")
async def get():
    return HTMLResponse(HTML_SHELL)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    latest_resolved_vdom = None

    # This replaces our old terminal render loop
    def render_loop():
        nonlocal latest_resolved_vdom
        
        # Resolve the tree and execute components
        root_vnode = VNode(tag=App)
        latest_resolved_vdom = resolve_vdom(root_vnode)
        
        # Convert to HTML string
        html_str = render_to_string(latest_resolved_vdom)
        
        # Send the HTML to the browser!
        # (We use asyncio.create_task because render_loop is called synchronously by use_state)
        asyncio.create_task(websocket.send_text(html_str))

    # Connect the Pyponent dispatcher to our new web render loop
    dispatcher.trigger_render = render_loop
    
    # Trigger the initial render to populate the screen
    render_loop()

    # The Event Loop: Wait for clicks from the browser
    try:
        while True:
            data = await websocket.receive_text()
            event_data = json.loads(data)
            
            target_id = event_data.get("target_id")
            event_name = event_data.get("event_name")
            
            # Find the element in the Python VDOM and execute its lambda
            fire_event(latest_resolved_vdom, target_id, event_name)
            
    except Exception as e:
        print("Client disconnected.")

# --- 3. Run the App ---
if __name__ == "__main__":
    print("Starting Pyponent Server on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)