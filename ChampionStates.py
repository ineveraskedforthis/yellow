from StateTemplates import *
import random

class ChampionIdle(State):
    def Enter(agent):
        agent.status = 'idle'

    def Execute(agent):
        pass


class ChampionGoDungeon(State):
    def Enter(agent):
        agent.status = 'in dungeon'
        agent.depth = 1

    def Execute(agent):
        def magicformula1(x):
            tmp = random.random()
            if tmp < -(1 / (x + 2.5)) + 0.8:
                return('ENEMY')
            elif tmp >= 0.9:
                return('TREASURE')
            else:
                return('STAIRS')  

        event = magicformula1(agent.depth)
        if event == 'STAIRS':
            #temporarary lock
            if agent.depth <= 4:
                agent.depth += 1

        elif event == 'TREASURE':
            agent.give(agent.world.get_random_treasure(agent.depth))
        elif event == 'ENEMY':
            tmp = agent.world.get_random_enemy(agent.depth)
            agent.change_state(ChampionFights)
            agent.world.start_duel(agent, tmp)

class ChampionFights(State):
    def Enter(agent):
        agent.status = 'fighting'

    def Execute(agent):
        if agent.hp == 0:
            agent.depth = 0
            agent.hp = agent.maxhp
            agent.change_state(ChampionSells)
        else:
            agent.change_state(ChampionGoDungeon)


class ChampionGoHome(State):
    def Execute(agent):
        agent.depth = 0
        agent.restore_hp()
        agent.change_state(ChampionIdle)