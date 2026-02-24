class Dispatcher:
    def __init__(self):
        self.states = {}
        self.hook_indices = {}
        self.current_node_id = None
        self.trigger_render = None

    def prepare_render(self, node_id: str):
        """Called by the framework right before executing a component."""
        self.current_node_id = node_id
        self.hook_indices[node_id] = 0
        
        # Initialize state list for this exact instance if new
        if node_id not in self.states:
            self.states[node_id] = []

dispatcher = Dispatcher()

def use_state(initial_value):
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