import contextvars
import threading
class Dispatcher:
    def __init__(self):
        self.states = {}
        self.hook_indices = {}
        self.current_node_id = None
        self.trigger_render = None
        
        # --- NEW: Effect Tracking ---
        self.effects = {}             # Stores previous dependencies: {node_id: [deps_1, deps_2]}
        self.effect_indices = {}      # Tracks the cursor for effects
        self.pending_effects = []     # A queue of effects to run AFTER the render is complete

    def prepare_render(self, node_id: str):
        self.current_node_id = node_id
        self.hook_indices[node_id] = 0
        self.effect_indices[node_id] = 0 # Reset effect cursor
        
        if node_id not in self.states:
            self.states[node_id] = []
        if node_id not in self.effects:
            self.effects[node_id] = []

dispatcher_context: contextvars.ContextVar[Dispatcher] = contextvars.ContextVar('dispatcher')

def use_state(initial_value):
    dispatcher = dispatcher_context.get()
    node_id = dispatcher.current_node_id
    idx = dispatcher.hook_indices[node_id]
    
    if len(dispatcher.states[node_id]) == idx:
        dispatcher.states[node_id].append(initial_value)
        
    def set_state(new_value):
        dispatcher.states[node_id][idx] = new_value
        if dispatcher.trigger_render:
            dispatcher.trigger_render()
            
    value = dispatcher.states[node_id][idx]
    dispatcher.hook_indices[node_id] += 1
    return value, set_state

# --- NEW: The use_effect hook ---
def use_effect(callback, deps=None):
    dispatcher = dispatcher_context.get()
    node_id = dispatcher.current_node_id
    idx = dispatcher.effect_indices[node_id]

    # If this is the very first render for this effect
    if len(dispatcher.effects[node_id]) == idx:
        dispatcher.effects[node_id].append(deps)
        dispatcher.pending_effects.append(callback)
    else:
        # Compare previous dependencies with the new ones
        prev_deps = dispatcher.effects[node_id][idx]
        
        # If deps is None, it runs every single render.
        # If deps changed, we update the stored deps and queue the effect.
        if deps is None or prev_deps != deps:
            dispatcher.effects[node_id][idx] = deps
            dispatcher.pending_effects.append(callback)

    dispatcher.effect_indices[node_id] += 1

def use_async_effect(callback, deps=None):
    """A custom hook that automatically runs the callback in a background thread."""
    def thread_runner():
        threading.Thread(target=callback).start()
        
    # We pass our thread_runner into the standard use_effect
    use_effect(thread_runner, deps)

