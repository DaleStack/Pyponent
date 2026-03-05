from fastapi import FastAPI
from src.pyponent.web import setup_pyponent, run
from src.pyponent.hooks import use_state
from src.pyponent.html import div, h1, p, button, input_, style_tag

# --- Component 1: The Counter ---
def Counter(**props):
    count, set_count = use_state(0)
    
    return div(
        h1(f"Clicks: {count}", 
           style="margin-top: 0;", 
           class_name="counter-title"),
        button("Increment", 
               onClick=lambda e: set_count(count + 1), 
               style="padding: 10px; margin-right: 10px;"),
        button("Reset", 
               onClick=lambda e: set_count(0)),
        button("Decrement", 
               onClick=lambda e: set_count(count - 1), 
               style="padding: 10px;"),
        style="padding: 20px; border: 2px solid #ddd; border-radius: 8px; margin-bottom: 20px; background: #f9f9f9;"
    )

# --- Component 2: The Live Text Mirror ---
def LiveText(**props):
    text, set_text = use_state("")
    
    return div(
        h1("Typing Test", style="margin-top: 0;"),
        p("Testing", class_name="text-lg font-bold text-yellow-400"),
        p("Type below. The DOM won't refresh, only the text will update!"),
        input_(
            id="live-text-input",
            type="text",
            value=text,
            onInput=lambda e: set_text(e.get("value", "")),
            placeholder="Type something fast...",
            style="padding: 10px; font-size: 16px; width: 100%; box-sizing: border-box;"
        ),
        p("You typed: ", str(text), style="color: #007bff; font-weight: bold; font-size: 1.2em;"),
        button("Clear", onClick=lambda e: set_text(""), style="padding: 10px; margin-top: 10px;"),
        style="padding: 20px; border: 2px solid #ddd; border-radius: 8px; background: #f9f9f9;"
    )

# --- The Root App ---
def App(**props):
    return div(
        style_tag("body { font-family: system-ui, sans-serif; padding: 40px; background: #f0f2f5; }"),
        div(
            h1("🚀 Pyponent Diffing Engine"),
            p("Open your browser's Developer Tools (F12) -> Network tab -> WS (WebSockets).", style="color: #555;"),
            
            # Render our two independent components
            Counter(),
            LiveText(),
            
            style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);"
        )
    )

app = FastAPI()
setup_pyponent(app, 
               App, 
               title="Pyponent Diffing Test",
               use_tailwind=True,
               header_tags=[
                   # Styles
                   "styles/sample.css"
               ])

if __name__ == "__main__":
    run("main:app", port=8000, reload=True)