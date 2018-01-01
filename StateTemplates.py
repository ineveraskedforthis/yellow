class State:
    def Enter(agent):
        pass
    
    def Execute(agent):
        pass
    
    def Exit(agent):
        pass
        
class StateMachine:
    def __init__(self, owner, firststate):
        self.owner = owner
        self.prev_state = 'NONE'
        self.curr_state = firststate
    
    def update(self):
        self.curr_state.Execute(self.owner)

    def change_state(self, new_state):
        self.prev_state = self.curr_state
        self.curr_state.Exit(self.owner)
        self.curr_state = new_state
        self.curr_state.Enter(self.owner)

    def revert(self):
        if self.prev_state != 'NONE':
            self.change_state(self.prev_state)

    def instate(self, qstate):
        return self.curr_state == qstate
