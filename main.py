from fastapi import FastAPI
from src.pyponent.web import setup_pyponent, run
from src.pyponent.html import div, h1, ul, li, span, button, input_, style_tag
from src.pyponent.hooks import use_state, use_async_effect
import time

app = FastAPI()

@app.get("/api/health")
def health_check():
    return {"status": "100% healthy"}

def TodoApp(props=None):
    props = props or {}
    
    # 1. State
    tasks, set_tasks = use_state([])              # Starts empty!
    is_loading, set_is_loading = use_state(True)  # Starts in a loading state
    current_task, set_current_task = use_state("")

    # 2. The Database Fetch Effect
    def fetch_tasks_from_db():
        # Simulate a slow 1.5 second database query
        time.sleep(1.5)
        set_tasks(["Build a Python framework", "Celebrate"])
        set_is_loading(False) # Turn off the loading spinner

    # Run ONCE on mount (empty dependency array [])
    use_async_effect(fetch_tasks_from_db, [])

    # ... (Keep your add_task and delete_task logic the same) ...
    def add_task():
        if current_task.strip():
            set_tasks(tasks + [current_task.strip()])
            set_current_task("")

    def delete_task(index_to_delete):
        new_tasks = [t for i, t in enumerate(tasks) if i != index_to_delete]
        set_tasks(new_tasks)

    # 3. Render
    return div(
        # ... (Keep your style_tag exactly the same) ...
        
        div(
            h1("Pyponent To-Do", class_name="header"),
            
            # Input Area
            div(
                input_(
                    id="new-task-input", 
                    type="text",
                    placeholder="What needs to be done?",
                    value=current_task,
                    onInput=lambda e: set_current_task(e.get("value", "")),
                    class_name="task-input"
                ),
                button("Add", onClick=add_task, class_name="add-btn"),
                class_name="input-group"
            ),
            
            # Conditional Rendering: Show a loader OR the list
            div("Loading tasks from database...", style="text-align: center; color: #888;") 
            if is_loading else 
            ul(
                *[
                    li(
                        span(task),
                        button("Delete", onClick=lambda e, idx=i: delete_task(idx), class_name="delete-btn"),
                        class_name="task-item"
                    )
                    for i, task in enumerate(tasks)
                ],
                class_name="task-list"
            ),
            
            class_name="container"
        )
    )

setup_pyponent(app, TodoApp, title="My pyponent App")

if __name__ == "__main__":
    # FIX: Pass the import string and enable reload!
    run("main:app", port=8000, reload=True)