import sqlite3
import time
from src.pyponent.core import VNode
from src.pyponent.hooks import use_state, use_async_effect
from src.pyponent.web import run

# --- 1. Database Setup (Just for this example) ---
def setup_database():
    conn = sqlite3.connect("users.db")
    conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, role TEXT)")
    
    # Insert a dummy user if the table is empty
    if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        conn.execute("INSERT INTO users (name, role) VALUES ('Grace Hopper', 'System Architect')")
        conn.commit()
    conn.close()


# --- 2. Your Pyponent Component ---
def UserDashboard(props):
    user, set_user = use_state(None)
    is_loading, set_is_loading = use_state(True)

    def fetch_from_db():
        # Do heavy database stuff here
        time.sleep(1) 
        set_user({"name": "Grace Hopper", "role": "System Architect"})
        set_is_loading(False)

    # MAGIC! So clean.
    use_async_effect(fetch_from_db, [])

    if is_loading:
        return VNode(tag="div", children=["Connecting to SQLite..."])

    return VNode(tag="div", children=[f"Hello, {user['name']}"])

# --- 4. The App Entry Point ---
def App():
    return VNode(
        tag="div",
        props={"style": "font-family: sans-serif; padding: 2rem;"},
        children=[
            VNode(tag="h1", children=["SQLite + Pyponent"]),
            VNode(tag=UserDashboard)
        ]
    )

if __name__ == "__main__":
    setup_database()
    run(App, port=8000)