from src.pyponent.hooks import use_state
from src.pyponent.web import run
from src.pyponent.html import div, h1, span, input_, button, component, style_tag


def TodoApp(props=None):
    props = props or {}
    
    # 1. State for the list of tasks, and state for the current typing box
    tasks, set_tasks = use_state(["Build a Python framework", "Celebrate"])
    current_task, set_current_task = use_state("")

    # 2. Add Task Logic
    def add_task():
        if current_task.strip():
            # We create a new list with the appended task to trigger state change properly
            set_tasks(tasks + [current_task.strip()])
            set_current_task("") # Clear the input box

    # 3. Delete Task Logic
    def delete_task(index_to_delete):
        # Filter out the task at the given index
        new_tasks = [t for i, t in enumerate(tasks) if i != index_to_delete]
        set_tasks(new_tasks)

    return div(
        # Injecting our scoped CSS
        style_tag("""
            body { background: #f0f2f5; margin: 0; }
            .container { max-width: 450px; margin: 50px auto; font-family: sans-serif; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            .header { text-align: center; color: #333; }
            .input-group { display: flex; gap: 10px; margin-bottom: 20px; }
            .task-input { flex: 1; padding: 10px; border: 1px solid #ccc; border-radius: 4px; font-size: 16px; }
            .add-btn { padding: 10px 15px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; }
            .add-btn:hover { background: #0056b3; }
            .task-list { display: flex; flex-direction: column; gap: 10px; }
            .task-item { display: flex; justify-content: space-between; align-items: center; padding: 10px; background: #f9f9f9; border-radius: 4px; border: 1px solid #eee; }
            .delete-btn { background: #dc3545; color: white; border: none; border-radius: 4px; padding: 6px 10px; cursor: pointer; }
            .delete-btn:hover { background: #c82333; }
        """),
        
        div(
            h1("Pyponent To-Do", class_name="header"),
            
            # --- The Input Area ---
            div(
                input_(
                    id="new-task-input", # MANDATORY MANUAL ID FOR TYPING!
                    type="text",
                    placeholder="What needs to be done?",
                    value=current_task,
                    onInput=lambda e: set_current_task(e.get("value", "")),
                    class_name="task-input",
                ),
                button("Add", onClick=add_task, class_name="add-btn"),
                class_name="input-group"
            ),
            
            # --- The Dynamic Array Rendering ---
            div(
                # We unpack a list comprehension of divs!
                *[
                    div(
                        span(task),
                        # Notice `idx=i`! This is a classic Python lambda loop gotcha.
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

if __name__ == "__main__":
    run(TodoApp, port=8000)