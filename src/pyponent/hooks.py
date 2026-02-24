import contextvars

class Dispatcher:
    def __init__(self):
        self.states = {}
        self.hook_indices = {}
        self.current_node_id = None
        self.trigger_render = None

    def prepare_render(self, node_id: str):
        self.current_node_id = node_id
        self.hook_indices[node_id] = 0
        if node_id not in self.states:
            self.states[node_id] = []

# MAGIC: This variable is automatically isolated per-websocket connection!
dispatcher_context: contextvars.ContextVar[Dispatcher] = contextvars.ContextVar('dispatcher')

def use_state(initial_value):
    # Retrieve the dispatcher for THIS specific user/tab
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