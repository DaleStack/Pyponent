from fastapi import FastAPI
from src.pyponent.web import setup_pyponent, run
from src.pyponent.html import div, h1, ul, li, span, button, input_, style_tag
from src.pyponent.hooks import use_state

# 1. The custom backend
app = FastAPI()

@app.get("/api/health")
def health_check():
    return {"status": "100% healthy"}

# 2. The UI
def TodoApp(props=None):
    return div(h1("Pyponent To-Do"))

# 3. Attach UI to Backend
setup_pyponent(app, TodoApp, title="My Hybrid App")

if __name__ == "__main__":
    # 4. Let the framework handle the heavy lifting and console output!
    run(app, port=8000)