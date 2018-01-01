from StateTemplates import *
from ChampionStates import *
from FightStates import *
import random

BASE_CHARACTER_ATTACK = 5
BASE_SLOTS = ['left_hand', 'right_hand', 'helmet', 'legs', 'body', 'head']
SKILLS_LIST = ['dual wielding', 'one hand weapon']

def exp_to_next_level(x):
    return (x + 1) * 100

class adam:
    def update(self):
        self.fsm.update()

    def change_state(self, new_state):
        self.fsm.change_state(new_state)


class Creature(adam):
    def __init__(self, name, hp, dmg, arm):
        self.name = name
        self.hp = hp
        self.maxhp = hp
        self.dmg = dmg
        self.arm = arm
        self.in_duel = False
        self.money = 0
        self.equip = Doll(self)

    def change_hp(self, x):
        self.hp = max(0, self.hp + x)

    def get_dmg(self):
        return self.dmg + self.equip.get_equip_damage()

    def get_arm(self):
        return self.arm + self.equip.get_equip_armour()


class Doll:
    def __init__(self, owner):
        self.items = dict()
        self.owner = owner
        for i in BASE_SLOTS:
            self.items[i] = -1

    def try_equip(self, x):
        if self.free(x.slot):
            self.items[i] = x
            return 1
        return -1

    def free(self, slot):
        if self.items[slot] == -1:
            return True

    def get_tag(self, tag):
        return self.items[tag]

    def set_tag(self, tag, item):
        self.items[tag] = item

    def get_tag_text(self, tag):
        if self.items[tag] == -1:
            return('empty')
        else:
            return(self.items[tag].name)
    
    def get_equip_damage(self):
        curr = 0
        for tag in BASE_SLOTS:
            if self.items[tag] != -1:
                curr += self.items[tag].dmg
        return curr
    
    def get_equip_armour(self):
        curr = 0
        for tag in BASE_SLOTS:
            if self.items[tag] != -1:
                curr += self.items[tag].armour
        return curr


class Inventory():
    def __init__(self):
        self.max_items = 5
        self.items = [-1] * self.max_items
        self.is_full = False

    def add_item(self, x):
        for i in range(self.max_items):
            if self.items[i] == -1:
                self.items[i] = x
                return
        if i == self.max_items - 1 and self.items[self.max_items - 1]:
            self.is_full = True

    def get_ind(self, ind):
        if ind < self.max_items:
            return self.items[ind]
        return -1

    def set_ind(self, ind, item):
        self.items[ind] = item

    def get_ind_name(self, ind):
        if self.items[ind] == -1:
            return -1
        return self.items[ind].name

    def eraze_ind(self, ind):
        self.items[ind] = -1

class Skills():
    def __init__(self):
        self.data = dict()
        for i in SKILLS_LIST:
            self.data[i] = False


class Champion(Creature):
    def __init__(self, world, name, hp):
        Creature.__init__(self, name, hp, BASE_CHARACTER_ATTACK, 0)
        self.world = world
        self.fsm = StateMachine(self, ChampionIdle)
        self.equip = Doll(self)
        self.inventory = Inventory()
        self.skills = Skills()
        self.exp = 0
        self.level = 0
        self.depth = 0
        self.status = 'idle'

    def give(self, item):
        #tmp = self.equip.try_equip(item)
        #if tmp == -1:
        #    self.inventory.add_item(item)
        self.inventory.add_item(item)

    def get_skill(self, s):
        return self.skills.data[s]

    def give_exp(self, amount):
        self.exp += amount
        if self.exp >= exp_to_next_level(self.level):
            self.exp -= exp_to_next_level(self.level)
            self.levelup()

    def levelup(self):
         self.level += 1

    def return_to_town(self):
        self.change_state(ChampionGoHome)

    def go_dungeon(self):
        self.change_state(ChampionGoDungeon)

    def can_wear_slot(self, ind):
        return True

    def equip_slot(self, ind):
        tmp1 = self.inventory.get_ind(ind)       
        if tmp1 == -1:
            return
        tmp2 = self.equip.get_tag(tmp1.slot)
        slot = tmp1.slot
        if tmp2 == -1:
            self.equip.set_tag(slot, tmp1)
            self.inventory.eraze_ind(ind)
            return
        self.inventory.set_ind(ind, tmp2)
        self.equip.set_tag(slot, tmp1)

    def sell_slot(self, ind):
        tmp = self.inventory.get_ind(ind)
        self.inventory.set_ind(ind, -1)
        if tmp != -1:
            self.money += tmp.cost

    def set_name(self, s):
        self.name = s


class Item():
    def __init__(self, name, typ, slot, damage, armour, weight):
        (self.name, self.typ, self.slot, self.damage, self.armour, self.weight) = (name, typ, slot, damage, armour, weight)
        self.cost = (self.damage + self.armour) * 10


class Fight(adam):
    def __init__(self, char1, char2):
        self.fsm = StateMachine(self, FightStarts)
        self.p1 = char1
        self.p2 = char2
        self.arm1 = self.p1.get_arm()
        self.arm2 = self.p2.get_arm()
        self.battle_over = False

    def set_flags(self):
        self.p1.in_duel = True
        self.p2.in_duel = True

    def remove_flags(self):
        self.p1.in_duel = False
        self.p2.in_duel = False  

    def melee_clash(self):
        self.p1.change_hp(min(0, self.arm1 - self.p2.get_dmg()))
        self.p2.change_hp(min(0, self.arm2 - self.p2.get_dmg()))
        if self.arm1 > 0:
            self.arm1 -= 1
        if self.arm2 > 0:
            self.arm2 -= 1
        if self.p1.hp * self.p2.hp == 0:
            self.battle_over = True

    def reward_winner(self):
        if self.p1.hp > 0:
            self.p1.give_exp(self.p1.depth)


class World:
    def __init__(self, item_list, creature_list, dungeon_list):
        self.items = []
        self.creatures = []
        self.dungeon_enemies = [[] for i in range(10)]
        self.dungeon_treasures = [[] for i in range(10)]
        self.duel = -1
        f = open(item_list)
        for x in f.readlines():
            x = x.strip()
            self.add_item(x.split())
        f = open(creature_list)
        for x in f.readlines():
            x = x.strip()
            self.add_creature(x.split())
        f = open(dungeon_list)
        i = 1
        for x in f.readlines():
            x = x.strip()
            self.add_dungeon_info(i, x.split())
            i += 1


    def add_item(self, list1):
        (name, typ, slot, damage, armour, weight) = tuple(list1)
        self.items.append(Item(name, typ, slot, int(damage), int(armour), int(weight)))

    def add_creature(self, l):
        (name, hp, dmg, arm) = tuple(l)
        self.creatures.append(Creature(name, int(hp), int(dmg), int(arm)))

    def add_dungeon_info(self, j, l):
        self.dungeon_enemies[j] = []
        self.dungeon_treasures[j] = []
        n = int(l[0])
        i = 1
        while i <= n:
            self.dungeon_enemies[j].append(int(l[i]))
            i += 1
        m = int(l[i])
        i += 1
        while i <= n + m + 1:
            self.dungeon_treasures[j].append(int(l[i]))
            i += 1

    def get_random_treasure(self, depth):
        x = self.items[random.choice(self.dungeon_treasures[depth])]
        return x

    def get_random_enemy(self, depth):
        x = self.creatures[random.choice(self.dungeon_enemies[depth])]
        return x

    def start_duel(self, chara, mob):
        chara.in_duel = True
        self.duel = Fight(chara, mob)

    def update(self):
        if self.player.in_duel:
             self.duel.update()
        else:
            self.player.update()

    def set_player(self, chara):
        self.player = chara