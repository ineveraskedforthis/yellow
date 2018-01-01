from StateTemplates import *

class FightIdle(State):
    def Execute(agent):
        agent.change_state(FightStarts)

class FightStarts(State):
    def Enter(agent):
        agent.set_flags()

    def Execute(agent):
        agent.change_state(FightRound)

class FightRound(State):
    def Execute(agent):
        agent.melee_clash()
        if agent.battle_over:
            agent.change_state(FightEnd)

class FightEnd(State):
    def Execute(agent):
        agent.reward_winner()
        agent.change_state(FightIdle)

    def Exit(agent):
        agent.remove_flags()