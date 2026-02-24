from fastapi import FastAPI
from src.pyponent.web import setup_pyponent, run
from src.pyponent.html import div, h1, ul, li, span, button, input_, style_tag
from src.pyponent.hooks import use_state

app = FastAPI()

@app.get("/api/health")
def health_check():
    return {"status": "100% healthy"}

def TodoApp(props=None):
    return div(h1("testing only hahahha!")) # Try changing this text!

setup_pyponent(app, TodoApp, title="My pyponent App")

if __name__ == "__main__":
    # FIX: Pass the import string and enable reload!
    run("main:app", port=8000, reload=True)